import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

detect_old = """            onSpeechDetected = { detectedText ->
                if (_isAetherSpeaking.value) {
                    if (!isLikelyEcho(detectedText)) {
                        voiceManager.stopSpeaking()
                        _isAetherSpeaking.value = false
                        currentAetherText = ""
                    }
                }
            }"""

detect_new = """            onSpeechDetected = { detectedText ->
                if (_isAetherSpeaking.value) {
                    if (!isLikelyEcho(detectedText)) {
                        voiceManager.stopSpeaking()
                    }
                }
            }"""

content = content.replace(detect_old, detect_new)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("onSpeechDetected patched")
