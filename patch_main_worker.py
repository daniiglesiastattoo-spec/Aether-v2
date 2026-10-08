import re
with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

# Check for existing WorkManager import
imports = "import androidx.work.OneTimeWorkRequestBuilder\nimport androidx.work.WorkManager\nimport com.example.manager.ModelDownloadWorker\nimport com.example.manager.LocalLlmEngine\nimport com.example.manager.ModelDownloadState\nimport androidx.work.NetworkType\nimport androidx.work.Constraints\n"

if "import androidx.work.WorkManager" not in content:
    content = content.replace("package com.example\n", "package com.example\n\n" + imports)

# We can launch the worker in a LaunchedEffect
download_effect = """
    LaunchedEffect(Unit) {
        LocalLlmEngine.checkModelState(context)
        if (LocalLlmEngine.state.value == LocalLlmEngine.State.NOT_DOWNLOADED || LocalLlmEngine.state.value == LocalLlmEngine.State.FAILED) {
            val constraints = Constraints.Builder().setRequiredNetworkType(NetworkType.UNMETERED).build()
            val request = OneTimeWorkRequestBuilder<ModelDownloadWorker>().setConstraints(constraints).build()
            WorkManager.getInstance(context).enqueue(request)
        }
    }
    val dlProgress by ModelDownloadState.progress.collectAsStateWithLifecycle()
    val dlStatus by ModelDownloadState.status.collectAsStateWithLifecycle()
"""
if "val dlProgress by ModelDownloadState.progress" not in content:
    # insert inside AetherAppScreen
    target = "fun AetherAppScreen(viewModel: ChatViewModel) {"
    idx = content.find(target)
    if idx != -1:
        # Find the end of the line
        end_idx = content.find("\n", idx)
        content = content[:end_idx] + "\n" + download_effect + content[end_idx:]

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
    print("Patched Worker start")
