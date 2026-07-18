import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# 1. Update toggleLiveModePause
old_toggle = """    fun toggleLiveModePause() {
        val newState = !_isLiveModePaused.value
        _isLiveModePaused.value = newState
        
        if (newState) {
            // Paused
            voiceManager.stopListening()
            _isRecordingVoice.value = false
        } else {
            // Resumed
            if (_isLiveMode.value && !_isAetherSpeaking.value) {
                startLiveModeListening()
            }
        }
    }"""
new_toggle = """    fun toggleLiveModePause() {
        val newState = !_isLiveModePaused.value
        _isLiveModePaused.value = newState
        
        if (newState) {
            // Paused
            if (_isAetherSpeaking.value) {
                voiceManager.stopSpeaking()
                _isAetherSpeaking.value = false
            }
            voiceManager.stopListening()
            _isRecordingVoice.value = false
        } else {
            // Resumed
            if (_isLiveMode.value && !_isAetherSpeaking.value) {
                startLiveModeListening()
            }
        }
    }"""
content = content.replace(old_toggle, new_toggle)

# 2. Update speakAndListen
old_speak = """    private fun speakAndListen(text: String, isOnline: Boolean) {
        _isAetherSpeaking.value = true
        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            if (_isLiveMode.value && !_isRecordingVoice.value) {
                startLiveModeListening()
            }
        }
    }"""
new_speak = """    private fun speakAndListen(text: String, isOnline: Boolean) {
        _isAetherSpeaking.value = true
        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            if (_isLiveMode.value && !_isRecordingVoice.value && !_isLiveModePaused.value) {
                startLiveModeListening()
            }
        }
        
        // Empezar a escuchar inmediatamente para poder interrumpir a Aether
        if (_isLiveMode.value && !_isRecordingVoice.value && !_isLiveModePaused.value) {
            startLiveModeListening()
        }
    }"""
content = content.replace(old_speak, new_speak)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("Patched ChatViewModel")
