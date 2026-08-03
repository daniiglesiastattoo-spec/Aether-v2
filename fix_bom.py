import re

with open('gradle/libs.versions.toml', 'r') as f:
    content = f.read()

content = content.replace('composeBom = "2024.12.00"', 'composeBom = "2024.09.00"')

with open('gradle/libs.versions.toml', 'w') as f:
    f.write(content)
