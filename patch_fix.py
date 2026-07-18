with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "_isLiveModePaused = MutableStateFlow(false)" in line:
        new_lines.append(line)
        new_lines.append("    val isLiveModePaused: StateFlow<Boolean> = _isLiveModePaused.asStateFlow()\n")
        new_lines.append("\n")
        new_lines.append("    private val _isRecordingVoice = MutableStateFlow(false)\n")
        new_lines.append("    val isRecordingVoice: StateFlow<Boolean> = _isRecordingVoice.asStateFlow()\n")
        new_lines.append("    private var currentAetherText: String = \"\"\n")
        skip = True
    elif skip and "_isAetherSpeaking = MutableStateFlow(false)" in line:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.writelines(new_lines)
