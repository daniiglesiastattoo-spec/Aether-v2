with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

trim_method = """
    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)
        if (level == android.content.ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW || level == android.content.ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL) {
            com.example.manager.LocalLlmEngine.unload()
        }
    }
"""
if "onTrimMemory" not in content:
    content = content.replace("class MainActivity : ComponentActivity() {", "class MainActivity : ComponentActivity() {\n" + trim_method)
    with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
        f.write(content)
        print("Patched trim memory")
