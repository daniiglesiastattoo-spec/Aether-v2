with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

dl_ui = """
                        if (dlStatus == "DOWNLOADING") {
                            Text(
                                text = "DL: ${dlProgress.toInt()}%",
                                color = StatusGreen,
                                fontSize = 9.sp,
                                modifier = Modifier.padding(end = 4.dp)
                            )
                        }
"""
target = "Text(\n                            text = activeEngine,"
if "DL:" not in content:
    content = content.replace(target, dl_ui + target)
    with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
        f.write(content)
        print("Patched UI dl progress")
