import re
with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

# Add LlmRouter.activeEngine to MainActivity
if "val activeEngine =" not in content:
    content = content.replace(
        "val connectionMode by viewModel.connectionMode.collectAsStateWithLifecycle()",
        "val connectionMode by viewModel.connectionMode.collectAsStateWithLifecycle()\n    val activeEngine by com.example.manager.LlmRouter.activeEngine.collectAsStateWithLifecycle()"
    )

old_ui = """                        IconButton(
                            onClick = {
                                viewModel.toggleConnectionMode()
                                Toast.makeText(
                                    context,
                                    "Conmutado a: ${if (connectionMode == ConnectionMode.LOCAL) "Gemini Online" else "Local Native"}",
                                    Toast.LENGTH_SHORT
                                ).show()
                            },
                            modifier = Modifier
                                .size(32.dp)
                                .background(AccentCyan.copy(alpha = 0.08f), RoundedCornerShape(6.dp))
                                .border(0.5.dp, AccentCyan.copy(alpha = 0.3f), RoundedCornerShape(6.dp))
                        ) {
                            Icon(
                                imageVector = if (connectionMode == ConnectionMode.LOCAL) Icons.Default.Smartphone else Icons.Default.Cloud,
                                contentDescription = "Mode Status",
                                tint = AccentCyan,
                                modifier = Modifier.size(16.dp)
                            )
                        }"""

new_ui = """                        Text(
                            text = activeEngine,
                            color = AccentCyan,
                            fontSize = 9.sp,
                            modifier = Modifier.padding(end = 4.dp)
                        )
                        IconButton(
                            onClick = {
                                viewModel.toggleConnectionMode()
                                Toast.makeText(
                                    context,
                                    "Preferencia conmutada a: ${if (connectionMode == ConnectionMode.LOCAL) "ONLINE" else "LOCAL"}",
                                    Toast.LENGTH_SHORT
                                ).show()
                            },
                            modifier = Modifier
                                .size(32.dp)
                                .background(AccentCyan.copy(alpha = 0.08f), RoundedCornerShape(6.dp))
                                .border(0.5.dp, AccentCyan.copy(alpha = 0.3f), RoundedCornerShape(6.dp))
                        ) {
                            Icon(
                                imageVector = if (connectionMode == ConnectionMode.LOCAL) Icons.Default.Smartphone else Icons.Default.Cloud,
                                contentDescription = "Mode Status",
                                tint = AccentCyan,
                                modifier = Modifier.size(16.dp)
                            )
                        }"""

content = content.replace(old_ui, new_ui)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
    print("Patched MainActivity UI")
