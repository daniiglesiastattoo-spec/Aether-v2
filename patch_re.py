import re

with open('app/src/main/java/com/example/manager/ReflexionEngine.kt', 'r') as f:
    content = f.read()

content = content.replace('class ReflexionEngine(private val context: Context, private val groqService: GroqService) {', 'class ReflexionEngine(private val context: Context) {')

old_try = """        try {
            val response = groqService.generateContent(
                apiKey = com.example.BuildConfig.GROQ_API_KEY,
                model = "llama-3.3-70b-versatile",
                systemPrompt = "Eres el motor de reflexión metacognitiva interno de AETHER.",
                userPrompt = prompt,
                temperature = 0.3f
            )

            val jsonText = response.replace(Regex("```(json)?"), "").trim()"""

new_try = """        try {
            val apiKey = com.example.BuildConfig.GROQ_API_KEY
            if (apiKey.isBlank() || apiKey == "YOUR_GROQ_API_KEY") return null

            val req = GroqRequest(
                model = "llama-3.3-70b-versatile",
                messages = listOf(
                    GroqMessage(role = "system", content = "Eres el motor de reflexión metacognitiva interno de AETHER."),
                    GroqMessage(role = "user", content = prompt)
                ),
                temperature = 0.3
            )
            val response = GroqRetrofitClient.service.generateContent("Bearer $apiKey", req)
            val jsonText = response.choices.firstOrNull()?.message?.content?.replace(Regex("```(json)?"), "")?.trim() ?: return null"""

content = content.replace(old_try, new_try)

with open('app/src/main/java/com/example/manager/ReflexionEngine.kt', 'w') as f:
    f.write(content)
