import re

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'r') as f:
    content = f.read()

# Update interface
old_interface = "    fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit, onSpeechDetected: () -> Unit = {})\n"
new_interface = "    fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit, onSpeechDetected: (String) -> Unit = {})\n"
content = content.replace(old_interface, new_interface)

# Update implementation signature
old_impl = "    override fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit, onSpeechDetected: () -> Unit) {\n"
new_impl = "    override fun startListening(onResult: (String) -> Unit, onError: (String) -> Unit, onSpeechDetected: (String) -> Unit) {\n"
content = content.replace(old_impl, new_impl)

# Update onPartialResults
old_partial = """                            mainHandler.post { onSpeechDetected() }"""
new_partial = """                            mainHandler.post { onSpeechDetected(text) }"""
content = content.replace(old_partial, new_partial)

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'w') as f:
    f.write(content)
print("VoiceManager updated")
