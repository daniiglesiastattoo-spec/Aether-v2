import re

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'r') as f:
    content = f.read()

# Add AudioAttributes to TTS so that it is recognized as media or communication for AEC
tts_init_old = """    init {
        textToSpeech = TextToSpeech(context) { status ->"""
tts_init_new = """    init {
        textToSpeech = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val audioAttributes = android.media.AudioAttributes.Builder()
                    .setUsage(android.media.AudioAttributes.USAGE_VOICE_COMMUNICATION)
                    .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
                textToSpeech?.setAudioAttributes(audioAttributes)
            }"""
            
if "setAudioAttributes" not in content:
    content = content.replace(tts_init_old, tts_init_new)

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'w') as f:
    f.write(content)
print("TTS Audio attributes patched")
