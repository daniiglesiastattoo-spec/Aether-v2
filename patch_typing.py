import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

content = content.replace("                    _isTyping.value = true\n", "")
content = content.replace("                    } finally {\n                        _isTyping.value = false\n", "                    } finally {")

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("Removed _isTyping")
