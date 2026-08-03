import re

with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

content = re.sub(r'versionCode = 140', 'versionCode = 141', content)
content = re.sub(r'versionName = "140.0"', 'versionName = "141.0"', content)

with open('app/build.gradle.kts', 'w') as f:
    f.write(content)
