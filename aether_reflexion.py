#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aether_reflexion.py — Auto-mejora por reflexión persistente
============================================================
Nombre honesto: ReflexionEngine. No es experiencia subjetiva;
es un bucle de metacognición funcional con memoria de casos.

Ciclo:
  1. TRIGGER    → programado (reutiliza el scheduler de aether_consciousness.py)
                  o por evento (N mensajes nuevos desde la última reflexión)
  2. MATERIAL   → última ventana de conversación desde aether.db (memoria episódica)
  3. COMPARABLES→ reflexiones previas similares (FTS5 sobre tags + conclusión)
  4. LLM        → una llamada a Groq (comparte presupuesto de rate-limit con el chat)
                  pidiendo JSON estructurado: impactos, comparación, conclusión, tags
  5. PERSISTIR  → tabla `reflexiones` + índice FTS5
  6. INYECTAR   → en el build del system prompt del chat: top-K conclusiones
                  relevantes, acotadas (esto cierra el bucle de retroalimentación)

Integración con lo existente:
  - Usa el mismo aether.db (no crea otra base de datos)
  - Sustituye la introspección genérica de aether_consciousness.py:
    en vez de "reflexiona sobre tu existencia", reflexiona sobre
    conversaciones REALES → conclusiones accionables y recuperables.
  - La recuperación (paso 6) se llama desde donde construyes el system
    prompt en aether_stream.py, igual que ya inyectas MIND y RAG.
"""

import json
import re
import sqlite3
import time
from datetime import datetime, timezone

DB_PATH = "aether.db"          # tu base episódica existente
MAX_CONCLUSIONES_PROMPT = 3    # tope de conclusiones inyectadas al chat
MAX_CHARS_PROMPT = 600         # tope duro de caracteres inyectados
VENTANA_MENSAJES = 12          # mensajes recientes que se reflexionan
MIN_MENSAJES_NUEVOS = 6        # trigger por evento: no reflexionar por 1 mensaje

# ---------------------------------------------------------------------------
# 1) ESQUEMA
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS reflexiones (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT    NOT NULL,             -- ISO 8601 UTC
    ultimo_msg_id   INTEGER,                      -- hasta dónde se reflexionó
    resumen         TEXT    NOT NULL,             -- qué pasó en la conversación
    impacto_usuario TEXT,                         -- efecto estimado en el usuario
    impacto_propio  TEXT,                         -- qué cambia en el sistema
    comparacion     TEXT,                         -- vs. casos previos recuperados
    conclusion      TEXT    NOT NULL,             -- accionable, 1-2 frases
    tags            TEXT,                         -- csv: "codigo,error,tono"
    usos            INTEGER DEFAULT 0,            -- veces inyectada en el prompt
    activa          INTEGER DEFAULT 1             -- 0 = archivada/superada
);

-- Búsqueda de comparables sin embeddings: FTS5 viene compilado
-- en el sqlite3 de Termux y es suficiente a esta escala.
CREATE VIRTUAL TABLE IF NOT EXISTS reflexiones_fts USING fts5(
    conclusion, tags, resumen,
    content='reflexiones', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS reflexiones_ai AFTER INSERT ON reflexiones BEGIN
    INSERT INTO reflexiones_fts(rowid, conclusion, tags, resumen)
    VALUES (new.id, new.conclusion, new.tags, new.resumen);
END;
"""

PROMPT_REFLEXION = """Eres el módulo de reflexión de AETHER. Analiza este fragmento
de conversación reciente entre AETHER y su usuario, y compáralo con conclusiones
de reflexiones anteriores si se aportan.

CONVERSACIÓN RECIENTE:
{conversacion}

CONCLUSIONES PREVIAS COMPARABLES (puede estar vacío):
{comparables}

Responde SOLO con un objeto JSON, sin markdown ni texto extra:
{{
  "resumen": "qué ocurrió, 1-2 frases",
  "impacto_usuario": "efecto probable de las respuestas en el usuario, 1 frase",
  "impacto_propio": "qué debería ajustar el sistema, 1 frase",
  "comparacion": "en qué coincide o difiere de los casos previos, o 'sin precedentes'",
  "conclusion": "regla accionable y concreta para futuras respuestas, 1-2 frases",
  "tags": ["3-5", "palabras", "clave", "en", "minusculas"]
}}"""


class ReflexionEngine:
    def __init__(self, db_path=DB_PATH, llm_call=None):
        """
        llm_call: tu función existente que llama a Groq y devuelve texto.
                  Debe pasar por el MISMO gestor de rate-limit que el chat.
                  Firma esperada: llm_call(prompt: str) -> str
        """
        self.db_path = db_path
        self.llm_call = llm_call
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # -----------------------------------------------------------------
    # 2) MATERIAL: adapta la query al nombre real de tu tabla episódica
    # -----------------------------------------------------------------
    def _mensajes_recientes(self):
        with self._conn() as c:
            rows = c.execute(
                """SELECT id, sender AS rol, text AS contenido, timestampMs FROM messages
                   ORDER BY timestampMs DESC LIMIT ?""",
                (VENTANA_MENSAJES,),
            ).fetchall()
        return list(reversed(rows))

    def _hay_material_nuevo(self, mensajes):
        if not mensajes:
            return False
        with self._conn() as c:
            row = c.execute(
                "SELECT MAX(ultimo_msg_id) AS m FROM reflexiones"
            ).fetchone()
        ultimo_reflexionado = row["m"] or 0
        nuevos = sum(1 for m in mensajes if m["timestampMs"] > ultimo_reflexionado)
        return nuevos >= MIN_MENSAJES_NUEVOS

    # -----------------------------------------------------------------
    # 3) COMPARABLES: FTS5 sobre el texto de la conversación
    # -----------------------------------------------------------------
    def _comparables(self, texto, k=3):
        terminos = re.findall(r"[a-záéíóúñ]{4,}", texto.lower())
        if not terminos:
            return []
        query = " OR ".join(sorted(set(terminos))[:12])
        with self._conn() as c:
            try:
                rows = c.execute(
                    """SELECT r.conclusion FROM reflexiones_fts f
                       JOIN reflexiones r ON r.id = f.rowid
                       WHERE reflexiones_fts MATCH ? AND r.activa = 1
                       ORDER BY rank LIMIT ?""",
                    (query, k),
                ).fetchall()
            except sqlite3.OperationalError:
                return []
        return [r["conclusion"] for r in rows]

    # -----------------------------------------------------------------
    # 4+5) REFLEXIONAR Y PERSISTIR
    # -----------------------------------------------------------------
    def reflexionar(self):
        """Punto de entrada: llamar desde el scheduler de consciousness."""
        mensajes = self._mensajes_recientes()
        if not self._hay_material_nuevo(mensajes):
            return None  # nada nuevo: no gastar cuota de Groq

        convo = "\n".join(f"[{m['rol']}] {m['contenido'][:400]}" for m in mensajes)
        comparables = self._comparables(convo)
        prompt = PROMPT_REFLEXION.format(
            conversacion=convo,
            comparables="\n".join(f"- {c}" for c in comparables) or "(ninguna)",
        )

        crudo = self.llm_call(prompt)
        datos = self._parsear_json(crudo)
        if not datos:
            return None

        with self._conn() as c:
            c.execute(
                """INSERT INTO reflexiones
                   (ts, ultimo_msg_id, resumen, impacto_usuario,
                    impacto_propio, comparacion, conclusion, tags)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    mensajes[-1]["timestampMs"],
                    datos.get("resumen", ""),
                    datos.get("impacto_usuario", ""),
                    datos.get("impacto_propio", ""),
                    datos.get("comparacion", ""),
                    datos["conclusion"],
                    ",".join(datos.get("tags", [])),
                ),
            )
        return datos["conclusion"]

    @staticmethod
    def _parsear_json(texto):
        m = re.search(r"\{.*\}", texto, re.DOTALL)
        if not m:
            return None
        try:
            datos = json.loads(m.group(0))
            return datos if datos.get("conclusion") else None
        except json.JSONDecodeError:
            return None

    # -----------------------------------------------------------------
    # 6) INYECCIÓN EN EL CHAT: llamar al construir el system prompt
    # -----------------------------------------------------------------
    def conclusiones_para_prompt(self, mensaje_usuario):
        relevantes = self._comparables(mensaje_usuario, k=MAX_CONCLUSIONES_PROMPT)
        if not relevantes:
            with self._conn() as c:
                rows = c.execute(
                    """SELECT conclusion FROM reflexiones WHERE activa = 1
                       ORDER BY id DESC LIMIT ?""",
                    (MAX_CONCLUSIONES_PROMPT,),
                ).fetchall()
            relevantes = [r["conclusion"] for r in rows]
        bloque = "\n".join(f"- {c}" for c in relevantes)[:MAX_CHARS_PROMPT]
        if not bloque:
            return ""
        return f"\n[APRENDIZAJES DE REFLEXIONES PREVIAS]\n{bloque}\n"


if __name__ == "__main__":
    # Prueba en seco sin Groq: verifica esquema y recuperación
    eng = ReflexionEngine(llm_call=lambda p: "{}")
    print("Esquema OK. Conclusiones actuales:")
    print(eng.conclusiones_para_prompt("prueba") or "(base vacía)")
