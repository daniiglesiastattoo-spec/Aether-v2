import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Add _isLiveModePaused state
state_code = """
    private val _isLiveMode = MutableStateFlow(false)
    val isLiveMode: StateFlow<Boolean> = _isLiveMode.asStateFlow()
    
    private val _isLiveModePaused = MutableStateFlow(false)
    val isLiveModePaused: StateFlow<Boolean> = _isLiveModePaused.asStateFlow()
"""
content = re.sub(r'private val _isLiveMode = MutableStateFlow\(false\)\s*val isLiveMode: StateFlow<Boolean> = _isLiveMode\.asStateFlow\(\)', state_code, content)

# Add toggleLiveModePause method
toggle_pause_code = """
    fun toggleLiveModePause() {
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
    }
    
    fun toggleLiveMode() {
"""
content = content.replace("    fun toggleLiveMode() {", toggle_pause_code)

# Add pause check to startLiveModeListening
content = content.replace("if (!_isLiveMode.value) return\n        if (_isRecordingVoice.value) return", "if (!_isLiveMode.value || _isLiveModePaused.value) return\n        if (_isRecordingVoice.value) return")

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)

print("Patch applied")
