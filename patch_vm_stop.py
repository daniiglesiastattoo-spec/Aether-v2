import re

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'r') as f:
    content = f.read()

old_listener = """        textToSpeech?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}
            override fun onDone(utteranceId: String?) { 
                mainHandler.post { onComplete() }
            }
            @Deprecated("Deprecated in Java", ReplaceWith("onComplete()"))
            override fun onError(utteranceId: String?) {
                mainHandler.post { onComplete() }
            }
        })"""

new_listener = """        textToSpeech?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}
            override fun onDone(utteranceId: String?) { 
                mainHandler.post { onComplete() }
            }
            @Deprecated("Deprecated in Java", ReplaceWith("onComplete()"))
            override fun onError(utteranceId: String?) {
                mainHandler.post { onComplete() }
            }
            override fun onStop(utteranceId: String?, interrupted: Boolean) {
                mainHandler.post { onComplete() }
            }
        })"""

content = content.replace(old_listener, new_listener)

with open('app/src/main/java/com/example/manager/VoiceManager.kt', 'w') as f:
    f.write(content)
print("VoiceManager TTS listener patched")
