import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

match = re.search(r'fun sendMessage.*?\{.*?(?=fun startLiveModeListening)', content, re.DOTALL)
if match:
    # Print the last 1500 chars of sendMessage
    text = match.group(0)
    print(text[-1500:]) 
