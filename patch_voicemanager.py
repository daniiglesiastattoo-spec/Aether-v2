import re

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'r') as f:
    content = f.read()

# 1. Revert speak method to v119 config
old_speak = """        // Cinematic voice: lower pitch, slightly slower rate for a more human/natural feel
        val pitch = 0.65f
        val rate = 0.95f
        textToSpeech?.setPitch(pitch)
        textToSpeech?.setSpeechRate(rate)"""

new_speak = """        if (isOnlineMode) {
            textToSpeech?.setPitch(0.8f) 
            textToSpeech?.setSpeechRate(1.2f) 
        } else {
            textToSpeech?.setPitch(0.8f) 
            textToSpeech?.setSpeechRate(1.2f) 
        }"""
content = content.replace(old_speak, new_speak)

# 2. Revert startListening muting logic to v119 config
old_start_listening = """            val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as android.media.AudioManager
            
            // Mute to avoid the "beep" sound when SpeechRecognizer starts
            try {
                audioManager.adjustStreamVolume(android.media.AudioManager.STREAM_NOTIFICATION, android.media.AudioManager.ADJUST_MUTE, 0)
                audioManager.adjustStreamVolume(android.media.AudioManager.STREAM_SYSTEM, android.media.AudioManager.ADJUST_MUTE, 0)
                // We also mute MUSIC briefly because some devices route the beep there
                audioManager.adjustStreamVolume(android.media.AudioManager.STREAM_MUSIC, android.media.AudioManager.ADJUST_MUTE, 0)
            } catch (e: Exception) {}

            speechRecognizer?.setRecognitionListener(object : RecognitionListener {
                private fun unmute() {
                    try {
                        audioManager.adjustStreamVolume(android.media.AudioManager.STREAM_NOTIFICATION, android.media.AudioManager.ADJUST_UNMUTE, 0)
                        audioManager.adjustStreamVolume(android.media.AudioManager.STREAM_SYSTEM, android.media.AudioManager.ADJUST_UNMUTE, 0)
                        audioManager.adjustStreamVolume(android.media.AudioManager.STREAM_MUSIC, android.media.AudioManager.ADJUST_UNMUTE, 0)
                    } catch (e: Exception) {}
                }

                override fun onReadyForSpeech(params: Bundle?) {
                    unmute()
                }"""
                
new_start_listening = """            speechRecognizer?.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {}"""
content = content.replace(old_start_listening, new_start_listening)


old_on_error = """                override fun onError(error: Int) {
                    unmute()
                    val errorMsg = when(error) {"""
new_on_error = """                override fun onError(error: Int) {
                    val errorMsg = when(error) {"""
content = content.replace(old_on_error, new_on_error)


old_on_results = """                override fun onResults(results: Bundle?) {
                    unmute()
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)"""
new_on_results = """                override fun onResults(results: Bundle?) {
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)"""
content = content.replace(old_on_results, new_on_results)


# 3. Revert interruption sensitivity to v119 config
old_interrupt = """                        // Solo interrumpir si de verdad ha reconocido alguna palabra (baja sensibilidad)
                        // Mayor sensibilidad para poder interrumpir más rápido
                        if (text.length > 2) {
                            mainHandler.post { onSpeechDetected(text) }
                        }"""
new_interrupt = """                        // Solo interrumpir si de verdad ha reconocido alguna palabra (baja sensibilidad)
                        // Solo interrumpir si la frase parcial es significativa
                        if (text.length > 5 && text.split(" ").size >= 2) {
                            mainHandler.post { onSpeechDetected(text) }
                        }"""
content = content.replace(old_interrupt, new_interrupt)

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'w') as f:
    f.write(content)
print("VoiceManager reverted to v119 config")
