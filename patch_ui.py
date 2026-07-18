import re

with open('app/src/main/java/com/example/MainActivity.kt', 'r') as f:
    content = f.read()

# Add import
if 'import androidx.compose.ui.platform.LocalFocusManager' not in content:
    content = content.replace('import androidx.compose.ui.platform.LocalContext', 'import androidx.compose.ui.platform.LocalContext\nimport androidx.compose.ui.platform.LocalFocusManager')

# Hide keyboard logic
effect_code = """
    val focusManager = LocalFocusManager.current
    androidx.compose.runtime.LaunchedEffect(isLiveMode) {
        if (isLiveMode) {
            keyboardController?.hide()
            focusManager.clearFocus()
        }
    }
    
    val filePickerLauncher"""

content = content.replace("    val filePickerLauncher", effect_code)

# Add isLiveModePaused to LiveModeOverlay
content = content.replace("fun LiveModeOverlay(\n    viewModel: ChatViewModel,\n    isAetherSpeaking: Boolean\n) {", "fun LiveModeOverlay(\n    viewModel: ChatViewModel,\n    isAetherSpeaking: Boolean\n) {\n    val isLiveModePaused by viewModel.isLiveModePaused.collectAsStateWithLifecycle()")

# Modify Status Text
status_text_old = """            Text(
                text = if (isAetherSpeaking) "AETHER ESTÁ HABLANDO..." else if (isRecordingVoice) "ESCUCHANDO..." else "LISTO",
                color = AccentCyan,"""
status_text_new = """            Text(
                text = if (isLiveModePaused) "PAUSADO" else if (isAetherSpeaking) "AETHER ESTÁ HABLANDO..." else if (isRecordingVoice) "ESCUCHANDO..." else "LISTO",
                color = if (isLiveModePaused) Color.Gray else AccentCyan,"""
content = content.replace(status_text_old, status_text_new)

# Add Pause Button next to Finalizar
buttons_old = """            Spacer(modifier = Modifier.height(30.dp))
            OutlinedButton(
                onClick = { viewModel.toggleLiveMode() },
                colors = ButtonDefaults.outlinedButtonColors(contentColor = StatusRed),
                border = androidx.compose.foundation.BorderStroke(1.dp, StatusRed)
            ) {
                Icon(Icons.Default.Close, contentDescription = "Cerrar Live Mode")
                Spacer(modifier = Modifier.width(8.dp))
                Text("FINALIZAR")
            }"""
buttons_new = """            Spacer(modifier = Modifier.height(30.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                OutlinedButton(
                    onClick = { viewModel.toggleLiveModePause() },
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = if (isLiveModePaused) AccentCyan else Color.White),
                    border = androidx.compose.foundation.BorderStroke(1.dp, if (isLiveModePaused) AccentCyan else Color.White)
                ) {
                    Icon(if (isLiveModePaused) Icons.Default.PlayArrow else Icons.Default.Pause, contentDescription = "Pausa")
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(if (isLiveModePaused) "REANUDAR" else "PAUSAR")
                }

                OutlinedButton(
                    onClick = { viewModel.toggleLiveMode() },
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = StatusRed),
                    border = androidx.compose.foundation.BorderStroke(1.dp, StatusRed)
                ) {
                    Icon(Icons.Default.Close, contentDescription = "Cerrar Live Mode")
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("FINALIZAR")
                }
            }"""
content = content.replace(buttons_old, buttons_new)

with open('app/src/main/java/com/example/MainActivity.kt', 'w') as f:
    f.write(content)

print("UI Patch applied")
