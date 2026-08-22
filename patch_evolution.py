import re

with open("app/src/main/java/com/example/manager/EvolutionScanner.kt", "r") as f:
    content = f.read()

content = content.replace("BuildConfig.GROQ_API_KEY", "BuildConfig.GEMINI_API_KEY")
content = content.replace('"YOUR_GROQ_API_KEY"', '"MY_GEMINI_API_KEY"')

old_block = """            val req = GroqRequest(
                messages = listOf(
                    GroqMessage(role = "system", content = "Analiza el prompt del usuario y devuelve un número entre 0 y 100 que represente su valor para la evolución de la memoria. Solo devuelve el número. Un prompt genérico como 'hola' vale 10. Una explicación técnica detallada vale 90."),
                    GroqMessage(role = "user", content = prompt)
                )
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            val text = response.choices.firstOrNull()?.message?.content ?: "0" """

new_block = """            val req = GenerateContentRequest(
                systemInstruction = Content(parts = listOf(Part(text = "Analiza el prompt del usuario y devuelve un número entre 0 y 100 que represente su valor para la evolución de la memoria. Solo devuelve el número. Un prompt genérico como 'hola' vale 10. Una explicación técnica detallada vale 90."))),
                contents = listOf(Content(role = "user", parts = listOf(Part(text = prompt))))
            )
            val response = RetrofitClient.service.generateContent(apiKey, req)
            val text = response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: "0" """

content = content.replace(old_block, new_block)
content = content.replace("híbrido local/Groq", "híbrido local/Gemini")

with open("app/src/main/java/com/example/manager/EvolutionScanner.kt", "w") as f:
    f.write(content)

