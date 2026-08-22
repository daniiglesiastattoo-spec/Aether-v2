import re

with open("app/src/main/java/com/example/manager/ReflexionEngine.kt", "r") as f:
    content = f.read()

old_block1 = """            val req = GroqRequest(
                model = "llama-3.3-70b-versatile",
                messages = listOf(
                    GroqMessage(role = "system", content = "Eres el motor de reflexión metacognitiva interno de AETHER."),
                    GroqMessage(role = "user", content = prompt)
                ),
                temperature = 0.3
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            val jsonText = response.choices.firstOrNull()?.message?.content?.replace(Regex("```(json)?"), "")?.trim() ?: return null"""

new_block1 = """            val req = GenerateContentRequest(
                systemInstruction = Content(parts = listOf(Part(text = "Eres el motor de reflexión metacognitiva interno de AETHER."))),
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt)))),
                generationConfig = GenerationConfig(temperature = 0.3)
            )
            val response = RetrofitClient.service.generateContent(apiKey, req)
            val jsonText = response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text?.replace(Regex("```(json)?"), "")?.trim() ?: return null"""
            
content = content.replace(old_block1, new_block1)

with open("app/src/main/java/com/example/manager/ReflexionEngine.kt", "w") as f:
    f.write(content)


with open("app/src/main/java/com/example/manager/EvolutionScanner.kt", "r") as f:
    content2 = f.read()

old_block2 = """            val req = GroqRequest(
                model = "llama-3.3-70b-versatile",
                messages = listOf(
                    GroqMessage(role = "user", content = prompt)
                ),
                temperature = 0.3
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            val jsonText = response.choices.firstOrNull()?.message?.content?.replace(Regex("```(json)?"), "")?.trim() ?: return 0"""

new_block2 = """            val req = GenerateContentRequest(
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt)))),
                generationConfig = GenerationConfig(temperature = 0.3)
            )
            val response = RetrofitClient.service.generateContent(apiKey, req)
            val jsonText = response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text?.replace(Regex("```(json)?"), "")?.trim() ?: return 0"""
            
content2 = content2.replace(old_block2, new_block2)

with open("app/src/main/java/com/example/manager/EvolutionScanner.kt", "w") as f:
    f.write(content2)

