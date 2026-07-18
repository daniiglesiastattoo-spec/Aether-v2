import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

old_code = """                            status = MessageStatus.UNCERTAIN
                        ))
                    
                    _curiosity.value = minOf(1.0f, _curiosity.value + 0.25f)"""

new_code = """                            status = MessageStatus.UNCERTAIN
                        ))
                    }
                    _curiosity.value = minOf(1.0f, _curiosity.value + 0.25f)"""

content = content.replace(old_code, new_code)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("Fixed missing bracket")
