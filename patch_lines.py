with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    lines = f.readlines()

# We need to replace lines 619 (inclusive) down to where the `} else {` of `currentMode == ConnectionMode.ONLINE` ends.
# Basically replacing from `} else if (currentMode == ConnectionMode.LOCAL) {` to the end of `sendMessage`'s if-else block.
# Let's just find `} else if (currentMode == ConnectionMode.LOCAL) {` and replace everything until `viewModelScope.launch {` inside `verifyResponseWithVeritas` or similar.

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "} else if (currentMode == ConnectionMode.LOCAL) {" in line:
        start_idx = i
    if start_idx != -1 and i > start_idx + 10:
        if "    private fun verifyResponseWithVeritas(" in line:
            end_idx = i - 1
            break

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx]
    
    new_block = """            } else {
                val responseText = generateHeuristicResponse(text, currentMode)
                val isVerified = verifyResponseWithVeritas(responseText, text)
                
                var finalText = responseText
                val saveNameRegex = "<SAVE_NAME:\\\\s*(.+?)>".toRegex(RegexOption.IGNORE_CASE)
                val nameMatch = saveNameRegex.find(finalText)
                if (nameMatch != null) {
                    userName = nameMatch.groupValues[1].trim()
                    prefs.edit().putString("USER_NAME", userName).apply()
                    finalText = finalText.replace(nameMatch.value, "").trim()
                    _nodes.value = _nodes.value + com.example.model.NodeItem("Usuario: $userName", "entity", 1.8f)
                }

                val aetherMsg = Message(
                    text = finalText,
                    sender = Sender.AETHER,
                    status = isVerified
                )
                addMessage(aetherMsg)
                speakAndListen(finalText, currentMode == ConnectionMode.ONLINE)
            }
        }
    }
"""
    new_lines.append(new_block)
    new_lines.extend(lines[end_idx:])
    
    with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
        f.writelines(new_lines)
    print("Patched sendMessage lines")
else:
    print("Could not find boundaries")
