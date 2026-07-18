import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Add currentAetherText state
state_block_old = """    private val _isRecordingVoice = MutableStateFlow(false)
    val isRecordingVoice: StateFlow<Boolean> = _isRecordingVoice"""
state_block_new = """    private val _isRecordingVoice = MutableStateFlow(false)
    val isRecordingVoice: StateFlow<Boolean> = _isRecordingVoice
    
    private var currentAetherText: String = \"\""""
content = content.replace(state_block_old, state_block_new)

# Update speakAndListen
speak_old = """    private fun speakAndListen(text: String, isOnline: Boolean) {
        _isAetherSpeaking.value = true
        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            if (_isLiveMode.value && !_isRecordingVoice.value && !_isLiveModePaused.value) {
                startLiveModeListening()
            }
        }
    }"""
speak_new = """    private fun speakAndListen(text: String, isOnline: Boolean) {
        currentAetherText = text
        _isAetherSpeaking.value = true
        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            currentAetherText = ""
            if (_isLiveMode.value && !_isRecordingVoice.value && !_isLiveModePaused.value) {
                startLiveModeListening()
            }
        }
        
        // Empezar a escuchar inmediatamente para poder interrumpir a Aether
        if (_isLiveMode.value && !_isRecordingVoice.value && !_isLiveModePaused.value) {
            startLiveModeListening()
        }
    }"""
content = content.replace(speak_old, speak_new)

# Update startLiveModeListening
listen_old = """        voiceManager.startListening(
            onResult = { resultText ->
                _isRecordingVoice.value = false
                viewModelScope.launch {
                    sendMessage(resultText)
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
                    voiceManager.setLiveMode(false)
                }
            },
            onSpeechDetected = {
                if (_isAetherSpeaking.value) {
                    voiceManager.stopSpeaking()
                    _isAetherSpeaking.value = false
                }
            }
        )"""

listen_new = """        voiceManager.startListening(
            onResult = { resultText ->
                _isRecordingVoice.value = false
                if (isLikelyEcho(resultText)) {
                    // Es eco, lo ignoramos y seguimos escuchando
                    if (_isLiveMode.value && !_isLiveModePaused.value) {
                        startLiveModeListening()
                    }
                } else {
                    viewModelScope.launch {
                        sendMessage(resultText)
                    }
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
                    voiceManager.setLiveMode(false)
                }
            },
            onSpeechDetected = { detectedText ->
                if (_isAetherSpeaking.value) {
                    if (!isLikelyEcho(detectedText)) {
                        voiceManager.stopSpeaking()
                        _isAetherSpeaking.value = false
                        currentAetherText = ""
                    }
                }
            }
        )"""
content = content.replace(listen_old, listen_new)

# Add isLikelyEcho method before startLiveModeListening
echo_method = """    private fun isLikelyEcho(recognizedText: String): Boolean {
        if (currentAetherText.isEmpty()) return false
        val normalRecognized = recognizedText.lowercase().replace(Regex("[^a-záéíóúñ0-9 ]"), "").trim()
        val normalSpoken = currentAetherText.lowercase().replace(Regex("[^a-záéíóúñ0-9 ]"), "").trim()
        
        if (normalRecognized.isEmpty() || normalSpoken.isEmpty()) return false
        
        if (normalSpoken.contains(normalRecognized)) {
            return true
        }
        
        val recognizedWords = normalRecognized.split(" ").filter { it.length > 2 }
        if (recognizedWords.isEmpty()) return false
        
        val spokenWords = normalSpoken.split(" ")
        
        var matchCount = 0
        for (word in recognizedWords) {
            if (spokenWords.contains(word)) {
                matchCount++
            }
        }
        
        val matchRatio = matchCount.toFloat() / recognizedWords.size
        return matchRatio > 0.6f
    }

    fun startLiveModeListening() {"""
content = content.replace("    fun startLiveModeListening() {", echo_method)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("ChatViewModel updated")
