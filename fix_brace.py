with open('app/src/main/java/com/example/core/AetherCoreService.kt', 'r') as f:
    content = f.read()

content = content.replace("private fun iniciarLatido() { {", "private fun iniciarLatido() {")

with open('app/src/main/java/com/example/core/AetherCoreService.kt', 'w') as f:
    f.write(content)
