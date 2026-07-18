import re

with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

content = re.sub(r'versionCode = 130', 'versionCode = 131', content)
content = re.sub(r'versionName = "130.0"', 'versionName = "131.0"', content)

with open('app/build.gradle.kts', 'w') as f:
    f.write(content)
print("Version updated to 131")
