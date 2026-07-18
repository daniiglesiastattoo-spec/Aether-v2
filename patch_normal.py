import re

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'r') as f:
    content = f.read()

# 1. Update TTS audio attributes to MEDIA
content = content.replace('.setUsage(android.media.AudioAttributes.USAGE_VOICE_COMMUNICATION)', '.setUsage(android.media.AudioAttributes.USAGE_MEDIA)')

# 2. Update setLiveMode to use normal media routing
old_set_live = """    override fun setLiveMode(isActive: Boolean) {
        val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
        if (isActive) {
            audioManager.mode = android.media.AudioManager.MODE_IN_COMMUNICATION
            audioManager.isSpeakerphoneOn = true // Altavoz principal (manos libres real)
        } else {
            audioManager.mode = android.media.AudioManager.MODE_NORMAL
            audioManager.isSpeakerphoneOn = false
        }
    }"""

new_set_live = """    override fun setLiveMode(isActive: Boolean) {
        val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
        // Volvemos a la vía normal (media) sin forzar modo comunicación
        audioManager.mode = android.media.AudioManager.MODE_NORMAL
        audioManager.isSpeakerphoneOn = false
    }"""

content = content.replace(old_set_live, new_set_live)

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'w') as f:
    f.write(content)
print("Normal audio routing patched")
