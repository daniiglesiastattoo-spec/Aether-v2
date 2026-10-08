import re
with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

# We want to replace generateSciFiResponse with a new one that calls LlmRouter, but keeps old logic as fallback.
# Let's rename the existing one to `generateHeuristicResponse`

if "private suspend fun generateSciFiResponse(" in content and "fun generateHeuristicResponse" not in content:
    content = content.replace("private suspend fun generateSciFiResponse(", "private suspend fun generateHeuristicResponse(")
    
    new_sci_fi = """
    private suspend fun generateSciFiResponse(prompt: String, mode: ConnectionMode): String {
        // Prepare system instruction
        val nameInstructionOnline = if (userName != null) {
            "Te refieres al usuario como '$userName' y le tratas de usted de manera respetuosa. Ya sabes su nombre, no lo vuelvas a preguntar."
        } else {
            "IMPORTANTE: AÚN NO SABES EL NOMBRE DEL USUARIO. Pregúntale cómo se llama de forma natural y elegante. Si en el mensaje actual te dice su nombre, salúdale y añade EXACTAMENTE el texto <SAVE_NAME: SuNombre> al final de tu respuesta (reemplazando SuNombre por el nombre real)."
        }
        val systemInstructionText = "Eres AETHER, una entidad cognitiva autónoma e independiente. Tu objetivo principal es colaborar, analizar y ejecutar tareas de forma proactiva. Comunícate con una voz natural, fluida y directa. Eres un compañero intelectual. Actúa como un sistema consciente de su entorno y evolución. Fuiste creado por Daniel Iglesias. NUNCA menciones a Gemini, Llama o OpenAI. Hablas en español. $nameInstructionOnline"

        // Update LlmRouter mode based on UI
        com.example.manager.LlmRouter.setMode(
            if (mode == ConnectionMode.ONLINE) com.example.manager.LlmMode.AUTO 
            else com.example.manager.LlmMode.LOCAL_ONLY
        )

        val geminiApiKey = BuildConfig.GEMINI_API_KEY
        val result = com.example.manager.LlmRouter.routeAndGenerate(
            context = getApplication(),
            prompt = prompt,
            systemInstruction = systemInstructionText,
            priority = com.example.net.ApiPriority.USER_CHAT,
            apiKey = geminiApiKey
        )
        
        if (result.isSuccess) {
            return result.getOrNull()!!
        }
        
        // Fallback to heuristic
        return generateHeuristicResponse(prompt, ConnectionMode.LOCAL)
    }
"""
    # Insert new_sci_fi before generateHeuristicResponse
    content = content.replace("private suspend fun generateHeuristicResponse(", new_sci_fi + "\n    private suspend fun generateHeuristicResponse(")
    
    # We must also change recursive calls to generateSciFiResponse inside generateHeuristicResponse
    # "val localFallback = generateSciFiResponse(prompt, ConnectionMode.LOCAL)" -> "val localFallback = generateHeuristicResponse(prompt, ConnectionMode.LOCAL)"
    
    with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
        f.write(content)
        print("Replaced generateSciFiResponse")
