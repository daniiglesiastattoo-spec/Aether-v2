import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Pattern 1:
#                 _isAetherSpeaking.value = true
#                 voiceManager.speak(responseText, isOnlineMode = currentMode == ConnectionMode.ONLINE) {
#                     _isAetherSpeaking.value = false
#                     if (_isLiveMode.value) {
#                         startLiveModeListening()
#                     }
#                 }
pattern1 = r'_isAetherSpeaking\.value = true\s*voiceManager\.speak\(([^,]+),\s*isOnlineMode = (.*?)\) \{\s*_isAetherSpeaking\.value = false\s*if \(_isLiveMode\.value\)\s*(?:\{\s*startLiveModeListening\(\)\s*\}|startLiveModeListening\(\))\s*\}'

content = re.sub(pattern1, r'speakAndListen(\1, \2)', content)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)

print("Patch 3 applied")
