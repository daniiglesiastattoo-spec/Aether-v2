import re

with open("app/src/main/java/com/example/manager/ReflexionEngine.kt", "r") as f:
    content = f.read()

content = content.replace("BuildConfig.GROQ_API_KEY", "BuildConfig.GEMINI_API_KEY")
content = content.replace('"YOUR_GROQ_API_KEY"', '"MY_GEMINI_API_KEY"')

old_block = """            val req = GroqRequest(
                messages = listOf(
                    GroqMessage(role = "system", content = "Eres el motor de reflexión metacognitiva interno de AETHER."),
                    GroqMessage(role = "user", content = prompt)
                )
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            return response.choices.firstOrNull()?.message?.content"""

new_block = """            val req = GenerateContentRequest(
                systemInstruction = Content(parts = listOf(Part(text = "Eres el motor de reflexión metacognitiva interno de AETHER."))),
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt))))
            )
            val response = RetrofitClient.service.generateContent(apiKey, req)
            return response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text"""

content = content.replace(old_block, new_block)

with open("app/src/main/java/com/example/manager/ReflexionEngine.kt", "w") as f:
    f.write(content)

