#!/usr/bin/env python3
"""
Integra AetherMemory en aether_stream.py
Ejecutar: python integrar_memoria.py
"""
import re

ARCHIVO = "/data/data/com.termux/files/home/aether/aether_stream.py"

with open(ARCHIVO, "r", encoding="utf-8") as f:
    codigo = f.read()

# ── CAMBIO 1: Importar y arrancar memoria junto a MIND ──
# Busca el bloque HAS_MIND y añade HAS_MEMORY después
viejo_1 = """try:
    from aether_mind import ConsciousnessLayer"""

nuevo_1 = """try:
    from aether_memory import AetherMemory
    memory = AetherMemory()
    HAS_MEMORY = True
    print("[MEMORY] ✓ Memoria episódica activa.")
except Exception as e:
    HAS_MEMORY = False
    print(f"[MEMORY] No disponible: {e}")

try:
    from aether_mind import ConsciousnessLayer"""

# ── CAMBIO 2: Inyectar contexto de memoria antes del LLM ──
viejo_2 = """    if HAS_MIND:
        try:
            ctx = mind.context_for(msg, "default")
            system = SYSTEM + "\\n" + ctx[:400]
        except: pass"""

nuevo_2 = """    if HAS_MEMORY:
        try:
            ctx_mem = memory.contexto_relevante(msg)
            if ctx_mem:
                system = SYSTEM + "\\n" + ctx_mem[:600]
        except: pass

    if HAS_MIND:
        try:
            ctx = mind.context_for(msg, "default")
            system = system + "\\n" + ctx[:400]
        except: pass"""

# ── CAMBIO 3: Guardar conversación después de responder ──
viejo_3 = """        if HAS_MIND:
            try: mind.update(msg, "".join(full), "default")
            except: pass
        yield "[FIN]" """

nuevo_3 = """        if HAS_MEMORY:
            try: memory.guardar(msg, "".join(full))
            except: pass
        if HAS_MIND:
            try: mind.update(msg, "".join(full), "default")
            except: pass
        yield "[FIN]" """

# Aplicar cambios
cambios = [
    (viejo_1, nuevo_1, "Importar AetherMemory"),
    (viejo_2, nuevo_2, "Inyectar contexto"),
    (viejo_3, nuevo_3, "Guardar conversación"),
]

errores = []
for viejo, nuevo, nombre in cambios:
    if viejo in codigo:
        codigo = codigo.replace(viejo, nuevo, 1)
        print(f"✅ {nombre}")
    else:
        errores.append(nombre)
        print(f"⚠️  No encontrado: {nombre} — aplicar manualmente")

if errores:
    print("\n⚠️  Algunos cambios no se pudieron aplicar automáticamente.")
    print("Revisa aether_stream.py manualmente para estos bloques:")
    for e in errores:
        print(f"  - {e}")
else:
    # Guardar solo si todo fue bien
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(codigo)
    print("\n✅ Integración completa. Reinicia AETHER.")
    print("   ~/aether/start.sh")
