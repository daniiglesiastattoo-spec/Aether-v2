with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Update Gemini Vision request
old_gemini = """            systemInstruction = com.example.manager.Content(
                role = "system",
                parts = listOf(com.example.manager.Part(text = systemInstructionText))
            ),
            tools = listOf(
                com.example.manager.Tool(googleSearch = com.example.manager.GoogleSearch())
            )
        )"""

new_gemini = """            systemInstruction = com.example.manager.Content(
                role = "system",
                parts = listOf(com.example.manager.Part(text = systemInstructionText))
            ),
            tools = listOf(
                com.example.manager.Tool(googleSearch = com.example.manager.GoogleSearch())
            ),
            generationConfig = com.example.manager.GenerationConfig(
                temperature = 0.7,
                topP = 0.9,
                topK = 40,
                stopSequences = listOf("\\n\\nUser:")
            )
        )"""

content = content.replace(old_gemini, new_gemini)

# Update Groq request in ChatViewModel
# Oh wait, we already set the default values in GroqRequest itself! So we don't strictly need to update it,
# but GroqRequest is constructed in ChatViewModel.kt:
# val request = com.example.manager.GroqRequest(
#     messages = groqMessages
# )
# It will use the default values: temperature = 0.7, top_p = 0.9, stop = listOf("\n\nUser:")

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
