import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Insert speakAndListen before startLiveModeListening
speak_and_listen_code = """
    private fun speakAndListen(text: String, isOnline: Boolean) {
        _isAetherSpeaking.value = true
        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            if (_isLiveMode.value && !_isRecordingVoice.value) {
                startLiveModeListening()
            }
        }
    }

"""

if "private fun speakAndListen" not in content:
    content = content.replace("    fun startLiveModeListening() {", speak_and_listen_code + "    fun startLiveModeListening() {")

# Update startLiveModeListening
import re
new_start = """    fun startLiveModeListening() {
        if (!_isLiveMode.value) return
        if (_isRecordingVoice.value) return
        _isRecordingVoice.value = true
        voiceManager.startListening(
            onResult = { resultText ->
                _isRecordingVoice.value = false
                viewModelScope.launch {
                    processUserInput(resultText)
                }
            },
            onError = { error ->
                _isRecordingVoice.value = false
                // Auto-retry in live mode on silent errors
                if (error == "No se entendió" || error == "Silencio corto" || error == "Vacío") {
                    startLiveModeListening()
                } else {
                    _messages.value = _messages.value + Message(
                        text = "MÚLTIPLES ERRORES EN SISTEMA VOCAL: $error. Live Mode desactivado.",
                        sender = Sender.AETHER,
                        status = MessageStatus.UNCERTAIN
                    )
                    _isLiveMode.value = false
                }
            },
            onSpeechDetected = {
                if (_isAetherSpeaking.value) {
                    voiceManager.stopSpeaking()
                    _isAetherSpeaking.value = false
                }
            }
        )
    }"""

# We'll use regex to replace startLiveModeListening
content = re.sub(r'    fun startLiveModeListening\(\) \{[\s\S]*?(?=\n    })' + '\n    }', new_start, content)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)

print("Patch 2 applied")
