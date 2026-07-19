import re

with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

content = re.sub(r'versionCode = \d+', 'versionCode = 140', content)
content = re.sub(r'versionName = "\d+\.\d+"', 'versionName = "140.0"', content)

with open('app/build.gradle.kts', 'w') as f:
    f.write(content)
print("Version updated to 140")
