import re

with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

# Replace Groq with Gemini references
content = content.replace(
    'return "SISTEMA ERROR: Clave API de Groq no configurada. Ingresa tu clave GROQ en los secretos para usar el modo ONLINE."', 
    'return "SISTEMA ERROR: Clave API de Gemini no configurada. Ingresa tu clave GEMINI en los secretos para usar el modo ONLINE."')

old_block2 = """        val groqMessages = mutableListOf<com.example.manager.GroqMessage>()
        groqMessages.add(com.example.manager.GroqMessage(role = "system", content = systemInstructionText))
        
        val maxHistory = _allDbMessages.value.filter {
            !it.text.startsWith("FOTO CAPTURADA") &&
            !it.text.startsWith("DISPOSITIVO DE VISIÓN") &&
            !it.text.startsWith("INTEGRACIÓN LOGRADA") &&
            !it.text.startsWith("SISTEMA:") &&
            !it.text.startsWith("CARGANDO VECTOR") &&
            !it.text.startsWith("SOLICITANDO CAPTURA")
        }.takeLast(8)
        
        maxHistory.forEach { msg ->
            val roleStr = if (msg.sender == com.example.model.Sender.USER) "user" else "assistant"
            groqMessages.add(com.example.manager.GroqMessage(role = roleStr, content = msg.text))
        }
        
        if (maxHistory.isEmpty() || maxHistory.last().text != prompt) {
            groqMessages.add(com.example.manager.GroqMessage(role = "user", content = prompt))
        }

        val request = com.example.manager.GroqRequest(
            messages = groqMessages
        )

        var lastException: Exception? = null
        for (attempt in 1..3) {
            try {
                val response = com.example.manager.GroqRetrofitClient.service.generateContent(
                    "Bearer $groqApiKey",
                    request
                )
                return response.choices.firstOrNull()?.message?.content ?: "NÚCLEO AETHER: Error de divergencia en la respuesta Groq."
            } catch (e: Exception) {
                lastException = e
                android.util.Log.e("AETHER", "Error en llamada a Groq", e)"""

new_block2 = """        val geminiContents = mutableListOf<com.example.manager.Content>()
        
        val maxHistory = _allDbMessages.value.filter {
            !it.text.startsWith("FOTO CAPTURADA") &&
            !it.text.startsWith("DISPOSITIVO DE VISIÓN") &&
            !it.text.startsWith("INTEGRACIÓN LOGRADA") &&
            !it.text.startsWith("SISTEMA:") &&
            !it.text.startsWith("CARGANDO VECTOR") &&
            !it.text.startsWith("SOLICITANDO CAPTURA")
        }.takeLast(8)
        
        maxHistory.forEach { msg ->
            val roleStr = if (msg.sender == com.example.model.Sender.USER) "user" else "model"
            geminiContents.add(com.example.manager.Content(role = roleStr, parts = listOf(com.example.manager.Part(text = msg.text))))
        }
        
        if (maxHistory.isEmpty() || maxHistory.last().text != prompt) {
            geminiContents.add(com.example.manager.Content(role = "user", parts = listOf(com.example.manager.Part(text = prompt))))
        }

        val request = com.example.manager.GenerateContentRequest(
            systemInstruction = com.example.manager.Content(parts = listOf(com.example.manager.Part(text = systemInstructionText))),
            contents = geminiContents
        )

        var lastException: Exception? = null
        for (attempt in 1..3) {
            try {
                val response = com.example.manager.RetrofitClient.service.generateContent(
                    groqApiKey,
                    request
                )
                return response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: "NÚCLEO AETHER: Error de divergencia en la respuesta Gemini."
            } catch (e: Exception) {
                lastException = e
                android.util.Log.e("AETHER", "Error en llamada a Gemini", e)"""

content = content.replace(old_block2, new_block2)
with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
    f.write(content)
