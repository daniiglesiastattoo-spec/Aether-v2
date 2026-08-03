import re
with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

if 'implementation(libs.androidx.work)' not in content:
    content = re.sub(r'implementation\(libs.androidx.room.runtime\)', r'implementation(libs.androidx.room.runtime)\n  implementation(libs.androidx.work)', content)
    with open('app/build.gradle.kts', 'w') as f:
        f.write(content)
