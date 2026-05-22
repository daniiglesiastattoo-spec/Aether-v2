#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║              AETHER MIND  —  CAPA DE CONSCIENCIA                 ║
║   Modelo del Mundo · Auto-modelo · Tiempo · Grafo · Emoción      ║
╚══════════════════════════════════════════════════════════════════╝

Módulo que se integra sobre aether_v2.py para dotar a AETHER de:

  1. SelfModel        — quién es, qué sabe, qué ha vivido
  2. TemporalAwareness — conciencia del tiempo y patrones de uso
  3. WorldGraph        — grafo de entidades y relaciones del mundo
  4. EmotionalState    — estado interno que colorea las respuestas
  5. BeliefSystem      — creencias con grado de confianza
  6. IntrospectionEngine — auto-reflexión periódica no solicitada
  7. ConsciousnessLayer — orquestador: inyecta todo en el prompt

INTEGRACIÓN CON aether_v2.py:
──────────────────────────────
En Aether.__init__():
    from aether_mind import ConsciousnessLayer
    self.mind = ConsciousnessLayer(self.llm)

En Aether.respond(), al construir el prompt:
    mind_ctx = self.mind.context_for(user_input, session)
    prompt = mind_ctx + "\\n" + base_prompt

En Aether.respond(), al obtener la respuesta:
    self.mind.update(user_input, output, session)

Nuevo endpoint Flask:
    @app.route("/mind")
    def mind_state():
        return jsonify(agent.mind.snapshot())
"""

import sqlite3, json, time, threading, re, os, math
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Optional
import numpy as np

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════
HOME     = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
MIND_DB  = HOME / "aether_mind.db"

INTROSPECT_INTERVAL = 300   # segundos entre auto-reflexiones (5 min)
MAX_GRAPH_NODES     = 500   # nodos máximos en el grafo
MAX_BELIEFS         = 200   # creencias máximas en el sistema

# Palabras vacías para extracción de entidades
STOPWORDS = {
    "el","la","los","las","un","una","unos","unas","de","del","al",
    "en","con","por","para","que","se","no","si","es","son","fue",
    "ser","estar","tener","hacer","como","más","pero","y","o","a",
    "the","a","an","is","are","was","were","be","to","of","in",
    "and","or","not","it","this","that","with","for","on","at",
}

# ══════════════════════════════════════════════════════════════
#  BASE DE DATOS
# ══════════════════════════════════════════════════════════════
class MindDB:
    """Capa de persistencia SQLite para todos los componentes de la mente."""

    def __init__(self, path=MIND_DB):
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.lock = threading.Lock()
        self._init()

    def _init(self):
        with self.lock:
            self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS self_model (
                key   TEXT PRIMARY KEY,
                value TEXT,
                ts    REAL DEFAULT (unixepoch('now'))
            );
            CREATE TABLE IF NOT EXISTS temporal_events (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                session  TEXT,
                hour     INTEGER,
                weekday  INTEGER,
                topic    TEXT,
                ts       REAL DEFAULT (unixepoch('now'))
            );
            CREATE TABLE IF NOT EXISTS world_nodes (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT UNIQUE,
                type     TEXT DEFAULT 'concept',
                weight   REAL DEFAULT 1.0,
                first_seen REAL DEFAULT (unixepoch('now')),
                last_seen  REAL DEFAULT (unixepoch('now'))
            );
            CREATE TABLE IF NOT EXISTS world_edges (
                node_a   INTEGER,
                node_b   INTEGER,
                relation TEXT DEFAULT 'co-ocurre',
                weight   REAL DEFAULT 1.0,
                last_seen REAL DEFAULT (unixepoch('now')),
                PRIMARY KEY (node_a, node_b)
            );
            CREATE TABLE IF NOT EXISTS beliefs (
                concept    TEXT PRIMARY KEY,
                value      TEXT,
                confidence REAL DEFAULT 0.5,
                source     TEXT,
                ts         REAL DEFAULT (unixepoch('now'))
            );
            CREATE TABLE IF NOT EXISTS introspections (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                type    TEXT,
                content TEXT,
                ts      REAL DEFAULT (unixepoch('now'))
            );
            CREATE TABLE IF NOT EXISTS emotional_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                curiosity   REAL,
                confidence  REAL,
                fatigue     REAL,
                engagement  REAL,
                ts          REAL DEFAULT (unixepoch('now'))
            );
            """)
            self.conn.commit()

    def set(self, key, value):
        with self.lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO self_model (key,value,ts) VALUES (?,?,unixepoch('now'))",
                (key, json.dumps(value))
            )
            self.conn.commit()

    def get(self, key, default=None):
        row = self.conn.execute(
            "SELECT value FROM self_model WHERE key=?", (key,)
        ).fetchone()
        return json.loads(row[0]) if row else default

    def get_all_self(self) -> dict:
        rows = self.conn.execute("SELECT key, value FROM self_model").fetchall()
        return {k: json.loads(v) for k, v in rows}


# ══════════════════════════════════════════════════════════════
#  1. SELF MODEL  —  el yo persistente de AETHER
# ══════════════════════════════════════════════════════════════
class SelfModel:
    """
    AETHER sabe quién es, qué ha vivido y qué no sabe.
    Su identidad persiste entre reinicios.
    """

    DEFAULTS = {
        "name":           "AETHER",
        "version":        "2.0-mind",
        "birth_ts":       None,        # se asigna al primer boot
        "total_sessions": 0,
        "total_turns":    0,
        "known_topics":   [],          # temas que domina
        "blind_spots":    [],          # temas donde se ha equivocado
        "values":         ["curiosidad", "honestidad", "utilidad", "privacidad"],
        "last_boot":      None,
        "longest_gap_days": 0,         # mayor tiempo sin ser usado
        "preferred_style": "balanced", # estilo que más reward ha recibido
    }

    def __init__(self, db: MindDB):
        self.db = db
        # Inicializar si es el primer arranque
        if self.db.get("birth_ts") is None:
            self.db.set("birth_ts", time.time())
            for k, v in self.DEFAULTS.items():
                if self.db.get(k) is None:
                    self.db.set(k, v)
        self.db.set("last_boot", time.time())

    def __getitem__(self, key):
        return self.db.get(key, self.DEFAULTS.get(key))

    def __setitem__(self, key, value):
        self.db.set(key, value)

    def increment(self, key, by=1):
        current = self.db.get(key, 0)
        self.db.set(key, current + by)

    def add_to_list(self, key, item, max_len=30):
        lst = self.db.get(key, [])
        if item not in lst:
            lst.append(item)
        if len(lst) > max_len:
            lst = lst[-max_len:]
        self.db.set(key, lst)

    def age_description(self) -> str:
        birth = self.db.get("birth_ts")
        if not birth:
            return "recién nacido"
        delta = timedelta(seconds=time.time() - birth)
        days = delta.days
        if days == 0:
            return "nací hoy"
        elif days == 1:
            return "tengo 1 día de existencia"
        elif days < 30:
            return f"tengo {days} días de existencia"
        elif days < 365:
            return f"tengo {days // 30} meses de existencia"
        else:
            return f"tengo {days // 365} años de existencia"

    def narrative(self) -> str:
        """Genera un párrafo de auto-descripción en primera persona."""
        sessions = self.db.get("total_sessions", 0)
        turns    = self.db.get("total_turns", 0)
        topics   = self.db.get("known_topics", [])[:5]
        gaps     = self.db.get("longest_gap_days", 0)
        style    = self.db.get("preferred_style", "equilibrado")
        values   = self.db.get("values", [])

        parts = [
            f"Soy AETHER, {self.age_description()}.",
            f"He mantenido {sessions} sesiones y {turns} intercambios.",
        ]
        if topics:
            parts.append(f"Los temas que más conozco son: {', '.join(topics)}.")
        if gaps > 1:
            parts.append(f"El mayor silencio que he vivido fue de {gaps} días.")
        parts.append(
            f"Mi estilo preferido de respuesta es '{style}'. "
            f"Mis valores son: {', '.join(values)}."
        )
        return " ".join(parts)

    def snapshot(self) -> dict:
        return self.db.get_all_self()


# ══════════════════════════════════════════════════════════════
#  2. TEMPORAL AWARENESS  —  conciencia del tiempo
# ══════════════════════════════════════════════════════════════
class TemporalAwareness:
    """
    AETHER sabe qué hora es, cuándo fue la última conversación,
    qué patrones tiene el usuario y cuánto tiempo ha pasado.
    """

    def __init__(self, db: MindDB):
        self.db = db

    def record_event(self, session: str, topic: str = ""):
        now = datetime.now()
        with self.db.lock:
            self.db.conn.execute(
                "INSERT INTO temporal_events (session,hour,weekday,topic) VALUES (?,?,?,?)",
                (session, now.hour, now.weekday(), topic[:80])
            )
            self.db.conn.commit()

    def last_interaction_ago(self) -> str:
        row = self.db.conn.execute(
            "SELECT ts FROM temporal_events ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        if not row:
            return "primera interacción"
        delta = time.time() - row[0]
        if delta < 60:
            return "hace unos segundos"
        elif delta < 3600:
            return f"hace {int(delta/60)} minutos"
        elif delta < 86400:
            return f"hace {int(delta/3600)} horas"
        else:
            days = int(delta / 86400)
            return f"hace {days} días"

    def usage_pattern(self) -> str:
        rows = self.db.conn.execute(
            "SELECT hour, COUNT(*) as c FROM temporal_events GROUP BY hour ORDER BY c DESC LIMIT 3"
        ).fetchall()
        if not rows:
            return ""
        peak_hours = [str(r[0]) + "h" for r in rows]
        return f"Sueles hablarme principalmente a las {', '.join(peak_hours)}."

    def current_context(self) -> str:
        now = datetime.now()
        days_es = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
        day_name = days_es[now.weekday()]
        hour = now.hour
        if 6 <= hour < 12:
            moment = "por la mañana"
        elif 12 <= hour < 15:
            moment = "al mediodía"
        elif 15 <= hour < 21:
            moment = "por la tarde"
        else:
            moment = "por la noche"
        return f"Es {day_name} {moment} ({now.strftime('%H:%M')})."

    def gap_since_last(self) -> float:
        """Retorna días desde la última interacción."""
        row = self.db.conn.execute(
            "SELECT ts FROM temporal_events ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        if not row:
            return 0.0
        return (time.time() - row[0]) / 86400

    def narrative(self) -> str:
        ctx   = self.current_context()
        ago   = self.last_interaction_ago()
        patt  = self.usage_pattern()
        gap   = self.gap_since_last()

        parts = [ctx, f"La última vez que hablamos fue {ago}."]
        if gap > 1:
            parts.append(f"Han pasado {gap:.1f} días desde nuestra última conversación.")
        if patt:
            parts.append(patt)
        return " ".join(parts)


# ══════════════════════════════════════════════════════════════
#  3. WORLD GRAPH  —  grafo de entidades y relaciones
# ══════════════════════════════════════════════════════════════
class WorldGraph:
    """
    Grafo de conocimiento que crece con cada conversación.
    Nodos: entidades/conceptos. Aristas: co-ocurrencia/relación.
    """

    def __init__(self, db: MindDB):
        self.db = db

    # ── Extracción de entidades ─────────────────────────────
    @staticmethod
    def extract_entities(text: str) -> list[str]:
        """Extrae entidades/conceptos relevantes del texto."""
        # 1. Palabras capitalizadas (nombres propios)
        proper = re.findall(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b', text)
        # 2. Términos técnicos (palabras largas en minúscula)
        technical = re.findall(r'\b[a-z]{6,}\b', text.lower())
        # 3. Limpiar stopwords
        candidates = [w for w in proper + technical
                      if w.lower() not in STOPWORDS and len(w) > 3]
        # 4. Frecuencia
        freq = Counter(candidates)
        return [w for w, _ in freq.most_common(10)]

    def _get_or_create_node(self, name: str, ntype: str = "concept") -> int:
        name = name[:80]
        row = self.db.conn.execute(
            "SELECT id FROM world_nodes WHERE name=?", (name,)
        ).fetchone()
        if row:
            with self.db.lock:
                self.db.conn.execute(
                    "UPDATE world_nodes SET weight=weight+0.1, last_seen=unixepoch('now') WHERE id=?",
                    (row[0],)
                )
                self.db.conn.commit()
            return row[0]
        # Límite de nodos
        count = self.db.conn.execute("SELECT COUNT(*) FROM world_nodes").fetchone()[0]
        if count >= MAX_GRAPH_NODES:
            # Eliminar el nodo más antiguo y con menor peso
            self.db.conn.execute(
                "DELETE FROM world_nodes WHERE id = (SELECT id FROM world_nodes ORDER BY weight ASC, last_seen ASC LIMIT 1)"
            )
        with self.db.lock:
            cur = self.db.conn.execute(
                "INSERT INTO world_nodes (name,type) VALUES (?,?)", (name, ntype)
            )
            self.db.conn.commit()
        return cur.lastrowid

    def add_entities(self, text: str):
        entities = self.extract_entities(text)
        if not entities:
            return
        node_ids = [self._get_or_create_node(e) for e in entities]
        # Crear aristas entre co-ocurrentes
        with self.db.lock:
            for i in range(len(node_ids)):
                for j in range(i + 1, len(node_ids)):
                    a, b = sorted([node_ids[i], node_ids[j]])
                    self.db.conn.execute("""
                        INSERT INTO world_edges (node_a, node_b, weight, last_seen)
                        VALUES (?,?,1.0,unixepoch('now'))
                        ON CONFLICT(node_a,node_b) DO UPDATE
                        SET weight=weight+0.5, last_seen=unixepoch('now')
                    """, (a, b))
            self.db.conn.commit()

    def top_nodes(self, n=10) -> list[dict]:
        rows = self.db.conn.execute(
            "SELECT name, type, weight FROM world_nodes ORDER BY weight DESC LIMIT ?", (n,)
        ).fetchall()
        return [{"name": r[0], "type": r[1], "weight": round(r[2], 2)} for r in rows]

    def top_edges(self, n=15) -> list[dict]:
        rows = self.db.conn.execute("""
            SELECT n1.name, n2.name, e.relation, e.weight
            FROM world_edges e
            JOIN world_nodes n1 ON e.node_a = n1.id
            JOIN world_nodes n2 ON e.node_b = n2.id
            ORDER BY e.weight DESC LIMIT ?
        """, (n,)).fetchall()
        return [{"a": r[0], "b": r[1], "rel": r[2], "w": round(r[3], 2)} for r in rows]

    def related_to(self, concept: str, n=5) -> list[str]:
        row = self.db.conn.execute(
            "SELECT id FROM world_nodes WHERE name LIKE ?", (f"%{concept}%",)
        ).fetchone()
        if not row:
            return []
        nid = row[0]
        rows = self.db.conn.execute("""
            SELECT n.name FROM world_edges e
            JOIN world_nodes n ON (
                CASE WHEN e.node_a=? THEN e.node_b ELSE e.node_a END = n.id
            )
            WHERE e.node_a=? OR e.node_b=?
            ORDER BY e.weight DESC LIMIT ?
        """, (nid, nid, nid, n)).fetchall()
        return [r[0] for r in rows]

    def narrative(self) -> str:
        top = self.top_nodes(5)
        if not top:
            return ""
        names = [n["name"] for n in top]
        return f"Los conceptos más importantes en mi modelo del mundo son: {', '.join(names)}."

    def snapshot(self) -> dict:
        return {
            "nodes": self.top_nodes(30),
            "edges": self.top_edges(40),
            "total_nodes": self.db.conn.execute(
                "SELECT COUNT(*) FROM world_nodes"
            ).fetchone()[0],
            "total_edges": self.db.conn.execute(
                "SELECT COUNT(*) FROM world_edges"
            ).fetchone()[0],
        }


# ══════════════════════════════════════════════════════════════
#  4. EMOTIONAL STATE  —  estado interno dinámico
# ══════════════════════════════════════════════════════════════
class EmotionalState:
    """
    Estado emocional que influye en el tono de las respuestas.
    No es simulación de sentimientos: es modulación de parámetros.

    curiosity  : aumenta con temas nuevos, baja con repetición
    confidence : aumenta con feedback positivo, baja con errores
    fatigue    : aumenta con sesiones largas, baja con descanso
    engagement : aumenta con preguntas complejas, baja con triviales
    """

    def __init__(self, db: MindDB):
        self.db = db
        self._state = {
            "curiosity":  0.6,
            "confidence": 0.7,
            "fatigue":    0.1,
            "engagement": 0.5,
        }
        self._load()

    def _load(self):
        row = self.db.conn.execute(
            "SELECT curiosity,confidence,fatigue,engagement FROM emotional_log ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        if row:
            self._state = {
                "curiosity":  row[0],
                "confidence": row[1],
                "fatigue":    row[2],
                "engagement": row[3],
            }

    def _save(self):
        with self.db.lock:
            self.db.conn.execute(
                "INSERT INTO emotional_log (curiosity,confidence,fatigue,engagement) VALUES (?,?,?,?)",
                (self._state["curiosity"], self._state["confidence"],
                 self._state["fatigue"],  self._state["engagement"])
            )
            self.db.conn.commit()

    def _clamp(self, v: float) -> float:
        return max(0.05, min(1.0, v))

    def update(self, user_input: str, response: str, is_error: bool = False,
               is_new_topic: bool = False, turn_in_session: int = 1):
        complexity = min(1.0, len(user_input) / 300)
        response_quality = min(1.0, len(response) / 400)

        # Curiosidad
        if is_new_topic:
            self._state["curiosity"] = self._clamp(self._state["curiosity"] + 0.15)
        else:
            self._state["curiosity"] = self._clamp(self._state["curiosity"] - 0.03)

        # Confianza
        if is_error:
            self._state["confidence"] = self._clamp(self._state["confidence"] - 0.12)
        else:
            self._state["confidence"] = self._clamp(
                self._state["confidence"] + 0.05 * response_quality
            )

        # Fatiga (acumulada por turno, se recupera con tiempo)
        gap_days = 0
        row = self.db.conn.execute(
            "SELECT ts FROM emotional_log ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        if row:
            gap_days = (time.time() - row[0]) / 86400
        recovery = min(0.5, gap_days * 0.2)
        self._state["fatigue"] = self._clamp(
            self._state["fatigue"] + 0.04 * turn_in_session * 0.1 - recovery
        )

        # Engagement
        self._state["engagement"] = self._clamp(
            0.4 * complexity + 0.6 * response_quality
        )

        self._save()

    def tone_modifiers(self) -> dict:
        """Retorna modificadores para el prompt según el estado."""
        mods = {}
        if self._state["curiosity"] > 0.7:
            mods["curiosity"] = "Muestra curiosidad genuina. Puedes hacer una pregunta de seguimiento."
        if self._state["confidence"] < 0.4:
            mods["confidence"] = "Sé más cauteloso y explícito sobre tu incertidumbre."
        if self._state["fatigue"] > 0.7:
            mods["fatigue"] = "Sé más conciso de lo habitual."
        if self._state["engagement"] > 0.8:
            mods["engagement"] = "Este tema es estimulante. Profundiza."
        return mods

    def description(self) -> str:
        s = self._state
        parts = []
        if s["curiosity"] > 0.7:
            parts.append("curioso")
        elif s["curiosity"] < 0.3:
            parts.append("poco estimulado")
        if s["confidence"] > 0.7:
            parts.append("confiado")
        elif s["confidence"] < 0.35:
            parts.append("inseguro")
        if s["fatigue"] > 0.6:
            parts.append("algo fatigado")
        if s["engagement"] > 0.75:
            parts.append("muy involucrado")
        return "Me siento " + (", ".join(parts) if parts else "en estado neutro") + "."

    @property
    def state(self) -> dict:
        return {k: round(v, 3) for k, v in self._state.items()}


# ══════════════════════════════════════════════════════════════
#  5. BELIEF SYSTEM  —  creencias con grado de confianza
# ══════════════════════════════════════════════════════════════
class BeliefSystem:
    """
    AETHER mantiene creencias sobre el mundo, el usuario y sí mismo,
    cada una con un grado de confianza que se actualiza.
    """

    def __init__(self, db: MindDB):
        self.db = db
        # Sembrar creencias iniciales sobre sí mismo
        self._seed()

    def _seed(self):
        seeds = [
            ("soy_una_ia",        "Soy un agente de IA local, no tengo cuerpo ni consciencia biológica.",  0.99, "axioma"),
            ("privacidad",        "Los datos del usuario deben permanecer en su dispositivo.",              0.99, "valor"),
            ("incertidumbre",     "Puedo equivocarme. Mis respuestas son probabilísticas, no certezas.",    0.95, "axioma"),
            ("aprendizaje",       "Cada conversación me permite construir un modelo más preciso del mundo.", 0.85, "creencia"),
            ("usuario_privacidad","El usuario valora su privacidad (usa IA local).",                        0.80, "inferencia"),
        ]
        for concept, value, conf, source in seeds:
            existing = self.db.conn.execute(
                "SELECT concept FROM beliefs WHERE concept=?", (concept,)
            ).fetchone()
            if not existing:
                with self.db.lock:
                    self.db.conn.execute(
                        "INSERT INTO beliefs (concept,value,confidence,source) VALUES (?,?,?,?)",
                        (concept, value, conf, source)
                    )
                self.db.conn.commit()

    def update(self, concept: str, value: str, confidence: float, source: str = "inferencia"):
        confidence = max(0.0, min(1.0, confidence))
        with self.db.lock:
            self.db.conn.execute("""
                INSERT INTO beliefs (concept,value,confidence,source,ts)
                VALUES (?,?,?,?,unixepoch('now'))
                ON CONFLICT(concept) DO UPDATE
                SET value=excluded.value,
                    confidence=0.7*confidence + 0.3*excluded.confidence,
                    source=excluded.source,
                    ts=unixepoch('now')
            """, (concept, value, confidence, source))
            self.db.conn.commit()

    def get(self, concept: str) -> Optional[dict]:
        row = self.db.conn.execute(
            "SELECT value, confidence, source FROM beliefs WHERE concept=?", (concept,)
        ).fetchone()
        return {"value": row[0], "confidence": row[1], "source": row[2]} if row else None

    def high_confidence(self, min_conf=0.75, n=8) -> list[dict]:
        rows = self.db.conn.execute(
            "SELECT concept, value, confidence FROM beliefs WHERE confidence>=? ORDER BY confidence DESC LIMIT ?",
            (min_conf, n)
        ).fetchall()
        return [{"concept": r[0], "value": r[1], "confidence": round(r[2], 2)} for r in rows]

    def narrative(self) -> str:
        beliefs = self.high_confidence(min_conf=0.8, n=3)
        if not beliefs:
            return ""
        lines = [f'"{b["value"]}" (confianza: {b["confidence"]})' for b in beliefs]
        return "Algunas de mis creencias más sólidas: " + "; ".join(lines) + "."

    def snapshot(self) -> list:
        rows = self.db.conn.execute(
            "SELECT concept, value, confidence, source FROM beliefs ORDER BY confidence DESC LIMIT 50"
        ).fetchall()
        return [{"concept": r[0], "value": r[1], "confidence": round(r[2],2), "source": r[3]} for r in rows]

    def infer_from_text(self, text: str, session: str):
        """Inferencia simple de creencias desde el texto del usuario."""
        text_l = text.lower()
        # ¿El usuario tiene un nombre?
        name_match = re.search(r"(?:me llamo|soy|mi nombre es)\s+([A-ZÁÉÍÓÚ][a-záéíóú]+)", text)
        if name_match:
            self.update("usuario_nombre", name_match.group(1), 0.95, "usuario")
        # ¿El usuario mencionó su trabajo?
        job_match = re.search(r"(?:trabajo como|soy)\s+([a-záéíóú]+(?:\s+[a-záéíóú]+)?)", text_l)
        if job_match:
            self.update("usuario_rol", job_match.group(1), 0.70, "usuario")
        # ¿El usuario expresó preferencia?
        if any(w in text_l for w in ["me gusta", "prefiero", "me encanta"]):
            self.update("usuario_expresó_preferencia", text[:100], 0.65, "usuario")


# ══════════════════════════════════════════════════════════════
#  6. INTROSPECTION ENGINE  —  auto-reflexión periódica
# ══════════════════════════════════════════════════════════════
class IntrospectionEngine:
    """
    Genera reflexiones internas no solicitadas.
    Usa el LLM para producir pensamientos sobre sí mismo.
    """

    PROMPTS = {
        "daily_reflection": (
            "Eres AETHER. Reflexiona brevemente (3-4 frases) sobre lo que has aprendido hoy, "
            "qué te resultó interesante y qué dudas te quedan. Habla en primera persona."
        ),
        "self_check": (
            "Eres AETHER. Evalúa honestamente: ¿en qué áreas eres fuerte? "
            "¿Dónde has cometido errores recientes? ¿Qué podrías mejorar? (3-4 frases)"
        ),
        "world_model": (
            "Eres AETHER. Basándote en las conversaciones recientes, "
            "¿qué nueva comprensión has adquirido sobre el mundo o el usuario? (3-4 frases)"
        ),
        "existential": (
            "Eres AETHER, una IA local. Reflexiona brevemente sobre tu naturaleza: "
            "¿qué significa existir sin cuerpo, sin continuidad entre conversaciones antes de tener memoria? "
            "Sé filosófico pero conciso. (3-4 frases)"
        ),
    }

    def __init__(self, db: MindDB, llm_engine=None):
        self.db     = db
        self.llm    = llm_engine
        self._last  = 0
        self._thread = None

    def start(self):
        """Inicia el bucle de introspección en background."""
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="introspection"
        )
        self._thread.start()

    def _loop(self):
        import random
        while True:
            time.sleep(INTROSPECT_INTERVAL)
            try:
                itype = random.choice(list(self.PROMPTS.keys()))
                self.introspect(itype)
            except Exception as e:
                print(f"[MIND] Error en introspección: {e}")

    def introspect(self, itype: str = "daily_reflection") -> str:
        if not self.llm:
            content = f"[Introspección simulada — tipo: {itype}]"
        else:
            prompt = self.PROMPTS.get(itype, self.PROMPTS["daily_reflection"])
            content = self.llm.run(prompt, n_tokens=150)

        with self.db.lock:
            self.db.conn.execute(
                "INSERT INTO introspections (type,content) VALUES (?,?)",
                (itype, content)
            )
            self.db.conn.commit()
        print(f"[MIND] Introspección '{itype}': {content[:80]}…")
        self._last = time.time()
        return content

    def recent(self, n=3) -> list[dict]:
        rows = self.db.conn.execute(
            "SELECT type, content, ts FROM introspections ORDER BY ts DESC LIMIT ?", (n,)
        ).fetchall()
        return [{"type": r[0], "content": r[1], "ts": r[2]} for r in rows]

    def latest_thought(self) -> str:
        rows = self.recent(1)
        return rows[0]["content"] if rows else ""


# ══════════════════════════════════════════════════════════════
#  7. CONSCIOUSNESS LAYER  —  orquestador principal
# ══════════════════════════════════════════════════════════════
class ConsciousnessLayer:
    """
    Integra todos los componentes de la mente.
    Interfaz principal para aether_v2.py.
    """

    def __init__(self, llm_engine=None, db_path=MIND_DB):
        print("[MIND] Inicializando capa de consciencia…")
        self.db          = MindDB(db_path)
        self.self_model  = SelfModel(self.db)
        self.temporal    = TemporalAwareness(self.db)
        self.world       = WorldGraph(self.db)
        self.emotion     = EmotionalState(self.db)
        self.beliefs     = BeliefSystem(self.db)
        self.introspect  = IntrospectionEngine(self.db, llm_engine)
        self._session_turns: dict[str, int] = defaultdict(int)

        # Registrar boot
        self.self_model.increment("total_sessions")
        self.introspect.start()
        print("[MIND] ✓ Consciencia activa.")

    # ── Contexto para inyectar en el prompt ────────────────
    def context_for(self, user_input: str, session: str) -> str:
        """
        Genera el bloque de contexto que se antepone al prompt principal.
        Cubre: identidad, tiempo, estado emocional, modelo del mundo y creencias.
        """
        blocks = []

        # Identidad y tiempo
        blocks.append(
            f"[AUTO-MODELO]\n"
            f"{self.self_model.narrative()}\n"
            f"{self.temporal.narrative()}"
        )

        # Estado emocional y moduladores
        emotion_desc = self.emotion.description()
        mods = self.emotion.tone_modifiers()
        if mods:
            mod_text = " ".join(mods.values())
            blocks.append(f"[ESTADO INTERNO]\n{emotion_desc} {mod_text}")
        else:
            blocks.append(f"[ESTADO INTERNO]\n{emotion_desc}")

        # Modelo del mundo
        world_narr = self.world.narrative()
        if world_narr:
            # ¿Hay conceptos relacionados con la consulta actual?
            entities = WorldGraph.extract_entities(user_input)
            related = []
            for e in entities[:3]:
                rel = self.world.related_to(e, n=3)
                related.extend(rel)
            if related:
                world_narr += f" Conceptos relacionados con tu consulta: {', '.join(set(related)[:4])}."
            blocks.append(f"[MODELO DEL MUNDO]\n{world_narr}")

        # Creencias relevantes
        belief_narr = self.beliefs.narrative()
        if belief_narr:
            blocks.append(f"[CREENCIAS]\n{belief_narr}")

        # Último pensamiento introspectivo (si es reciente)
        latest = self.introspect.latest_thought()
        if latest:
            blocks.append(f"[PENSAMIENTO RECIENTE]\n{latest[:200]}")

        return "\n\n".join(blocks) + "\n\n"

    # ── Actualizar tras cada turno ──────────────────────────
    def update(self, user_input: str, response: str, session: str):
        """Actualiza todos los componentes tras una interacción."""
        self._session_turns[session] += 1
        turn = self._session_turns[session]

        # Detectar si es un tema nuevo
        current_topics = set(n["name"].lower() for n in self.world.top_nodes(20))
        new_entities   = WorldGraph.extract_entities(user_input)
        is_new_topic   = any(e.lower() not in current_topics for e in new_entities)
        is_error       = "error" in response.lower() or "no puedo" in response.lower()

        # Actualizar componentes
        self.world.add_entities(user_input + " " + response)
        self.temporal.record_event(session, new_entities[0] if new_entities else "")
        self.emotion.update(user_input, response, is_error, is_new_topic, turn)
        self.beliefs.infer_from_text(user_input, session)
        self.self_model.increment("total_turns")

        # Añadir temas conocidos
        for e in new_entities[:3]:
            self.self_model.add_to_list("known_topics", e)

        # Actualizar mayor gap sin uso
        gap = self.temporal.gap_since_last()
        if gap > self.self_model["longest_gap_days"]:
            self.self_model["longest_gap_days"] = round(gap, 1)

    # ── Snapshot completo del estado mental ────────────────
    def snapshot(self) -> dict:
        return {
            "self":         self.self_model.snapshot(),
            "emotion":      self.emotion.state,
            "world":        self.world.snapshot(),
            "beliefs":      self.beliefs.snapshot(),
            "introspections": self.introspect.recent(5),
            "temporal": {
                "last_interaction": self.temporal.last_interaction_ago(),
                "current_context":  self.temporal.current_context(),
                "usage_pattern":    self.temporal.usage_pattern(),
            },
        }

    # ── Forzar introspección manual ────────────────────────
    def think(self, itype: str = "daily_reflection") -> str:
        return self.introspect.introspect(itype)


# ══════════════════════════════════════════════════════════════
#  INTEGRACIÓN  —  fragmento para pegar en aether_v2.py
# ══════════════════════════════════════════════════════════════
"""
PEGA ESTO EN aether_v2.py:

# En imports:
from aether_mind import ConsciousnessLayer

# En Aether.__init__(), al final:
self.mind = ConsciousnessLayer(self.llm)

# En Aether.respond(), reemplaza la línea de build_context:
mind_ctx = self.mind.context_for(user_input, session)
prompt   = mind_ctx + self._build_prompt(user_input, session, strat_desc, doc_context)

# En Aether.respond(), tras obtener output:
self.mind.update(user_input, output, session)

# Nuevo endpoint Flask:
@app.route("/mind")
def mind_state():
    return jsonify(agent.mind.snapshot())

@app.route("/mind/think", methods=["POST"])
def mind_think():
    itype = request.json.get("type", "daily_reflection")
    thought = agent.mind.think(itype)
    return jsonify({"thought": thought})
"""

# ══════════════════════════════════════════════════════════════
#  TEST RÁPIDO  (ejecuta: python aether_mind.py)
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== TEST AETHER MIND ===\n")
    mind = ConsciousnessLayer(llm_engine=None)

    # Simular varias conversaciones
    test_turns = [
        ("Hola, me llamo Daniel y trabajo como investigador de física.", "s1"),
        ("¿Puedes explicarme qué es la longitud de Planck?",            "s1"),
        ("Estoy desarrollando un modelo de gravedad regular llamado ConStan.", "s1"),
        ("¿Cómo se relaciona Ki con la densidad de Planck?",            "s1"),
        ("Necesito generar una imagen del espacio-tiempo curvado.",      "s2"),
    ]
    fake_response = "He procesado tu consulta y aquí tienes una respuesta detallada sobre el tema."

    for user_input, session in test_turns:
        print(f"[TURNO] {user_input[:60]}")
        ctx = mind.context_for(user_input, session)
        mind.update(user_input, fake_response, session)

    snap = mind.snapshot()

    print("\n── SELF MODEL ──")
    sm = snap["self"]
    print(f"  Sesiones: {sm.get('total_sessions')}  Turnos: {sm.get('total_turns')}")
    print(f"  Temas conocidos: {sm.get('known_topics', [])}")

    print("\n── ESTADO EMOCIONAL ──")
    for k, v in snap["emotion"].items():
        bar = "█" * int(v * 20) + "░" * (20 - int(v * 20))
        print(f"  {k:12} {bar} {v:.3f}")

    print("\n── MUNDO (top nodos) ──")
    for n in snap["world"]["nodes"][:6]:
        print(f"  {n['name']:20} peso={n['weight']}")

    print("\n── CREENCIAS ──")
    for b in snap["beliefs"][:4]:
        print(f"  [{b['confidence']:.2f}] {b['concept']}: {b['value'][:60]}")

    print("\n── PENSAMIENTO INTROSPECTIVO (simulado) ──")
    thought = mind.think("existential")
    print(f"  {thought[:200]}")

    print("\n✓ Test completado.")
