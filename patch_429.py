import re

with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

# Patch 1: generateSciFiResponse fallback
old_sci = """                if (is429) {
                    return "NÚCLEO AETHER: Límite de procesamiento cognitivo en cluster online alcanzado (HTTP 429). Por favor, aguarda."
                }"""

new_sci = """                if (is429) {
                    val localFallback = generateSciFiResponse(prompt, ConnectionMode.LOCAL)
                    return "NÚCLEO AETHER: [ALERTA HTTP 429] Red neuronal online sobrecargada. Ejecutando salto de emergencia a proceso heurístico LOCAL:\n\n$localFallback"
                }"""

content = content.replace(old_sci, new_sci)

# Patch 2: generateGeminiVisionResponse fallback
old_vis = """                val is503 = e.message?.contains("503") == true || (e as? retrofit2.HttpException)?.code() == 503
                if (attempt < 2) {
                    kotlinx.coroutines.delay(1000L * attempt)
                    continue
                }
                if (is503) {
                    return "NÚCLEO AETHER: Conexión visual caída por alta demanda en el nodo (Servicio 503). Por favor reintenta en breve."
                }"""

new_vis = """                val is503 = e.message?.contains("503") == true || (e as? retrofit2.HttpException)?.code() == 503
                val is429 = e.message?.contains("429") == true || (e as? retrofit2.HttpException)?.code() == 429
                if (attempt < 2) {
                    kotlinx.coroutines.delay(1000L * attempt)
                    continue
                }
                if (is429) {
                    return "NÚCLEO AETHER: [ALERTA HTTP 429] Límite visual online alcanzado. Visión conmutada a offline. Análisis local estimativo: $localTags"
                }
                if (is503) {
                    return "NÚCLEO AETHER: Conexión visual caída por alta demanda en el nodo (Servicio 503). Por favor reintenta en breve."
                }"""

content = content.replace(old_vis, new_vis)

with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
    f.write(content)
