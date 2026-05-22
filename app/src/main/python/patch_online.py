#!/usr/bin/env python3
"""
Integra modo online/offline en aether_stream.py
Ejecutar: python ~/aether/patch_online.py
"""
import os, shutil, re
from datetime import datetime

STREAM = os.path.expanduser("~/aether/aether_stream.py")

with open(STREAM, "r") as f:
    code = f.read()

# Backup
ts = datetime.now().strftime("%H%M%S")
shutil.copy2(STREAM, STREAM + ".bak_" + ts)
print(f"✅ Backup creado")

# ── CAMBIO 1: Importar aether_online ────────────────────
viejo_1 = "from aether_veritas import AetherVeritas"
nuevo_1 = """from aether_veritas import AetherVeritas
try:
    from aether_online import groq_stream, set_modo, get_modo, info_modo
    HAS_ONLINE = True
    print("[ONLINE] ✓ Módulo online cargado.")
except Exception as e:
    HAS_ONLINE = False
    print(f"[ONLINE] No disponible: {e}")"""

# ── CAMBIO 2: Ruta para toggle online/offline ────────────
ruta_toggle = """

@app.route("/modo", methods=["POST"])
def cambiar_modo():
    if not HAS_ONLINE:
        return jsonify({"ok": False, "mensaje": "Módulo online no disponible"})
    data = request.json or {}
    online = data.get("online", False)
    resultado = set_modo(online)
    return jsonify(resultado)

@app.route("/modo", methods=["GET"])
def estado_modo():
    if not HAS_ONLINE:
        return jsonify({"modo": "offline", "modelo": "phi-3-mini-local"})
    return jsonify(info_modo())

"""

# ── CAMBIO 3: Usar Groq o local según modo ───────────────
viejo_3 = """    payload = json.dumps({
        "messages":[
            {"role":"system","content":system},
            {"role":"user","content":msg}
        ],
        "max_tokens": 150,
        "stream": True,
        "temperature": 0.7
    }).encode()

    def generate():
        full = []
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:8080/v1/chat/completions",
                data=payload,
                headers={"Content-Type":"application/json"}
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                for line in resp:
                    line = line.decode().strip()
                    if not line.startswith("data:"): continue
                    data = line[5:].strip()
                    if data == "[DONE]": break
                    try:
                        j = json.loads(data)
                        token = j["choices"][0]["delta"].get("content","")
                        if token:
                            full.append(token)
                            yield token + "|||"
                    except: pass
        except Exception as e:
            yield "Error: " + str(e) + "|||"
        if HAS_MEMORY:
            try: memory.guardar(msg, "".join(full))
            except: pass
        if HAS_MIND:
            try: mind.update(msg, "".join(full), "default")
            except: pass
        yield "[FIN]" """

nuevo_3 = """    def generate():
        full = []
        try:
            # ── Modo online (Groq) ──────────────────────
            if HAS_ONLINE and get_modo():
                for token in groq_stream(system, msg):
                    full.append(token)
                    yield token + "|||"
            # ── Modo offline (llama local) ──────────────
            else:
                payload = json.dumps({
                    "messages":[
                        {"role":"system","content":system},
                        {"role":"user","content":msg}
                    ],
                    "max_tokens": 150,
                    "stream": True,
                    "temperature": 0.7
                }).encode()
                req = urllib.request.Request(
                    "http://127.0.0.1:8080/v1/chat/completions",
                    data=payload,
                    headers={"Content-Type":"application/json"}
                )
                with urllib.request.urlopen(req, timeout=300) as resp:
                    for line in resp:
                        line = line.decode().strip()
                        if not line.startswith("data:"): continue
                        data = line[5:].strip()
                        if data == "[DONE]": break
                        try:
                            j = json.loads(data)
                            token = j["choices"][0]["delta"].get("content","")
                            if token:
                                full.append(token)
                                yield token + "|||"
                        except: pass
        except Exception as e:
            yield "Error: " + str(e) + "|||"
        if HAS_MEMORY:
            try: memory.guardar(msg, "".join(full))
            except: pass
        if HAS_MIND:
            try: mind.update(msg, "".join(full), "default")
            except: pass
        yield "[FIN]" """

# Aplicar cambios
errores = []

if viejo_1 in code:
    code = code.replace(viejo_1, nuevo_1, 1)
    print("✅ Importación online añadida")
else:
    errores.append("Importación")

# Insertar rutas antes de if __name__
if 'if __name__' in code:
    code = code.replace('if __name__', ruta_toggle + 'if __name__', 1)
    print("✅ Rutas /modo añadidas")
else:
    # Insertar al final
    code += ruta_toggle
    print("✅ Rutas /modo añadidas al final")

if viejo_3 in code:
    code = code.replace(viejo_3, nuevo_3, 1)
    print("✅ Lógica online/offline integrada")
else:
    errores.append("Lógica streaming")
    print("⚠️  No se encontró el bloque de streaming exacto")
    print("   Aplica el cambio manualmente en la función generate()")

if errores:
    print(f"\n⚠️  Cambios pendientes: {errores}")
else:
    with open(STREAM, "w") as f:
        f.write(code)
    print("\n✅ Integración completa.")
    print("   Reinicia AETHER: ~/aether/start.sh")

# Añadir botón toggle a la UI también
print("\n📝 Recuerda añadir el botón toggle en la UI.")
print("   El endpoint es POST /modo con body: {\"online\": true/false}")
