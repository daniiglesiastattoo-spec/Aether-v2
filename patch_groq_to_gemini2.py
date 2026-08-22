import os

def replace_in_file(filepath, old, new):
    with open(filepath, 'r') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        print(f"String not found in {filepath}: {old[:50]}...")

# ChatViewModel.kt changes
replace_in_file("app/src/main/java/com/example/ChatViewModel.kt", 
    'groqApiKey == "MY_GROQ_API_KEY"', 
    'groqApiKey == "MY_GEMINI_API_KEY"')
    
replace_in_file("app/src/main/java/com/example/ChatViewModel.kt",
"""                                val groqMessages = listOf(
                                    com.example.manager.GroqMessage(role = "system", content = "Eres AETHER. Resume el contenido del archivo proporcionado."),
                                    com.example.manager.GroqMessage(role = "user", content = summaryPrompt)
                                )
                                val req = com.example.manager.GroqRequest(messages = groqMessages)
                                val resp = com.example.manager.GroqRetrofitClient.service.generateContent("Bearer $groqApiKey", req)
                                val summary = resp.choices.firstOrNull()?.message?.content ?: "Resumen no disponible.\"""",
"""                                val req = com.example.manager.GenerateContentRequest(
                                    systemInstruction = com.example.manager.Content(parts = listOf(com.example.manager.Part(text = "Eres AETHER. Resume el contenido del archivo proporcionado."))),
                                    contents = listOf(com.example.manager.Content(role = "user", parts = listOf(com.example.manager.Part(text = summaryPrompt))))
                                )
                                val resp = com.example.manager.RetrofitClient.service.generateContent(groqApiKey, req)
                                val summary = resp.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: "Resumen no disponible.\"""")

