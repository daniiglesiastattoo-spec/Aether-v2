import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

content = content.replace("processUserInput(resultText)", "sendMessage(resultText)")

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)

print("Patch 4 applied")
