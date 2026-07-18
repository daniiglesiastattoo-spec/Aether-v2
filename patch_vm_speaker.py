import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# toggleLiveMode
toggle_old = """    fun toggleLiveMode() {
        val newState = !_isLiveMode.value
        _isLiveMode.value = newState
        
        if (newState) {"""
toggle_new = """    fun toggleLiveMode() {
        val newState = !_isLiveMode.value
        _isLiveMode.value = newState
        
        voiceManager.setLiveMode(newState)
        
        if (newState) {"""
content = content.replace(toggle_old, toggle_new)

# if live mode deactivated on error
error_old = """                    _messages.value = _messages.value + Message(
                        text = "MÚLTIPLES ERRORES EN SISTEMA VOCAL: $error. Live Mode desactivado.",
                        sender = Sender.AETHER,
                        status = MessageStatus.UNCERTAIN
                    )
                    _isLiveMode.value = false
                }"""
error_new = """                    _messages.value = _messages.value + Message(
                        text = "MÚLTIPLES ERRORES EN SISTEMA VOCAL: $error. Live Mode desactivado.",
                        sender = Sender.AETHER,
                        status = MessageStatus.UNCERTAIN
                    )
                    _isLiveMode.value = false
                    voiceManager.setLiveMode(false)
                }"""
content = content.replace(error_old, error_new)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("ChatViewModel updated for speakerphone")
