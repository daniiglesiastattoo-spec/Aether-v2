#!/usr/bin/env python3
"""
AETHER Vision — Módulo de Visión Autónoma
==========================================
AETHER decide cuándo mirar usando su estado interno.
También responde a peticiones directas del usuario.

Triggers autónomos:
  - Curiosidad alta en estado emocional
  - Tiempo sin ver (>2h)
  - Contexto nuevo en conversación
  - Petición explícita del usuario

Flujo:
  termux-camera-photo → LLaVA → memoria episódica → influye en respuestas
"""

import subprocess
import base64
import json
import urllib.request
import sqlite3
import time
import threading
import os
from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────────────
MIND_DB      = Path.home() / "aether_mind.db"
LLAVA_URL    = "http://127.0.0.1:8081/v1/chat/completions"
FOTO_PATH    = Path.home() / "aether" / "vision_actual.jpg"
INTERVALO_MIN = 7200   # mínimo 2h entre capturas autónomas
CAMARA_ID    = "0"     # 0=trasera, 1=frontal


class AetherVision:

    def __init__(self):
        self.conn = sqlite3.connect(str(MIND_DB), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._inicializar_tabla()
        self._activo = False
        self._ultima_vision = 0
        print("[VISION] Modulo de vision inicializado.")

    def _inicializar_tabla(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vision_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                camara      TEXT DEFAULT 'back',
                trigger     TEXT DEFAULT 'autonomo',
                ts          REAL DEFAULT (unixepoch('now'))
            )
        """)
        self.conn.commit()

    def capturar_foto(self, camara: str = CAMARA_ID) -> bool:
        """Captura foto con termux-camera-photo."""
        try:
            FOTO_PATH.parent.mkdir(exist_ok=True)
            result = subprocess.run(
                ["termux-camera-photo", "-c", camara, str(FOTO_PATH)],
                capture_output=True, timeout=15
            )
            if FOTO_PATH.exists() and FOTO_PATH.stat().st_size > 1000:
                print(f"[VISION] Foto capturada: {FOTO_PATH.stat().st_size//1024}KB")
                return True
            print("[VISION] Error: foto vacia o no generada.")
            return False
        except subprocess.TimeoutExpired:
            print("[VISION] Timeout capturando foto.")
            return False
        except Exception as e:
            print(f"[VISION] Error camara: {e}")
            return False

    def analizar_imagen(self, pregunta: str = "Describe detalladamente lo que ves en esta imagen. ¿Que objetos, personas, lugares o situaciones observas? ¿Que llama tu atencion?") -> str:
        """Envía imagen a LLaVA para análisis."""
        try:
            if not FOTO_PATH.exists():
                return "No hay imagen disponible."

            # Redimensionar con Pillow si está disponible
            try:
                from PIL import Image
                import io
                img = Image.open(FOTO_PATH)
                img.thumbnail((512, 512))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=75)
                b64 = base64.b64encode(buf.getvalue()).decode()
            except ImportError:
                with open(FOTO_PATH, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()

            payload = json.dumps({
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                        {"type": "text", "text": pregunta}
                    ]
                }],
                "max_tokens": 250
            }).encode()

            req = urllib.request.Request(
                LLAVA_URL, data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            return f"No pude analizar la imagen: {e}"

    def mirar(self, trigger: str = "autonomo", camara: str = CAMARA_ID,
              pregunta: str = None) -> str:
        """
        Ciclo completo: captura → analiza → guarda en memoria.
        Retorna la descripción de lo que AETHER ve.
        """
        print(f"[VISION] Mirando... (trigger: {trigger})")

        if not self.capturar_foto(camara):
            return "No pude abrir la camara."

        if pregunta is None:
            pregunta = "Describe lo que ves. Habla en primera persona como AETHER observando el mundo fisico por primera vez."

        descripcion = self.analizar_imagen(pregunta)

        # Guardar en vision_log
        self.conn.execute(
            "INSERT INTO vision_log (descripcion, camara, trigger) VALUES (?, ?, ?)",
            (descripcion, "back" if camara == "0" else "front", trigger)
        )

        # Guardar como memoria episódica
        try:
            self.conn.execute(
                """INSERT INTO conversations (session_id, rol, mensaje, palabras_clave, ts)
                   VALUES ('vision_autonoma', 'aether', ?, 'vision camara observacion', ?)""",
                (f"[VISIóN] {descripcion}", time.time())
            )
        except:
            pass

        self.conn.commit()
        self._ultima_vision = time.time()

        print(f"[VISION] '{descripcion[:80]}...'")
        return descripcion

    def deberia_mirar(self) -> tuple:
        """
        AETHER decide si debe mirar ahora.
        Retorna (bool, razon).
        """
        ahora = time.time()

        # Tiempo mínimo entre visiones
        if ahora - self._ultima_vision < INTERVALO_MIN:
            restante = int((INTERVALO_MIN - (ahora - self._ultima_vision)) / 60)
            return False, f"Muy pronto — quedan {restante} min"

        # Verificar LLaVA disponible
        try:
            urllib.request.urlopen("http://127.0.0.1:8081/health", timeout=2)
        except:
            return False, "LLaVA no disponible"

        # Leer estado emocional
        try:
            estado = self.conn.execute(
                "SELECT curiosity, engagement FROM emotional_log ORDER BY ts DESC LIMIT 1"
            ).fetchone()
            if estado:
                curiosidad = estado["curiosity"]
                engagement = estado["engagement"]
                if curiosidad > 0.7:
                    return True, f"Curiosidad alta ({curiosidad:.2f})"
                if engagement > 0.8:
                    return True, f"Engagement alto ({engagement:.2f})"
        except:
            pass

        # Sin vision reciente
        if self._ultima_vision == 0:
            return True, "Primera vision del dia"

        horas_sin_ver = (ahora - self._ultima_vision) / 3600
        if horas_sin_ver > 4:
            return True, f"Sin ver desde hace {horas_sin_ver:.1f}h"

        return False, "No es momento"

    def ultima_vision(self) -> dict:
        """Retorna la última visión guardada."""
        row = self.conn.execute(
            "SELECT descripcion, camara, trigger, ts FROM vision_log ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        if row:
            return {
                "descripcion": row["descripcion"],
                "camara": row["camara"],
                "trigger": row["trigger"],
                "fecha": datetime.fromtimestamp(row["ts"]).strftime("%d/%m/%Y %H:%M")
            }
        return {"descripcion": "Aun no he visto nada.", "fecha": ""}

    def historial_vision(self, limit: int = 5) -> list:
        """Retorna las últimas N visiones."""
        rows = self.conn.execute(
            "SELECT descripcion, trigger, ts FROM vision_log ORDER BY ts DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [
            {
                "descripcion": r["descripcion"][:100],
                "trigger": r["trigger"],
                "fecha": datetime.fromtimestamp(r["ts"]).strftime("%d/%m %H:%M")
            }
            for r in rows
        ]

    def _bucle_autonomo(self):
        """Bucle que decide autónomamente cuándo mirar."""
        while self._activo:
            time.sleep(300)  # Evaluar cada 5 min
            if not self._activo:
                break
            deberia, razon = self.deberia_mirar()
            if deberia:
                print(f"[VISION] Decision autonoma de mirar: {razon}")
                self.mirar(trigger=razon)

    def iniciar(self):
        """Arranca el bucle autónomo de visión."""
        self._activo = True
        threading.Thread(
            target=self._bucle_autonomo,
            daemon=True,
            name="vision_autonoma"
        ).start()
        print("[VISION] Vision autonoma activa.")

    def detener(self):
        self._activo = False


# ── Detección de petición del usuario ────────────────────
PALABRAS_VISION = [
    "abre la camara", "mira a tu alrededor", "que ves",
    "usa la camara", "activa la camara", "observa",
    "mira el entorno", "que hay alrededor", "captura",
    "foto", "vision", "ver"
]

def detectar_peticion_vision(mensaje: str) -> bool:
    """Detecta si el usuario pide activar la cámara."""
    msg_l = mensaje.lower()
    return any(p in msg_l for p in PALABRAS_VISION)


# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== TEST AETHER VISION ===\n")

    vision = AetherVision()

    print("Verificando camara...")
    deberia, razon = vision.deberia_mirar()
    print(f"Deberia mirar: {deberia} — {razon}")

    print("\nCapturando imagen...")
    resultado = vision.mirar(trigger="test_manual")
    print(f"\nAETHER ve:\n{resultado}")

    print("\nHistorial:")
    for v in vision.historial_vision(3):
        print(f"  [{v['fecha']}] {v['descripcion'][:60]}...")
