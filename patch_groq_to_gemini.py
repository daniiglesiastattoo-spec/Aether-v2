import os
import glob

def replace_in_file(filepath, old, new):
    with open(filepath, 'r') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w') as f:
            f.write(content)

# For ReflexionEngine.kt
replace_in_file("app/src/main/java/com/example/manager/ReflexionEngine.kt", 
    'val apiKey = com.example.BuildConfig.GROQ_API_KEY', 
    'val apiKey = com.example.BuildConfig.GEMINI_API_KEY')
replace_in_file("app/src/main/java/com/example/manager/ReflexionEngine.kt", 
    'if (apiKey.isBlank() || apiKey == "YOUR_GROQ_API_KEY") return null', 
    'if (apiKey.isBlank() || apiKey == "MY_GEMINI_API_KEY") return null')

replace_in_file("app/src/main/java/com/example/manager/ReflexionEngine.kt", 
    """            val req = GroqRequest(
                messages = listOf(
                    GroqMessage(role = "system", content = "Eres el motor de reflexión metacognitiva interno de AETHER."),
                    GroqMessage(role = "user", content = prompt)
                )
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            return response.choices.firstOrNull()?.message?.content""",
    """            val req = GenerateContentRequest(
                systemInstruction = Content(parts = listOf(Part(text = "Eres el motor de reflexión metacognitiva interno de AETHER."))),
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt))))
            )
            val response = RetrofitClient.service.generateContent(apiKey, req)
            return response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text""")


# For EvolutionScanner.kt
replace_in_file("app/src/main/java/com/example/manager/EvolutionScanner.kt", 
    'val apiKey = com.example.BuildConfig.GROQ_API_KEY', 
    'val apiKey = com.example.BuildConfig.GEMINI_API_KEY')
replace_in_file("app/src/main/java/com/example/manager/EvolutionScanner.kt", 
    'if (apiKey.isBlank() || apiKey == "YOUR_GROQ_API_KEY") return 0', 
    'if (apiKey.isBlank() || apiKey == "MY_GEMINI_API_KEY") return 0')

replace_in_file("app/src/main/java/com/example/manager/EvolutionScanner.kt", 
    """            val req = GroqRequest(
                messages = listOf(
                    GroqMessage(role = "system", content = "Analiza el prompt del usuario y devuelve un número entre 0 y 100 que represente su valor para la evolución de la memoria. Solo devuelve el número. Un prompt genérico como 'hola' vale 10. Una explicación técnica detallada vale 90."),
                    GroqMessage(role = "user", content = prompt)
                )
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            val text = response.choices.firstOrNull()?.message?.content ?: "0" """,
    """            val req = GenerateContentRequest(
                systemInstruction = Content(parts = listOf(Part(text = "Analiza el prompt del usuario y devuelve un número entre 0 y 100 que represente su valor para la evolución de la memoria. Solo devuelve el número. Un prompt genérico como 'hola' vale 10. Una explicación técnica detallada vale 90."))),
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt))))
            )
            val response = RetrofitClient.service.generateContent(apiKey, req)
            val text = response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: "0" """)


# For ChatViewModel.kt
replace_in_file("app/src/main/java/com/example/ChatViewModel.kt", 
    'val groqApiKey = BuildConfig.GROQ_API_KEY', 
    'val groqApiKey = BuildConfig.GEMINI_API_KEY')
replace_in_file("app/src/main/java/com/example/ChatViewModel.kt", 
    'groqApiKey != "MY_GROQ_API_KEY"', 
    'groqApiKey != "MY_GEMINI_API_KEY"')

replace_in_file("app/src/main/java/com/example/ChatViewModel.kt", 
    """                                val groqMessages = listOf(
                                    com.example.manager.GroqMessage(role = "system", content = "Eres AETHER. Resume el contenido del archivo proporcionado."),
                                    com.example.manager.GroqMessage(role = "user", content = summaryPrompt)
                                )
                                val req = com.example.manager.GroqRequest(messages = groqMessages)
                                val resp = com.example.manager.GroqRetrofitClient.service.generateContent("Bearer $groqApiKey", req)
                                val summary = resp.choices.firstOrNull()?.message?.content ?: "Resumen no disponible."""",
    """                                val req = com.example.manager.GenerateContentRequest(
                                    systemInstruction = com.example.manager.Content(parts = listOf(com.example.manager.Part(text = "Eres AETHER. Resume el contenido del archivo proporcionado."))),
                                    contents = listOf(com.example.manager.Content(role = "user", parts = listOf(com.example.manager.Part(text = summaryPrompt))))
                                )
                                val resp = com.example.manager.RetrofitClient.service.generateContent(groqApiKey, req)
                                val summary = resp.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: "Resumen no disponible."""")

