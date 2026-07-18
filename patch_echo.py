import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# 1. Add variables
var_old = """    private var currentAetherText: String = ""
    private val _isAetherSpeaking = MutableStateFlow(false)"""

var_new = """    private var currentAetherText: String = ""
    private var lastAetherText: String = ""
    private var lastAetherSpeakEndTime: Long = 0
    private val _isAetherSpeaking = MutableStateFlow(false)"""

content = content.replace(var_old, var_new)

# 2. Update speakAndListen
speak_old = """        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            currentAetherText = ""
            if (_isLiveMode.value && !_isRecordingVoice.value && !_isLiveModePaused.value) {"""

speak_new = """        voiceManager.speak(text, isOnlineMode = isOnline) {
            _isAetherSpeaking.value = false
            lastAetherText = currentAetherText
            lastAetherSpeakEndTime = System.currentTimeMillis()
            currentAetherText = ""
            if (_isLiveMode.value && !_isRecordingVoice.value && !_isLiveModePaused.value) {"""
content = content.replace(speak_old, speak_new)

# 3. Update isLikelyEcho
echo_old = """    private fun isLikelyEcho(recognizedText: String): Boolean {
        if (currentAetherText.isEmpty()) return false
        val normalRecognized = recognizedText.lowercase().replace(Regex("[^a-záéíóúñ0-9 ]"), "").trim()
        val normalSpoken = currentAetherText.lowercase().replace(Regex("[^a-záéíóúñ0-9 ]"), "").trim()"""

echo_new = """    private fun isLikelyEcho(recognizedText: String): Boolean {
        var textToCompare = currentAetherText
        if (textToCompare.isEmpty() && System.currentTimeMillis() - lastAetherSpeakEndTime < 3000) {
            textToCompare = lastAetherText
        }
        if (textToCompare.isEmpty()) return false
        
        val normalRecognized = recognizedText.lowercase().replace(Regex("[^a-záéíóúñ0-9 ]"), "").trim()
        val normalSpoken = textToCompare.lowercase().replace(Regex("[^a-záéíóúñ0-9 ]"), "").trim()"""

content = content.replace(echo_old, echo_new)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("Echo patched")
