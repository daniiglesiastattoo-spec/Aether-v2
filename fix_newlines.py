with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

bad_str = 'LOCAL:\n\n$localFallback"'
good_str = 'LOCAL:\\n\\n$localFallback"'

if bad_str in content:
    content = content.replace(bad_str, good_str)
    with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
        f.write(content)
        print("Fixed newlines")
else:
    print("Not found")

