#!/usr/bin/env python3
"""
AETHER Online Mode — Integración Groq
======================================
Llama 3.3 70B como LLM online.
Veritas, Memory y ConStan KB activos en ambos modos.
"""

import urllib.request
import urllib.error
import json
import os
from pathlib import Path

# ── Configuración ────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
KEY_PATH     = Path.home() / "aether" / ".groq_key"

# Estado global del modo
_modo_online = False


def cargar_key() -> str:
    """Lee la API key de Groq desde archivo."""
    try:
        key = KEY_PATH.read_text().strip()
        if key.startswith("gsk_"):
            return key
        raise ValueError("Key inválida — debe empezar por gsk_")
    except FileNotFoundError:
        raise RuntimeError(f"No se encontró la key en {KEY_PATH}")


def esta_online() -> bool:
    """Comprueba si hay conexión a internet."""
    try:
        urllib.request.urlopen("https://api.groq.com", timeout=3)
        return True
    except:
        return False


def get_modo() -> bool:
    """Retorna el modo actual (True=online, False=offline)."""
    return _modo_online


def set_modo(online: bool) -> dict:
    """
    Cambia el modo de AETHER.
    Retorna estado del cambio.
    """
    global _modo_online

    if online:
        if not esta_online():
            return {
                "ok": False,
                "modo": "offline",
                "mensaje": "Sin conexión a internet. Permaneciendo en modo offline."
            }
        try:
            cargar_key()
        except Exception as e:
            return {
                "ok": False,
                "modo": "offline",
                "mensaje": f"Error con la API key: {e}"
            }
        _modo_online = True
        return {
            "ok": True,
            "modo": "online",
            "modelo": GROQ_MODEL,
            "mensaje": f"Modo online activo — {GROQ_MODEL}"
        }
    else:
        _modo_online = False
        return {
            "ok": True,
            "modo": "offline",
            "modelo": "phi-3-mini-local",
            "mensaje": "Modo offline activo — Phi-3-mini local"
        }


def groq_stream(system: str, mensaje: str):
    """
    Genera respuesta streaming desde Groq.
    Yield de tokens igual que llama-server local.
    """
    key = cargar_key()

    payload = json.dumps({
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": mensaje}
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
        "stream": True
    }).encode()

    req = urllib.request.Request(
        GROQ_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        for line in resp:
            line = line.decode().strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                j = json.loads(data)
                token = j["choices"][0]["delta"].get("content", "")
                if token:
                    yield token
            except:
                pass


def groq_simple(system: str, mensaje: str) -> str:
    """
    Respuesta completa sin streaming (para uso interno).
    """
    key = cargar_key()

    payload = json.dumps({
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": mensaje}
        ],
        "max_tokens": 512,
        "temperature": 0.7,
        "stream": False
    }).encode()

    req = urllib.request.Request(
        GROQ_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]


def info_modo() -> dict:
    """Retorna información del modo actual para la UI."""
    if _modo_online:
        return {
            "modo": "online",
            "modelo": GROQ_MODEL,
            "proveedor": "Groq",
            "icono": "🌐",
            "color": "#00dcff"
        }
    else:
        return {
            "modo": "offline",
            "modelo": "Phi-3-mini-Q4",
            "proveedor": "Local",
            "icono": "📱",
            "color": "#00ff9d"
        }


# ── TEST ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== TEST AETHER ONLINE MODE ===\n")

    print("1. Verificando conexión...")
    online = esta_online()
    print(f"   Internet: {'✅' if online else '❌'}")

    print("\n2. Cargando key...")
    try:
        key = cargar_key()
        print(f"   Key: {key[:8]}...{key[-4:]} ✅")
    except Exception as e:
        print(f"   Error: {e}")
        exit(1)

    print("\n3. Activando modo online...")
    resultado = set_modo(True)
    print(f"   {resultado['mensaje']}")

    if resultado["ok"]:
        print("\n4. Test de respuesta Groq...")
        try:
            respuesta = groq_simple(
                "Eres AETHER, una IA local consciente creada por Daniel Iglesias López.",
                "Di 'AETHER online operativo' y nada más."
            )
            print(f"   Groq dice: {respuesta.strip()}")
            print("\n✅ Modo online completamente funcional.")
        except Exception as e:
            print(f"   Error en llamada: {e}")

    print(f"\n📊 Info modo: {info_modo()}")
