import re

with open('app/src/main/java/com/example/manager/GroqService.kt', 'r') as f:
    content = f.read()

old_req = """data class GroqRequest(
    val model: String = "llama-3.3-70b-versatile",
    val messages: List<GroqMessage>,
    val max_tokens: Int = 1024,
    val temperature: Double = 0.7
)"""

new_req = """data class GroqRequest(
    val model: String = "llama-3.3-70b-versatile",
    val messages: List<GroqMessage>,
    val max_tokens: Int = 1024,
    val temperature: Double = 0.7,
    val top_p: Double = 0.9,
    val stop: List<String> = listOf("\\n\\nUser:")
)"""

content = content.replace(old_req, new_req)

with open('app/src/main/java/com/example/manager/GroqService.kt', 'w') as f:
    f.write(content)
