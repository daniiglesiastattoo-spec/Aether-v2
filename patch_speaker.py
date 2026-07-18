import re

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'r') as f:
    content = f.read()

old_code = """    override fun setLiveMode(isActive: Boolean) {
        val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
        if (isActive) {
            audioManager.mode = android.media.AudioManager.MODE_IN_COMMUNICATION
            audioManager.isSpeakerphoneOn = false // Altavoz secundario (earpiece)
        } else {
            audioManager.mode = android.media.AudioManager.MODE_NORMAL
            audioManager.isSpeakerphoneOn = false
        }
    }"""

new_code = """    override fun setLiveMode(isActive: Boolean) {
        val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
        if (isActive) {
            audioManager.mode = android.media.AudioManager.MODE_IN_COMMUNICATION
            audioManager.isSpeakerphoneOn = true // Altavoz principal (manos libres real)
        } else {
            audioManager.mode = android.media.AudioManager.MODE_NORMAL
            audioManager.isSpeakerphoneOn = false
        }
    }"""

content = content.replace(old_code, new_code)

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'w') as f:
    f.write(content)
print("Speakerphone patched")
