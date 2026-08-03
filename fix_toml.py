import re

with open('gradle/libs.versions.toml', 'r') as f:
    content = f.read()

content = content.replace('[versions]\nwork = "2.9.0"\n[versions]', '[versions]\nwork = "2.9.0"')

with open('gradle/libs.versions.toml', 'w') as f:
    f.write(content)
