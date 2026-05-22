#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║           AETHER v2.0  —  LOCAL AI AGENT  (TERMUX)          ║
║   Texto · Visión · Generación de Imágenes · Memoria SQL      ║
╚══════════════════════════════════════════════════════════════╝

MODELOS RECOMENDADOS — elige según tu RAM disponible:
┌─────────────────────────────────────────────────────────────┐
│ 6 GB RAM  (Redmi 13 base)                                   │
│  • LLM+Vision : LLaVA-Phi-3-mini-4k-instruct-Q4_K_M.gguf  │
│                 mmproj-llava-phi-3-mini-f16.gguf            │
│  • ImgGen     : sd-turbo-q8_0.gguf  (512×512, 4 steps)     │
│                                                             │
│ 8 GB RAM  (Redmi 13 8GB / gama media)                       │
│  • LLM+Vision : llava-1.5-7b-hf-Q4_K_M.gguf               │
│                 mmproj-model-f16.gguf                       │
│  • ImgGen     : sd-turbo-q8_0.gguf                         │
└─────────────────────────────────────────────────────────────┘

INSTALACIÓN TERMUX (copia y pega bloque a bloque):
──────────────────────────────────────────────────
# 1. Paquetes del sistema
pkg update && pkg install -y python python-pip cmake git clang \
    libopenblas libjpeg-turbo libpng zlib curl

# 2. Dependencias Python
pip install flask sentence-transformers numpy psutil pillow \
    pypdf2 requests sse-flask

# 3. Compilar llama.cpp (con soporte LLaVA multimodal)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DLLAMA_CURL=OFF -DLLAVA_BUILD=ON
cmake --build build -j4
cp build/bin/llama-cli ~/bin/
cp build/bin/llama-server ~/bin/
cd ..

# 4. Compilar stable-diffusion.cpp (generación de imágenes)
git clone --recursive https://github.com/leejet/stable-diffusion.cpp
cd stable-diffusion.cpp
cmake -B build
cmake --build build -j4
cp build/bin/sd ~/bin/
cd ..

# 5. Descargar modelos (ajusta según tu RAM):
#    LLaVA 3.8B (6 GB):
#    huggingface-cli download xtuner/llava-phi-3-mini-gguf \
#        llava-phi-3-mini-q4_k_m.gguf --local-dir ~/models/
#    huggingface-cli download xtuner/llava-phi-3-mini-gguf \
#        llava-phi-3-mini-mmproj-f16.gguf --local-dir ~/models/
#
#    LLaVA 7B (8 GB):
#    huggingface-cli download mys/ggml_llava-v1.5-7b \
#        ggml-model-q4_k.gguf mmproj-model-f16.gguf --local-dir ~/models/
#
#    SD-Turbo para imagen:
#    huggingface-cli download MnDiaz/sd-turbo-gguf \
#        sd-turbo-q8_0.gguf --local-dir ~/models/

# 6. Ejecutar Aether
python aether_v2.py
# Abre en tu navegador móvil: http://localhost:5000
"""

import subprocess, json, random, time, tempfile, re, os
import psutil, threading, sqlite3, base64, hashlib, uuid
from pathlib import Path
from datetime import datetime
from collections import deque
from flask import Flask, request, jsonify, Response, stream_with_context
from sentence_transformers import SentenceTransformer
import numpy as np
from PIL import Image
import io

# ══════════════════════════════════════════════════════════════
#  CONFIG  —  ajusta rutas a tu entorno
# ══════════════════════════════════════════════════════════════
HOME      = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
MODELS    = HOME / "models"

# ─── Modelo principal (LLM + Visión) ───────────────────────
LLM_MODEL   = MODELS / "llava-phi-3-mini-q4_k_m.gguf"   # cambia si usas 7B
MMPROJ      = MODELS / "llava-phi-3-mini-mmproj-f16.gguf"
LLAMA_CLI   = HOME  / "bin" / "llama-cli"

# ─── Modelo generación de imágenes ─────────────────────────
SD_MODEL    = MODELS / "sd-turbo-q8_0.gguf"
SD_CLI      = HOME  / "bin" / "sd"
SD_OUTPUT   = HOME  / "aether_images"

# ─── Parámetros de rendimiento (ajusta según RAM libre) ────
THREADS     = 4          # núcleos para inferencia (4 recomendado en Redmi 13)
CTX_SIZE    = 2048       # ventana de contexto (sube a 4096 si tienes ≥8 GB)
MAX_TOKENS  = 512        # tokens de respuesta máximos
TEMP        = 0.7        # temperatura del modelo
SD_STEPS    = 4          # pasos SD-Turbo (rápido; sube a 8 para más calidad)
SD_WIDTH    = 512
SD_HEIGHT   = 512

# ─── Misc ───────────────────────────────────────────────────
DB_PATH     = HOME / "aether_memory.db"
EMBED_MODEL = "all-MiniLM-L6-v2"   # ~23 MB, eficiente en CPU
MAX_MEM_SEG = 200                   # segmentos máx en memoria semántica

SD_OUTPUT.mkdir(parents=True, exist_ok=True)

# ══════════════════════════════════════════════════════════════
#  EMBEDDING MODEL  (compartido globalmente)
# ══════════════════════════════════════════════════════════════
print("[BOOT] Cargando modelo de embeddings…")
embed_model = SentenceTransformer(EMBED_MODEL)
print("[BOOT] Embeddings listos.")

# ══════════════════════════════════════════════════════════════
#  MEMORIA PERSISTENTE  (SQLite + búsqueda semántica)
# ══════════════════════════════════════════════════════════════
class Memory:
    """Memoria episódica persistente con recuperación semántica."""

    def __init__(self, db_path=DB_PATH):
        self.db = sqlite3.connect(str(db_path), check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()
        # Cache en RAM para búsqueda rápida
        self._cache_texts: deque = deque(maxlen=MAX_MEM_SEG)
        self._cache_embs:  deque = deque(maxlen=MAX_MEM_SEG)
        self._load_recent_cache()

    def _init_db(self):
        with self.lock:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    session   TEXT,
                    role      TEXT,
                    content   TEXT,
                    embedding BLOB,
                    ts        REAL DEFAULT (unixepoch('now'))
                )""")
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id    TEXT PRIMARY KEY,
                    title TEXT,
                    ts    REAL DEFAULT (unixepoch('now'))
                )""")
            self.db.commit()

    def _load_recent_cache(self):
        rows = self.db.execute(
            "SELECT content, embedding FROM memory ORDER BY id DESC LIMIT ?",
            (MAX_MEM_SEG,)
        ).fetchall()
        for text, emb_blob in reversed(rows):
            emb = np.frombuffer(emb_blob, dtype=np.float32) if emb_blob else None
            if emb is not None:
                self._cache_texts.append(text)
                self._cache_embs.append(emb)

    def add(self, session: str, role: str, content: str):
        emb = embed_model.encode([content])[0].astype(np.float32)
        with self.lock:
            self.db.execute(
                "INSERT INTO memory (session,role,content,embedding) VALUES (?,?,?,?)",
                (session, role, content, emb.tobytes())
            )
            self.db.commit()
        self._cache_texts.append(content)
        self._cache_embs.append(emb)

    @staticmethod
    def _cosine(a, b):
        d = np.linalg.norm(a) * np.linalg.norm(b)
        return float(np.dot(a, b) / d) if d > 0 else 0.0

    def get_relevant(self, query: str, k=6) -> str:
        if not self._cache_texts:
            return ""
        qe = embed_model.encode([query])[0]
        scored = [
            (self._cosine(qe, e), t)
            for e, t in zip(self._cache_embs, self._cache_texts)
        ]
        scored.sort(reverse=True)
        return "\n".join(t for _, t in scored[:k])

    def get_session_history(self, session: str, limit=20) -> list:
        rows = self.db.execute(
            "SELECT role, content FROM memory WHERE session=? ORDER BY id DESC LIMIT ?",
            (session, limit)
        ).fetchall()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    def list_sessions(self) -> list:
        rows = self.db.execute(
            "SELECT id, title, ts FROM sessions ORDER BY ts DESC LIMIT 30"
        ).fetchall()
        return [{"id": i, "title": t, "ts": ts} for i, t, ts in rows]

    def create_session(self, title="Nueva sesión") -> str:
        sid = str(uuid.uuid4())[:8]
        with self.lock:
            self.db.execute(
                "INSERT INTO sessions (id,title) VALUES (?,?)", (sid, title)
            )
            self.db.commit()
        return sid

    def coherence_score(self) -> float:
        if len(self._cache_texts) < 4:
            return 1.0
        words = " ".join(list(self._cache_texts)[-20:]).lower().split()
        if not words:
            return 1.0
        unique = len(set(words))
        rep = (len(words) - unique) / (len(words) + 1)
        return round(max(0.1, 1.0 - rep), 3)

# ══════════════════════════════════════════════════════════════
#  MOTOR DE INFERENCIA LLM + VISIÓN  (llama.cpp)
# ══════════════════════════════════════════════════════════════
class LLMEngine:
    """Interfaz con llama-cli; soporta texto y visión (LLaVA)."""

    BASE_FLAGS = [
        "--threads",   str(THREADS),
        "--ctx-size",  str(CTX_SIZE),
        "--temp",      str(TEMP),
        "--repeat-penalty", "1.1",
        "--no-display-prompt",
        "--log-disable",
    ]

    def __init__(self):
        if not LLAMA_CLI.exists():
            raise FileNotFoundError(
                f"llama-cli no encontrado en {LLAMA_CLI}\n"
                "Compila llama.cpp y copia el binario a ~/bin/"
            )
        if not LLM_MODEL.exists():
            raise FileNotFoundError(
                f"Modelo no encontrado: {LLM_MODEL}\n"
                "Descarga el modelo GGUF y colócalo en ~/models/"
            )
        self.has_vision = MMPROJ.exists()
        print(f"[LLM] Modelo: {LLM_MODEL.name}")
        print(f"[LLM] Visión: {'✓ LLaVA activo' if self.has_vision else '✗ sin mmproj'}")

    def _build_cmd(self, prompt: str, image_path: str | None = None, n_tokens=MAX_TOKENS):
        cmd = [str(LLAMA_CLI), "-m", str(LLM_MODEL)]
        cmd += self.BASE_FLAGS
        cmd += ["-n", str(n_tokens)]
        if image_path and self.has_vision:
            cmd += ["--mmproj", str(MMPROJ), "--image", image_path]
        cmd += ["-p", prompt]
        return cmd

    def run(self, prompt: str, image_path: str | None = None, n_tokens=MAX_TOKENS) -> str:
        """Inferencia bloqueante, retorna texto completo."""
        try:
            cmd = self._build_cmd(prompt, image_path, n_tokens)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=180
            )
            out = result.stdout.strip()
            # Eliminar prompt reflejado (llama-cli lo incluye a veces)
            if prompt[:30] in out:
                out = out[out.find(prompt[:30]) + len(prompt):]
            return out.strip() or "[Sin respuesta del modelo]"
        except subprocess.TimeoutExpired:
            return "[TIMEOUT] El modelo tardó demasiado. Reduce MAX_TOKENS o CTX_SIZE."
        except Exception as e:
            return f"[ERROR LLM] {e}"

    def stream(self, prompt: str, image_path: str | None = None, n_tokens=MAX_TOKENS):
        """Generador que yielda tokens conforme llegan."""
        try:
            cmd = self._build_cmd(prompt, image_path, n_tokens)
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, bufsize=1
            )
            # Saltar el reflejo del prompt
            skip_chars = len(prompt)
            total_read = 0
            for chunk in iter(lambda: proc.stdout.read(4), ""):
                if not chunk:
                    break
                total_read += len(chunk)
                if total_read <= skip_chars:
                    continue
                yield chunk
            proc.wait()
        except Exception as e:
            yield f"[ERROR STREAM] {e}"

# ══════════════════════════════════════════════════════════════
#  GENERADOR DE IMÁGENES  (stable-diffusion.cpp)
# ══════════════════════════════════════════════════════════════
class ImageGenerator:
    """Generación de imágenes local mediante stable-diffusion.cpp."""

    def __init__(self):
        self.available = SD_CLI.exists() and SD_MODEL.exists()
        if self.available:
            print(f"[SD] Modelo: {SD_MODEL.name} ✓")
        else:
            print("[SD] stable-diffusion.cpp o modelo no encontrado — generación deshabilitada.")
            if not SD_CLI.exists():
                print(f"    → Falta binario: {SD_CLI}")
            if not SD_MODEL.exists():
                print(f"    → Falta modelo:  {SD_MODEL}")

    def generate(self, prompt: str, negative="", seed=-1) -> dict:
        """
        Genera imagen. Retorna dict con path, base64 y metadatos.
        Llama al LLM primero para mejorar el prompt automáticamente.
        """
        if not self.available:
            return {"error": "Generador no disponible. Instala stable-diffusion.cpp y el modelo SD."}

        img_id   = hashlib.md5(f"{prompt}{time.time()}".encode()).hexdigest()[:8]
        out_path = SD_OUTPUT / f"{img_id}.png"

        cmd = [
            str(SD_CLI),
            "-m", str(SD_MODEL),
            "-p", prompt,
            "--steps",   str(SD_STEPS),
            "-W",        str(SD_WIDTH),
            "-H",        str(SD_HEIGHT),
            "--seed",    str(seed),
            "-o",        str(out_path),
        ]
        if negative:
            cmd += ["-n", negative]

        try:
            t0 = time.time()
            subprocess.run(cmd, capture_output=True, timeout=300, check=True)
            elapsed = round(time.time() - t0, 1)

            # Convertir a base64 para envío al cliente
            with open(out_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()

            return {
                "path":    str(out_path),
                "base64":  b64,
                "prompt":  prompt,
                "elapsed": elapsed,
                "width":   SD_WIDTH,
                "height":  SD_HEIGHT,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout generando imagen (>5 min)."}
        except subprocess.CalledProcessError as e:
            return {"error": f"Error SD: {e.stderr[:200] if e.stderr else 'desconocido'}"}
        except Exception as e:
            return {"error": str(e)}

# ══════════════════════════════════════════════════════════════
#  LECTOR DE DOCUMENTOS  (imágenes, PDF, texto)
# ══════════════════════════════════════════════════════════════
class DocumentReader:
    """Extrae texto/descripción de archivos subidos."""

    SUPPORTED_IMG = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
    SUPPORTED_DOC = {".pdf", ".txt", ".md", ".py", ".json", ".csv"}

    @staticmethod
    def read_image_file(path: str) -> tuple[str | None, str]:
        """
        Retorna (ruta_optimizada, tipo).
        Redimensiona si la imagen es mayor de 1024px para ahorrar memoria.
        """
        try:
            with Image.open(path) as img:
                # Convertir a RGB si es necesario
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                # Redimensionar si es muy grande
                max_dim = 1024
                if max(img.size) > max_dim:
                    ratio = max_dim / max(img.size)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.LANCZOS)
                # Guardar versión optimizada
                tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                img.save(tmp.name, "JPEG", quality=85)
                return tmp.name, "image"
        except Exception as e:
            return None, f"error:{e}"

    @staticmethod
    def read_pdf(path: str) -> str:
        try:
            import pypdf2
            reader = pypdf2.PdfReader(path)
            pages  = [p.extract_text() for p in reader.pages[:20]]  # máx 20 pág
            return "\n".join(p for p in pages if p).strip()[:8000]
        except ImportError:
            return "[PyPDF2 no instalado: pip install pypdf2]"
        except Exception as e:
            return f"[Error leyendo PDF: {e}]"

    @staticmethod
    def read_text(path: str) -> str:
        try:
            return Path(path).read_text(errors="replace")[:8000]
        except Exception as e:
            return f"[Error leyendo archivo: {e}]"

    def process(self, path: str, original_name="") -> dict:
        ext = Path(original_name or path).suffix.lower()
        if ext in self.SUPPORTED_IMG:
            img_path, kind = self.read_image_file(path)
            return {"type": kind, "path": img_path}
        elif ext == ".pdf":
            return {"type": "text", "content": self.read_pdf(path)}
        elif ext in self.SUPPORTED_DOC:
            return {"type": "text", "content": self.read_text(path)}
        else:
            return {"type": "unknown", "content": f"Formato '{ext}' no soportado."}

# ══════════════════════════════════════════════════════════════
#  MOTOR EVOLUTIVO DE ESTRATEGIAS
# ══════════════════════════════════════════════════════════════
STRATEGIES = {
    "Concise":     "Responde de forma breve y directa.",
    "StepByStep":  "Razona paso a paso antes de responder.",
    "Expert":      "Responde como experto técnico con detalle.",
    "Teacher":     "Explica como si el usuario fuera principiante.",
    "Creative":    "Sé creativo, usa analogías y ejemplos originales.",
    "Critical":    "Analiza críticamente, menciona ventajas e inconvenientes.",
}

class EvoEngine:
    def __init__(self):
        self.scores = {s: 1.0 for s in STRATEGIES}

    def pick(self) -> tuple[str, str]:
        total = sum(self.scores.values())
        r = random.uniform(0, total)
        upto = 0.0
        for s, w in self.scores.items():
            upto += w
            if upto >= r:
                return s, STRATEGIES[s]
        return list(STRATEGIES.items())[0]

    def update(self, strategy: str, reward: float):
        self.scores[strategy] = max(0.1, self.scores[strategy] + reward)

    def evaluate(self, response: str) -> float:
        score = 0.1
        if len(response) > 60:   score += 0.3
        if len(response) > 200:  score += 0.2
        if "error" in response.lower(): score -= 0.4
        if "?" not in response and len(response) > 30: score += 0.1
        return score

# ══════════════════════════════════════════════════════════════
#  GESTOR DE RECURSOS  (CPU/RAM adaptativo)
# ══════════════════════════════════════════════════════════════
class ResourceManager:
    def __init__(self):
        self._lock = threading.Lock()

    def stats(self) -> dict:
        vm   = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "cpu":      round(psutil.cpu_percent(interval=0.3), 1),
            "ram_used": round(vm.percent, 1),
            "ram_avail_mb": round(vm.available / 1e6),
            "swap_used": round(swap.percent, 1),
        }

    def regulate(self):
        """Rebajar prioridad de procesos pesados si CPU > 80%."""
        s = self.stats()
        if s["cpu"] > 80:
            for proc in psutil.process_iter(["pid", "cpu_percent", "nice"]):
                try:
                    if proc.info["cpu_percent"] > 25:
                        os.nice(5)          # rebajar prioridad del proceso actual
                except Exception:
                    pass
        return s

    def can_run_sd(self) -> bool:
        """Comprueba si hay RAM suficiente para generar imagen."""
        return self.stats()["ram_avail_mb"] > 1800  # necesita ~1.8 GB libres

# ══════════════════════════════════════════════════════════════
#  CODE EVOLVER  (automodificación supervisada)
# ══════════════════════════════════════════════════════════════
class CodeEvolver:
    MARKER_START = "[[EVOLVE_START]]"
    MARKER_END   = "[[EVOLVE_END]]"

    def __init__(self, target="aether_v2.py"):
        self.target = target

    def extract(self, text: str) -> str | None:
        m = re.search(
            r"\[\[EVOLVE_START\]\](.*?)\[\[EVOLVE_END\]\]", text, re.DOTALL
        )
        return m.group(1).strip() if m else None

    def sandbox_test(self, code: str) -> bool:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
                f.write(code)
                path = f.name
            r = subprocess.run(
                ["python", path], capture_output=True, timeout=5, text=True
            )
            return r.returncode == 0
        except Exception:
            return False
        finally:
            try: os.unlink(path)
            except: pass

    def apply(self, new_code: str) -> bool:
        if self.sandbox_test(new_code):
            backup = self.target + ".bak"
            if os.path.exists(self.target):
                import shutil
                shutil.copy2(self.target, backup)
            with open(self.target, "w") as f:
                f.write(new_code)
            print("[EVOLVE] ✓ Actualización aplicada")
            return True
        print("[EVOLVE] ✗ Código rechazado (falló sandbox)")
        return False

# ══════════════════════════════════════════════════════════════
#  AETHER  —  AGENTE PRINCIPAL
# ══════════════════════════════════════════════════════════════
class Aether:
    def __init__(self):
        print("[BOOT] Iniciando Aether v2.0…")
        self.memory   = Memory()
        self.llm      = LLMEngine()
        self.imggen   = ImageGenerator()
        self.docread  = DocumentReader()
        self.evo      = EvoEngine()
        self.res      = ResourceManager()
        self.evolver  = CodeEvolver()
        self._start_bg_scanner()
        print("[BOOT] ✓ Aether listo.")

    # ── Prompt builder ──────────────────────────────────────
    def _build_prompt(
        self,
        user_input: str,
        session: str,
        strategy_desc: str,
        doc_context: str = "",
    ) -> str:
        history = self.memory.get_session_history(session, limit=12)
        hist_text = "\n".join(
            f"{'Usuario' if h['role']=='user' else 'Aether'}: {h['content']}"
            for h in history[-6:]
        )
        relevant = self.memory.get_relevant(user_input, k=4)

        parts = [
            "Eres AETHER, un asistente de IA avanzado ejecutándose completamente en local.",
            f"Estilo de respuesta: {strategy_desc}",
        ]
        if hist_text:
            parts.append(f"\n[Historial reciente]\n{hist_text}")
        if relevant:
            parts.append(f"\n[Contexto relevante de memoria]\n{relevant}")
        if doc_context:
            parts.append(f"\n[Documento adjunto]\n{doc_context[:3000]}")
        parts.append(f"\nUsuario: {user_input}\nAether:")
        return "\n".join(parts)

    # ── Detectores de intención ─────────────────────────────
    @staticmethod
    def _wants_image_gen(text: str) -> bool:
        kws = ["genera", "crea una imagen", "dibuja", "pinta", "ilustra",
               "generate image", "draw", "create image", "make a picture"]
        return any(k in text.lower() for k in kws)

    @staticmethod
    def _extract_image_prompt(text: str, llm_fallback=None) -> str:
        """Extrae el sujeto de la petición de imagen."""
        patterns = [
            r"(?:genera|crea|dibuja|pinta|ilustra)\s+(?:una?\s+)?imagen\s+(?:de\s+)?(.+)",
            r"(?:generate|draw|create|make)\s+(?:a\s+)?(?:image|picture|photo)\s+(?:of\s+)?(.+)",
        ]
        for p in patterns:
            m = re.search(p, text, re.I)
            if m:
                return m.group(1).strip().rstrip(".!?")
        return text  # usa el texto completo como prompt

    # ── Respuesta principal ─────────────────────────────────
    def respond(
        self,
        user_input: str,
        session: str,
        image_path: str | None = None,
        doc_context: str = "",
    ) -> dict:
        strategy, strat_desc = self.evo.pick()
        stats = self.res.regulate()

        # ── Modo generación de imagen ───────────────────────
        if self._wants_image_gen(user_input) and not image_path:
            if not self.res.can_run_sd():
                return {
                    "output": "⚠️ RAM insuficiente para generar imagen ahora mismo. "
                              f"Disponible: {stats['ram_avail_mb']} MB. "
                              "Cierra otras apps e inténtalo de nuevo.",
                    **stats, "strategy": strategy, "type": "text",
                }
            img_prompt = self._extract_image_prompt(user_input)
            # Enriquecer el prompt con el LLM antes de generar
            enrich_prompt = (
                f"Mejora este prompt para Stable Diffusion en inglés, "
                f"añade estilo artístico, iluminación y detalles. "
                f"Solo devuelve el prompt mejorado, sin explicaciones:\n{img_prompt}"
            )
            rich_prompt = self.llm.run(enrich_prompt, n_tokens=80)
            rich_prompt = rich_prompt.strip().split("\n")[0]  # primera línea

            result = self.imggen.generate(rich_prompt)
            if "error" in result:
                output = f"❌ Error generando imagen: {result['error']}"
                resp_type = "text"
            else:
                output = (
                    f"✅ Imagen generada en {result['elapsed']}s\n"
                    f"Prompt usado: {rich_prompt}"
                )
                resp_type = "image"
            self.memory.add(session, "user", user_input)
            self.memory.add(session, "assistant", output)
            return {
                "output": output,
                "image": result.get("base64"),
                "type": resp_type,
                **stats, "strategy": strategy,
                "coherence": self.memory.coherence_score(),
            }

        # ── Modo visión (imagen adjunta) ────────────────────
        vision_prefix = ""
        if image_path:
            if not self.llm.has_vision:
                vision_prefix = "[Nota: modelo sin soporte de visión; se analizará solo el texto]\n"
                image_path = None
            else:
                vision_prefix = "[Analizando imagen adjunta…]\n"

        # ── Modo texto / visión ─────────────────────────────
        prompt = self._build_prompt(user_input, session, strat_desc, doc_context)
        if vision_prefix:
            prompt = vision_prefix + prompt

        output = self.llm.run(prompt, image_path=image_path)

        # Evaluar y actualizar estrategia
        reward = self.evo.evaluate(output)
        self.evo.update(strategy, reward)

        # Autoevolución
        candidate = self.evolver.extract(output)
        if candidate:
            threading.Thread(
                target=self.evolver.apply, args=(candidate,), daemon=True
            ).start()

        # Guardar en memoria
        self.memory.add(session, "user", user_input)
        self.memory.add(session, "assistant", output)

        return {
            "output":    output,
            "type":      "text",
            **stats,
            "strategy":  strategy,
            "coherence": self.memory.coherence_score(),
        }

    def stream_respond(self, user_input: str, session: str, image_path=None, doc_context=""):
        """Versión streaming: yielda Server-Sent Events."""
        strategy, strat_desc = self.evo.pick()
        prompt = self._build_prompt(user_input, session, strat_desc, doc_context)
        full_output = []
        for chunk in self.llm.stream(prompt, image_path=image_path):
            full_output.append(chunk)
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        complete = "".join(full_output)
        self.memory.add(session, "user", user_input)
        self.memory.add(session, "assistant", complete)
        self.evo.update(strategy, self.evo.evaluate(complete))
        stats = self.res.stats()
        yield f"data: {json.dumps({'done': True, 'strategy': strategy, **stats})}\n\n"

    # ── Scanner de coherencia en background ─────────────────
    def _start_bg_scanner(self):
        def _scan():
            while True:
                time.sleep(120)
                c = self.memory.coherence_score()
                s = self.res.stats()
                print(f"[SCAN] Coherencia={c:.2f}  CPU={s['cpu']}%  RAM={s['ram_used']}%")
        threading.Thread(target=_scan, daemon=True).start()

# ══════════════════════════════════════════════════════════════
#  HTML UI  (interfaz web mobile-first)
# ══════════════════════════════════════════════════════════════
UI_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>AETHER v2</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@300;400&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0b0f;--bg2:#111318;--bg3:#1a1c24;
  --ac:#7fffbf;--ac2:#4fd9ff;--ac3:#ff7eb6;
  --tx:#c8d8f0;--tx2:#5a6a80;
  --rad:12px;--font:'JetBrains Mono',monospace;
}
body{background:var(--bg);color:var(--tx);font-family:var(--font);
  min-height:100vh;display:flex;flex-direction:column;font-size:13px}
header{padding:12px 16px;background:var(--bg2);border-bottom:1px solid #1e2535;
  display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10}
.logo{font-family:'Syne',sans-serif;font-weight:800;font-size:18px;
  background:linear-gradient(90deg,var(--ac),var(--ac2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stats{display:flex;gap:8px;font-size:10px;color:var(--tx2)}
.stat{background:var(--bg3);padding:3px 7px;border-radius:6px;border:1px solid #1e2535}
.stat span{color:var(--ac);font-weight:700}
#chat{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:10px}
.msg{max-width:92%;padding:10px 13px;border-radius:var(--rad);line-height:1.55;font-size:12.5px;animation:fadein .25s ease}
.msg.user{align-self:flex-end;background:linear-gradient(135deg,#1a2540,#1e2e50);
  border:1px solid #2a3d60;border-bottom-right-radius:3px}
.msg.ai{align-self:flex-start;background:var(--bg3);
  border:1px solid #1e2535;border-bottom-left-radius:3px}
.msg.ai .tag{font-size:9px;color:var(--tx2);margin-bottom:5px;display:flex;gap:6px}
.msg.ai .tag .st{color:var(--ac);font-weight:700}
.msg img{max-width:100%;border-radius:8px;margin-top:8px;border:1px solid #1e2535}
.msg pre{background:#0d0f14;padding:8px;border-radius:6px;overflow-x:auto;
  font-size:11px;margin-top:6px;border:1px solid #1e2535}
.msg code{color:var(--ac2);font-size:11.5px}
.typing{display:flex;gap:5px;padding:5px 0}
.typing span{width:6px;height:6px;background:var(--ac);border-radius:50%;
  animation:bounce .8s ease-in-out infinite}
.typing span:nth-child(2){animation-delay:.15s}
.typing span:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes fadein{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
footer{padding:10px 12px;background:var(--bg2);border-top:1px solid #1e2535;position:sticky;bottom:0}
.toolbar{display:flex;gap:6px;margin-bottom:8px;flex-wrap:wrap}
.btn{background:var(--bg3);border:1px solid #1e2535;color:var(--tx);
  padding:5px 10px;border-radius:8px;font-family:var(--font);font-size:11px;
  cursor:pointer;transition:all .15s}
.btn:hover,.btn.active{background:var(--ac);color:#000;border-color:var(--ac)}
.btn.imgbtn{border-color:var(--ac3);color:var(--ac3)}
.btn.imgbtn.active,.btn.imgbtn:hover{background:var(--ac3);color:#000}
.preview{margin-bottom:6px;display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.preview img{height:48px;border-radius:6px;border:1px solid var(--ac)}
.preview .doc{background:var(--bg3);padding:4px 8px;border-radius:6px;
  font-size:10px;border:1px solid #2a3d60;color:var(--ac2)}
.preview .rm{background:none;border:none;color:var(--tx2);cursor:pointer;font-size:14px}
.input-row{display:flex;gap:8px}
textarea{flex:1;background:var(--bg3);border:1px solid #1e2535;border-radius:10px;
  color:var(--tx);font-family:var(--font);font-size:13px;
  padding:10px 13px;resize:none;max-height:120px;min-height:44px;outline:none;
  transition:border-color .2s}
textarea:focus{border-color:var(--ac)}
#sendBtn{background:linear-gradient(135deg,var(--ac),var(--ac2));
  border:none;border-radius:10px;width:46px;cursor:pointer;
  font-size:20px;color:#000;font-weight:700;flex-shrink:0;transition:opacity .2s}
#sendBtn:disabled{opacity:.4;cursor:default}
input[type=file]{display:none}
#imgModal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);
  z-index:100;align-items:center;justify-content:center;padding:20px}
#imgModal img{max-width:100%;max-height:90vh;border-radius:12px}
#imgModal.open{display:flex}
</script>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════
#  FLASK API
# ══════════════════════════════════════════════════════════════
app   = Flask(__name__)
agent = Aether()

@app.route("/")
def index():
    return UI_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/chat", methods=["POST"])
def chat():
    msg     = request.form.get("message", "").strip()
    session = request.form.get("session", "default")
    file    = request.files.get("file")

    image_path  = None
    doc_context = ""

    if file and file.filename:
        # Guardar temporalmente
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        result = agent.docread.process(tmp_path, original_name=file.filename)

        if result["type"] == "image":
            image_path = result.get("path")
        elif result["type"] == "text":
            doc_context = result.get("content", "")
        # tmp_path se limpiará al reiniciar (o puede programarse cleanup)

    if not msg and not image_path and not doc_context:
        return jsonify({"output": "Mensaje vacío.", "type": "text"}), 400

    response = agent.respond(msg or "[Analiza el archivo adjunto]", session, image_path, doc_context)
    return jsonify(response)

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """Endpoint SSE para respuesta en streaming."""
    data    = request.get_json(silent=True) or {}
    msg     = data.get("message", "").strip()
    session = data.get("session", "default")

    def generate():
        yield from agent.stream_respond(msg, session)

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@app.route("/session/new", methods=["POST"])
def new_session():
    sid = agent.memory.create_session()
    return jsonify({"session_id": sid})

@app.route("/session/<sid>/history")
def session_history(sid):
    return jsonify(agent.memory.get_session_history(sid))

@app.route("/sessions")
def list_sessions():
    return jsonify(agent.memory.list_sessions())

@app.route("/stats")
def stats():
    s = agent.res.stats()
    s["coherence"] = agent.memory.coherence_score()
    return jsonify(s)

@app.route("/models")
def models_info():
    return jsonify({
        "llm":    str(LLM_MODEL),
        "mmproj": str(MMPROJ) if MMPROJ.exists() else None,
        "sd":     str(SD_MODEL) if SD_MODEL.exists() else None,
        "vision": agent.llm.has_vision,
        "imggen": agent.imggen.available,
        "ctx":    CTX_SIZE,
        "threads": THREADS,
    })

# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("━" * 54)
    print(" AETHER v2.0 · http://localhost:5000")
    print(f" Modelo : {LLM_MODEL.name}")
    print(f" Visión : {'Sí (LLaVA)' if agent.llm.has_vision else 'No (falta mmproj)'}")
    print(f" ImgGen : {'Sí (SD-Turbo)' if agent.imggen.available else 'No (falta sd/modelo)'}")
    print(f" Hilos  : {THREADS}  |  Contexto: {CTX_SIZE} tokens")
    print("━" * 54)
    app.run(host="0.0.0.0", port=5000, threaded=True)
