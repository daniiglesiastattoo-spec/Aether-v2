import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

local_vision = '    private val localVisionEngine = com.example.manager.LocalVisionEngine(context)'
if local_vision not in content:
    content = content.replace('    private val reflexionEngine = com.example.manager.ReflexionEngine(context)',
                              '    private val reflexionEngine = com.example.manager.ReflexionEngine(context)\n' + local_vision)

func_old = 'private suspend fun generateGeminiVisionResponse(bitmap: android.graphics.Bitmap, prompt: String, isOnline: Boolean): String {'
func_new = 'private suspend fun generateGeminiVisionResponse(bitmap: android.graphics.Bitmap, prompt: String, isOnline: Boolean, localTags: String): String {'
content = content.replace(func_old, func_new)

fallback_old = """        if (!isOnline) {
            return "NÚCLEO AETHER: [Procesamiento Óptico Local] He capturado la imagen. Al estar desconectado de la red global, mi heurística local infiere mampostería relacional, un terminal parpadeante y un observador en primera persona."
        }"""
fallback_new = """        if (!isOnline) {
            return "NÚCLEO AETHER: [Procesamiento Óptico Local] Análisis offline. Elementos detectados: $localTags"
        }"""
content = content.replace(fallback_old, fallback_new)

apikey_fallback_old = """        if (apiKey.isBlank() || apiKey == "MY_GEM" || apiKey == "MY_GEMINI_API_KEY") {
            return "NÚCLEO AETHER: [Aviso de Red] He capturado la imagen en tiempo real, pero no se ha encontrado una clave API válida para acceder a la red neuronal global de Google. Heurística local activada."
        }"""
apikey_fallback_new = """        if (apiKey.isBlank() || apiKey == "MY_GEM" || apiKey == "MY_GEMINI_API_KEY") {
            return "NÚCLEO AETHER: [Aviso de Red] Clave API Gemini no encontrada. Análisis local detectó: $localTags"
        }"""
content = content.replace(apikey_fallback_old, apikey_fallback_new)

trigger_old = """            if (capturedBitmap != null) {
                addMessage(Message(
                    text = "FOTO CAPTURADA EXITOSAMENTE. ENVIANDO MATRIZ DE PÍXELES A ANALIZADOR ÓPTICO...",
                    sender = Sender.AETHER,
                    status = MessageStatus.VERIFIED
                ))
                desc = generateGeminiVisionResponse(capturedBitmap, "Describe exactamente lo que ves en esta imagen de la cámara en tiempo real con total detalle, e identifica información que podrías usar a través de las herramientas de búsqueda de Google.", isOnline)
            }"""
trigger_new = """            if (capturedBitmap != null) {
                val localTags = localVisionEngine.analyze(capturedBitmap)
                addMessage(Message(
                    text = "FOTO CAPTURADA EXITOSAMENTE. RESULTADO LOCAL OBTENIDO: $localTags.\\nENVIANDO A AETHER-NÚCLEO-CLOUD PARA DESCRIPCIÓN RICA...",
                    sender = Sender.AETHER,
                    status = MessageStatus.VERIFIED
                ))
                val enhancedPrompt = "Etiquetas locales detectadas: $localTags. Describe exactamente lo que ves en esta imagen de la cámara en tiempo real con total detalle, e identifica información que podrías usar a través de las herramientas de búsqueda de Google. Integra las etiquetas locales detectadas en tu descripción si tienen sentido."
                desc = generateGeminiVisionResponse(capturedBitmap, enhancedPrompt, isOnline, localTags)
            }"""
content = content.replace(trigger_old, trigger_new)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("ChatViewModel patched for vision")
