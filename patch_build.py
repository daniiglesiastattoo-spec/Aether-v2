import re

with open('app/build.gradle.kts', 'r') as f:
    content = f.read()

dep = "  implementation(\"com.google.mediapipe:tasks-vision:0.10.14\")\n"
content = content.replace('  implementation(libs.androidx.camera.view)\n', '  implementation(libs.androidx.camera.view)\n' + dep)

with open('app/build.gradle.kts', 'w') as f:
    f.write(content)
