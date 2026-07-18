with open('app/src/main/java/com/example/manager/GeminiService.kt', 'r') as f:
    content = f.read()

old_req = """data class GenerateContentRequest(
    val contents: List<Content>,
    @field:Json(name = "system_instruction")
    val systemInstruction: Content? = null,
    val tools: List<Tool>? = null
)"""

new_req = """data class GenerateContentRequest(
    val contents: List<Content>,
    @field:Json(name = "system_instruction")
    val systemInstruction: Content? = null,
    val tools: List<Tool>? = null,
    val generationConfig: GenerationConfig? = null
)

data class GenerationConfig(
    val temperature: Double? = null,
    val topP: Double? = null,
    val topK: Int? = null,
    @field:Json(name = "stop_sequences")
    val stopSequences: List<String>? = null
)"""

content = content.replace(old_req, new_req)

with open('app/src/main/java/com/example/manager/GeminiService.kt', 'w') as f:
    f.write(content)
