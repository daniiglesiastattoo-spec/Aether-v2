with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

content = content.replace("com.example.manager.LocalLlmEngine.getModelFile(viewModel.context)", "java.io.File(androidx.compose.ui.platform.LocalContext.current.filesDir, \"models/Gemma3-1B-IT_multi-prefill-seq_q4_ekv2048.task\")")

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
