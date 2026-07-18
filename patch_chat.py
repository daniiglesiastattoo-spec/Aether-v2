import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Replace ConnectionMode.LOCAL with ConnectionMode.ONLINE for default value
content = re.sub(r'MutableStateFlow\(ConnectionMode\.LOCAL\)', r'MutableStateFlow(ConnectionMode.ONLINE)', content, count=1)

# Modify startLiveModeListening
old_start_listen = """    fun startLiveModeListening() {
        if (!_isLiveMode.value) return
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
            }
        )
    }"""

new_start_listen = """    private fun speakAndListen(text: String, isOnline: Boolean) {
        _isAetherSpeaking.value = true
        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            if (_isLiveMode.value && !_isRecordingVoice.value) {
                startLiveModeListening()
            }
        }
        if (_isLiveMode.value) {
            startLiveModeListening()
        }
    }

    fun startLiveModeListening() {
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

content = content.replace(old_start_listen, new_start_listen)

# Replace the speak blocks
content = re.sub(
    r'_isAetherSpeaking\.value = true\s*voiceManager\.speak\(([^,]+),\s*isOnlineMode\s*=\s*(.*?)\)\s*\{\s*_isAetherSpeaking\.value = false\s*if \(_isLiveMode\.value\)\s*\{\s*startLiveModeListening\(\)\s*\}\s*\}',
    r'speakAndListen(\1, \2)',
    content
)

content = re.sub(
    r'_isAetherSpeaking\.value = true\s*voiceManager\.speak\(([^,]+),\s*isOnlineMode\s*=\s*(.*?)\)\s*\{\s*_isAetherSpeaking\.value = false\s*if \(_isLiveMode\.value\)\s*startLiveModeListening\(\)\s*\}',
    r'speakAndListen(\1, \2)',
    content
)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)

print("Patch applied")
