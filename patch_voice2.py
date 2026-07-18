import re

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'r') as f:
    content = f.read()

# Add VOICE_COMMUNICATION source to intent to enable AEC (Acoustic Echo Cancellation)
intent_old = """            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES")
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            }"""
            
intent_new = """            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "es-ES")
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
                // Use VOICE_COMMUNICATION for hardware Acoustic Echo Cancellation
                putExtra("android.speech.extra.AUDIO_SOURCE", android.media.MediaRecorder.AudioSource.VOICE_COMMUNICATION)
            }"""
content = content.replace(intent_old, intent_new)

# Make partial results even less sensitive to avoid self-interruption (e.g., length > 4 or more words)
partial_old = """                        if (text.length > 1) {
                            mainHandler.post { onSpeechDetected() }
                        }"""
partial_new = """                        // Solo interrumpir si la frase parcial es significativa
                        if (text.length > 5 && text.split(" ").size >= 2) {
                            mainHandler.post { onSpeechDetected() }
                        }"""
content = content.replace(partial_old, partial_new)

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'w') as f:
    f.write(content)

print("VoiceManager patched with AEC")
