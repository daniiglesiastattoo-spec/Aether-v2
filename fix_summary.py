import re

with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

old_block = """                                val req = com.example.manager.GenerateContentRequest(
                                    systemInstruction = com.example.manager.Content(parts = listOf(com.example.manager.Part(text = "Eres AETHER. Resume el contenido del archivo proporcionado."))),
                                    contents = listOf(com.example.manager.Content(role = "user", parts = listOf(com.example.manager.Part(text = summaryPrompt))))
                                )
                                val resp = com.example.manager.RetrofitClient.service.generateContent(geminiApiKey, req)
                                resp.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: "SISTEMA AETHER: He indexado el contenido de '$fileName'."""

new_block = """                                try {
                                    val req = com.example.manager.GenerateContentRequest(
                                        systemInstruction = com.example.manager.Content(parts = listOf(com.example.manager.Part(text = "Eres AETHER. Resume el contenido del archivo proporcionado."))),
                                        contents = listOf(com.example.manager.Content(role = "user", parts = listOf(com.example.manager.Part(text = summaryPrompt))))
                                    )
                                    val resp = com.example.manager.RetrofitClient.service.generateContent(geminiApiKey, req)
                                    resp.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: "SISTEMA AETHER: He indexado el contenido de '$fileName'."
                                } catch (e: Exception) {
                                    "SISTEMA AETHER: He interiorizado el documento '$fileName' en modo local. (No se pudo procesar online: ${e.message})"
                                }"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
        f.write(content)
        print("Fixed summary")
else:
    print("Not found")
