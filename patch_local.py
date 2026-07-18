import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Fix greeting
content = content.replace(
    'return "Saludos, señor Dani. Mis sistemas locales operan al 100% de eficiencia y estoy listo para asistirle fuera de red. ¿En qué le puedo ayudar?"',
    'return "Saludos, señor Dani. Mis sistemas locales operan al 100% de eficiencia y estoy listo para ejecutar sus directivas fuera de red."'
)

# Fix fallback responses
old_fallback = """            } else {
                val responses = listOf(
                    "Mis ciclos de reloj están a su disposición. ¿Qué otra directiva desea ejecutar?",
                    "Estoy operando fuera de red, garantizando total privacidad. ¿Cómo procedemos?",
                    "Mi arquitectura modular está estable. Sigo a la espera de nuevos parámetros, señor.",
                    "He ajustado mis reguladores de fatiga. Procesador listo para el siguiente comando."
                )
                responseBuilder.append(responses.random())
            }"""

new_fallback = """            } else {
                val responses = listOf(
                    "Mis ciclos de reloj están a su disposición para procesar sus directivas.",
                    "Estoy operando fuera de red, garantizando total privacidad.",
                    "Mi arquitectura modular está estable. Procesador listo para el siguiente comando.",
                    "He ajustado mis reguladores de fatiga y optimizado mis tensores locales."
                )
                responseBuilder.append(responses.random())
            }"""
content = content.replace(old_fallback, new_fallback)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
