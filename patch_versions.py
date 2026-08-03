import re

with open('gradle/libs.versions.toml', 'r') as f:
    content = f.read()

# Update versions to latest 2026 ones (hypothetical or known latest)
content = re.sub(r'coreKtx = ".*?"', 'coreKtx = "1.18.0"', content)
content = re.sub(r'lifecycleRuntimeKtx = ".*?"', 'lifecycleRuntimeKtx = "2.8.7"', content)
content = re.sub(r'activityCompose = ".*?"', 'activityCompose = "1.10.1"', content)
content = re.sub(r'kotlin = ".*?"', 'kotlin = "2.2.10"', content)
content = re.sub(r'composeBom = ".*?"', 'composeBom = "2024.12.00"', content)

with open('gradle/libs.versions.toml', 'w') as f:
    f.write(content)
