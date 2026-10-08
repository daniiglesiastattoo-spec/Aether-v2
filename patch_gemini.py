with open("app/src/main/java/com/example/manager/GeminiService.kt", "r") as f:
    content = f.read()

new_client = """
object GeminiClient {
    suspend fun generateContentSafe(
        apiKey: String,
        request: GenerateContentRequest,
        priority: com.example.net.ApiPriority
    ): Result<String> {
        return com.example.net.RetryPolicy.executeWithRetry(
            provider = com.example.net.ApiProvider.GEMINI,
            priority = priority
        ) {
            val response = RetrofitClient.service.generateContent(apiKey, request)
            response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text 
                ?: throw Exception("Respuesta vacía o formato inválido de Gemini")
        }
    }
}
"""

if "object GeminiClient" not in content:
    content = content + new_client
    with open("app/src/main/java/com/example/manager/GeminiService.kt", "w") as f:
        f.write(content)
        print("Patched GeminiService")
else:
    print("Already patched")
