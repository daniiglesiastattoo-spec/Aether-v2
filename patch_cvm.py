with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

content = content.replace("com.example.manager.LocalLlmEngine.isModelAvailable(context)", "(com.example.manager.LocalLlmEngine.state.value == com.example.manager.LocalLlmEngine.State.READY || com.example.manager.LocalLlmEngine.state.value == com.example.manager.LocalLlmEngine.State.LOADED)")
content = content.replace("com.example.manager.LocalLlmEngine.getModelFile(context)", "java.io.File(context.filesDir, \"models/Gemma3-1B-IT_multi-prefill-seq_q4_ekv2048.task\")")
content = content.replace("com.example.manager.LocalLlmEngine.release()", "com.example.manager.LocalLlmEngine.unload()")
content = content.replace("getApplication()", "context") # Wait, in generateSciFiResponse I used getApplication(), but context is a property of AndroidViewModel... wait, wait, I can use (this as AndroidViewModel).getApplication<Application>()

# Let's fix getApplication() in generateSciFiResponse
content = content.replace("context = getApplication(),", "context = getApplication<android.app.Application>(),")

with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
    f.write(content)
