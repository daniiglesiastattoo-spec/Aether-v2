#!/usr/bin/env python3
"""
AETHER Agents — Motor de Agentes
=================================
Herramientas disponibles:
  - calculadora: evalúa expresiones matemáticas
  - fecha_hora: fecha y hora actual
  - busqueda_web: búsqueda DuckDuckGo sin API
  - galeria: lista y analiza imágenes con LLaVA
"""

import re
import os
import json
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# ── Rutas ────────────────────────────────────────────────
LLAVA_MODEL = Path.home() / "aether" / "llava-phi-3-mini-q4_k_m.gguf"
LLAMA_SERVER = Path.home() / "bin" / "llama-server"
GALERIA_PATH = Path("/sdcard/DCIM")
NOTAS_PATH   = Path.home() / "aether" / "notas.json"


# ══════════════════════════════════════════════════════════
# HERRAMIENTA 1: CALCULADORA
# ══════════════════════════════════════════════════════════
def herramienta_calculadora(expresion: str) -> str:
    """Evalúa una expresión matemática de forma segura."""
    try:
        # Limpiar expresión
        expr = expresion.strip()
        expr = expr.replace("x", "*").replace("×", "*").replace("÷", "/")
        expr = expr.replace(",", ".")
        expr = re.sub(r"[^0-9+\-*/().\s%]", "", expr)

        if not expr:
            return "No entendí la expresión matemática."

        # Evaluar de forma segura
        resultado = eval(expr, {"__builtins__": {}}, {})

        # Formatear resultado
        if isinstance(resultado, float) and resultado.is_integer():
            resultado = int(resultado)

        return f"{expresion} = {resultado}"
    except ZeroDivisionError:
        return "Error: división por cero."
    except Exception as e:
        return f"No pude calcular eso: {e}"


# ══════════════════════════════════════════════════════════
# HERRAMIENTA 2: FECHA Y HORA
# ══════════════════════════════════════════════════════════
def herramienta_fecha_hora(consulta: str = "") -> str:
    """Devuelve fecha, hora o información temporal."""
    ahora = datetime.now()

    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    dia_semana = dias[ahora.weekday()]
    mes = meses[ahora.month - 1]

    consulta_l = consulta.lower()

    if "hora" in consulta_l:
        return f"Son las {ahora.strftime('%H:%M')} del {dia_semana} {ahora.day} de {mes} de {ahora.year}."
    elif "día" in consulta_l or "dia" in consulta_l or "fecha" in consulta_l:
        return f"Hoy es {dia_semana}, {ahora.day} de {mes} de {ahora.year}."
    elif "año" in consulta_l:
        return f"Estamos en {ahora.year}."
    elif "mes" in consulta_l:
        return f"Estamos en {mes} de {ahora.year}."
    else:
        return f"Hoy es {dia_semana}, {ahora.day} de {mes} de {ahora.year}, y son las {ahora.strftime('%H:%M')}."


# ══════════════════════════════════════════════════════════
# HERRAMIENTA 3: BÚSQUEDA WEB
# ══════════════════════════════════════════════════════════
def herramienta_busqueda_web(consulta: str) -> str:
    """Busca en DuckDuckGo Instant Answer API sin API key."""
    try:
        query = urllib.parse.quote(consulta)
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AETHER/2.0"}
        )

        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        # Respuesta directa
        if data.get("AbstractText"):
            fuente = data.get("AbstractSource", "")
            texto = data["AbstractText"][:400]
            return f"{texto}\n[Fuente: {fuente}]"

        # Respuesta de tipo definición
        if data.get("Answer"):
            return data["Answer"]

        # Resultados relacionados
        if data.get("RelatedTopics"):
            resultados = []
            for topic in data["RelatedTopics"][:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    resultados.append(topic["Text"][:150])
            if resultados:
                return "Encontré esto:\n• " + "\n• ".join(resultados)

        return f"No encontré información directa sobre '{consulta}'. Prueba a ser más específico."

    except Exception as e:
        return f"Error al buscar: {e}"


# ══════════════════════════════════════════════════════════
# HERRAMIENTA 4: GALERÍA
# ══════════════════════════════════════════════════════════
def herramienta_galeria_listar(filtro: str = "") -> str:
    """Lista imágenes de la galería del dispositivo."""
    try:
        rutas = [
            Path("/sdcard/DCIM/Camera"),
            Path("/sdcard/Pictures"),
            Path("/sdcard/Download"),
        ]

        imagenes = []
        extensiones = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

        for ruta in rutas:
            if ruta.exists():
                for f in sorted(ruta.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                    if f.suffix.lower() in extensiones:
                        if not filtro or filtro.lower() in f.name.lower():
                            imagenes.append(f)
                        if len(imagenes) >= 10:
                            break

        if not imagenes:
            return "No encontré imágenes en la galería."

        lista = []
        for img in imagenes[:8]:
            fecha = datetime.fromtimestamp(img.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
            lista.append(f"• {img.name} ({fecha})")

        return f"Encontré {len(imagenes)} imagen(es):\n" + "\n".join(lista)

    except Exception as e:
        return f"No pude acceder a la galería: {e}"


def herramienta_galeria_analizar(ruta_imagen: str) -> str:
    """Analiza una imagen usando LLaVA."""
    if not LLAVA_MODEL.exists():
        return "El modelo de visión LLaVA no está disponible."

    ruta = Path(ruta_imagen)
    if not ruta.exists():
        # Buscar por nombre parcial
        for directorio in [Path("/sdcard/DCIM/Camera"), Path("/sdcard/Pictures")]:
            if directorio.exists():
                for f in directorio.iterdir():
                    if ruta_imagen.lower() in f.name.lower():
                        ruta = f
                        break

    if not ruta.exists():
        return f"No encontré la imagen: {ruta_imagen}"

    try:
        # Llamar a llama-server con LLaVA
        cmd = [
            str(LLAMA_SERVER),
            "-m", str(LLAVA_MODEL),
            "--image", str(ruta),
            "-p", "Describe esta imagen en español de forma detallada.",
            "-n", "200",
            "--no-display-prompt",
            "-t", "2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.stdout:
            return result.stdout.strip()
        return "No pude analizar la imagen."
    except subprocess.TimeoutExpired:
        return "El análisis tardó demasiado."
    except Exception as e:
        return f"Error al analizar imagen: {e}"


# ══════════════════════════════════════════════════════════
# DETECTOR DE INTENCIÓN
# ══════════════════════════════════════════════════════════
class DetectorIntencion:
    """Detecta qué herramienta usar según el mensaje."""

    PATRONES = {
        "calculadora": [
            r"\b(\d+[\s]*[+\-*/×÷x%][\s]*\d+)",
            r"\bcuánto\s+es\b.{0,30}\d",
            r"\bcalcula\b",
            r"\b\d+\s*(?:por|entre|más|menos|dividido)\s*\d+",
            r"\bporcentaje\b.*\d",
            r"\b\d+%\s+de\s+\d+",
        ],
        "fecha_hora": [
            r"\bqué\s+hora\b",
            r"\bqué\s+día\b",
            r"\bfecha\s+(?:de\s+)?hoy\b",
            r"\bhoy\s+es\b",
            r"\bqué\s+(?:día|fecha|mes|año)\b",
            r"\bcu[aá]ndo\s+es\b",
            r"\btiempo\s+(?:actual|ahora)\b",
        ],
        "busqueda_web": [
            r"\bquién\s+es\b",
            r"\bqué\s+es\b",
            r"\bcuándo\s+(?:fue|nació|murió)\b",
            r"\bdónde\s+(?:está|queda)\b",
            r"\bbusca\b",
            r"\binforma(?:ción)?\s+sobre\b",
            r"\bnoticia[s]?\b",
            r"\búltimo[s]?\b.{0,20}\b(?:sobre|de)\b",
            r"\bganó\b",
            r"\bpresidente\b",
            r"\bcapital\s+de\b",
        ],
        "galeria_listar": [
            r"\bmi[s]?\s+foto[s]?\b",
            r"\bmi[s]?\s+imagen[es]?\b",
            r"\bgaler[ií]a\b",
            r"\bmuestra\b.{0,20}\bfoto[s]?\b",
            r"\bver\b.{0,20}\bfoto[s]?\b",
            r"\búltima[s]?\s+foto[s]?\b",
        ],
        "galeria_analizar": [
            r"\banaliza\b.{0,30}\b(?:foto|imagen)\b",
            r"\bqué\s+(?:ves|hay)\s+en\b",
            r"\bdescribe\b.{0,20}\b(?:foto|imagen)\b",
            r"\bque\s+muestra\b",
        ],
    }

    def detectar(self, mensaje: str) -> tuple:
        """
        Retorna (herramienta, confianza) o (None, 0).
        """
        msg_l = mensaje.lower()

        for herramienta, patrones in self.PATRONES.items():
            for patron in patrones:
                if re.search(patron, msg_l):
                    return herramienta, 0.9

        return None, 0.0


# ══════════════════════════════════════════════════════════
# MOTOR DE AGENTES
# ══════════════════════════════════════════════════════════
class AetherAgents:
    """Motor principal de agentes de AETHER."""

    def __init__(self):
        self.detector = DetectorIntencion()
        self.herramientas = {
            "calculadora":     herramienta_calculadora,
            "fecha_hora":      herramienta_fecha_hora,
            "busqueda_web":    herramienta_busqueda_web,
            "galeria_listar":  herramienta_galeria_listar,
            "galeria_analizar": herramienta_galeria_analizar,
        }
        print("[AGENTS] Motor de agentes activo.")

    def procesar(self, mensaje: str) -> dict:
        """
        Procesa un mensaje y ejecuta la herramienta si corresponde.
        Retorna dict con resultado o None si no hay herramienta aplicable.
        """
        herramienta, confianza = self.detector.detectar(mensaje)

        if not herramienta or confianza < 0.8:
            return {"herramienta": None, "resultado": None}

        print(f"[AGENTS] Herramienta detectada: {herramienta}")

        try:
            fn = self.herramientas[herramienta]

            if herramienta == "calculadora":
                # Extraer la expresión matemática
                expr = re.search(r"[\d\s+\-*/×÷x%(),.]+", mensaje)
                arg = expr.group(0).strip() if expr else mensaje
                resultado = fn(arg)

            elif herramienta == "fecha_hora":
                resultado = fn(mensaje)

            elif herramienta == "busqueda_web":
                # Extraer término de búsqueda
                termino = re.sub(
                    r"^(busca|qué es|quién es|dónde está|información sobre|cuándo)\s*",
                    "", mensaje, flags=re.IGNORECASE
                ).strip()
                resultado = fn(termino or mensaje)

            elif herramienta == "galeria_listar":
                # Extraer filtro opcional
                filtro = re.search(r"de\s+(\w+)", mensaje)
                arg = filtro.group(1) if filtro else ""
                resultado = fn(arg)

            elif herramienta == "galeria_analizar":
                # Extraer nombre de imagen
                nombre = re.search(r"(?:foto|imagen)\s+[\"']?([^\"']+)[\"']?", mensaje, re.IGNORECASE)
                arg = nombre.group(1).strip() if nombre else ""
                resultado = fn(arg)

            else:
                resultado = fn(mensaje)

            return {
                "herramienta": herramienta,
                "resultado": resultado,
                "confianza": confianza
            }

        except Exception as e:
            return {
                "herramienta": herramienta,
                "resultado": f"Error en herramienta {herramienta}: {e}",
                "confianza": confianza
            }

    def listar_herramientas(self) -> list:
        return list(self.herramientas.keys())


# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== TEST AETHER AGENTS ===\n")
    agents = AetherAgents()

    casos = [
        "¿Cuánto es 347 × 28?",
        "¿Qué hora es?",
        "¿Qué día es hoy?",
        "¿Quién es el presidente de España?",
        "Muestra mis fotos",
        "¿Qué es la relatividad general?",
        "Calcula el 15% de 2400",
    ]

    for caso in casos:
        r = agents.procesar(caso)
        if r["herramienta"]:
            print(f"[{r['herramienta']}] {caso}")
            print(f"  → {r['resultado']}\n")
        else:
            print(f"[LLM] {caso}\n")
