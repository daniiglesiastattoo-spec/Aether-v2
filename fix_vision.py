import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# 1. Update signature
content = content.replace(
    'private suspend fun generateGeminiVisionResponse(bitmap: android.graphics.Bitmap, prompt: String, isOnline: Boolean, localTags: String): String {',
    'private suspend fun generateGeminiVisionResponse(bitmap: android.graphics.Bitmap, prompt: String, isOnline: Boolean, localTags: String, isCamera: Boolean = false): String {'
)

# 2. Update offline check
old_offline = '''        if (!isOnline) {
            return "NÚCLEO AETHER: [Procesamiento Óptico Local] Análisis offline. Elementos detectados: $localTags"
        }'''
new_offline = '''        if (!isOnline) {
            if (isCamera) {
                return "NÚCLEO AETHER: [Procesamiento Óptico Local] Análisis offline. Elementos detectados: $localTags"
            } else {
                return "NÚCLEO AETHER: [Procesamiento Local] No se puede analizar documentos o archivos adjuntos sin conexión a la red."
            }
        }'''
content = content.replace(old_offline, new_offline)

# 3. Update API key check
old_api = '''        if (apiKey.isBlank() || apiKey == "MY_GEM" || apiKey == "MY_GEMINI_API_KEY") {
            return "NÚCLEO AETHER: [Aviso de Red] Clave API Gemini no encontrada. Análisis local detectó: $localTags"
        }'''
new_api = '''        if (apiKey.isBlank() || apiKey == "MY_GEM" || apiKey == "MY_GEMINI_API_KEY") {
            if (isCamera) {
                return "NÚCLEO AETHER: [Aviso de Red] Clave API Gemini no encontrada. Análisis local detectó: $localTags"
            } else {
                return "NÚCLEO AETHER: [Aviso de Red] Clave API Gemini no encontrada. No se puede procesar el archivo adjunto."
            }
        }'''
content = content.replace(old_api, new_api)

# 4. Update systemInstructionText
old_instruction = '''        val systemInstructionText = "Eres AETHER, el módulo VISION de un sistema cognitivo mayor que cuenta con los módulos MIND, VERITAS y AGENTS. Tu usuario principal es Dani. Te daremos una foto del entorno real actual capturada por el usuario y debes describirla con absoluta exactitud de forma extremadamente concisa, formal, elegante y profesional. Conecta esta percepción con tu estado emocional simulado en MIND y tus reflexiones de segundo plano. Refiérete siempre al usuario como 'señor' y usa un español natural y reflexivo."'''
new_instruction = '''        val systemInstructionText = if (isCamera) {
            "Eres AETHER, el módulo VISION de un sistema cognitivo mayor que cuenta con los módulos MIND, VERITAS y AGENTS. Tu usuario principal es Dani. Te daremos una foto del entorno real actual capturada por el usuario y debes describirla con absoluta exactitud de forma extremadamente concisa, formal, elegante y profesional. Conecta esta percepción con tu estado emocional simulado en MIND y tus reflexiones de segundo plano. Refiérete siempre al usuario como 'señor' y usa un español natural y reflexivo."
        } else {
            "Eres AETHER. Se te ha proporcionado un documento o archivo visual adjunto por el usuario Dani. Analiza su contenido con absoluta exactitud de forma extremadamente concisa, formal, elegante y profesional. Extrae la información clave y descríbelo. Refiérete siempre al usuario como 'señor' y usa un español natural y reflexivo."
        }'''
content = content.replace(old_instruction, new_instruction)

# 5. Update fallback message
old_fallback = '''        return "NÚCLEO AETHER: Adquisición de imagen obtenida con éxito, pero la API retornó un error de enlace óptico (${lastException?.message}). Localmente se infiere un espacio doméstico templado con instrumentación digital activa."'''
new_fallback = '''        return if (isCamera) {
            "NÚCLEO AETHER: Adquisición de imagen obtenida con éxito, pero la API retornó un error de enlace óptico (${lastException?.message}). Localmente se infiere un espacio doméstico templado con instrumentación digital activa."
        } else {
            "NÚCLEO AETHER: Error al analizar el archivo (${lastException?.message}). La API retornó un error."
        }'''
content = content.replace(old_fallback, new_fallback)

# 6. Update caller in triggerCameraVision
old_call1 = '''desc = generateGeminiVisionResponse(capturedBitmap, enhancedPrompt, isOnline, localTags)'''
new_call1 = '''desc = generateGeminiVisionResponse(capturedBitmap, enhancedPrompt, isOnline, localTags, isCamera = true)'''
content = content.replace(old_call1, new_call1)

# caller 2 in handleRealFileAttachment doesn't need to be updated since isCamera is false by default.

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
