import re
with open("app/src/main/java/com/example/manager/ReflexionEngine.kt", "r") as f:
    content = f.read()

old_call = """            val response = RetrofitClient.service.generateContent(apiKey, req)
            val jsonText = response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text?.replace(Regex("```(json)?"), "")?.trim() ?: return null"""

new_call = """            val result = GeminiClient.generateContentSafe(apiKey, req, com.example.net.ApiPriority.BACKGROUND_REFLEXION)
            if (result.isFailure) return null
            val jsonText = result.getOrNull()?.replace(Regex("```(json)?"), "")?.trim() ?: return null"""

if old_call in content:
    content = content.replace(old_call, new_call)
    with open("app/src/main/java/com/example/manager/ReflexionEngine.kt", "w") as f:
        f.write(content)
        print("Patched ReflexionEngine")
else:
    print("Not found in ReflexionEngine")
