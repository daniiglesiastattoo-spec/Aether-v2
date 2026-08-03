import re

with open('gradle/libs.versions.toml', 'r') as f:
    content = f.read()

content = content.replace('androidx-work = { group = "androidx.work", name = "work-runtime-ktx", version.ref = "work" }\n', '')
content = content.replace('androidx-work = { group = "androidx.work", name = "work-runtime-ktx", version.ref = "work" }', '')

# Insert under [libraries]
content = content.replace('[libraries]', '[libraries]\nandroidx-work = { group = "androidx.work", name = "work-runtime-ktx", version.ref = "work" }')

with open('gradle/libs.versions.toml', 'w') as f:
    f.write(content)
