import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Replace the direct call in onResult for isLikelyEcho
echo_block_old = """                if (isLikelyEcho(resultText)) {
                    // Es eco, lo ignoramos y seguimos escuchando
                    if (_isLiveMode.value && !_isLiveModePaused.value) {
                        startLiveModeListening()
                    }
                }"""

echo_block_new = """                if (isLikelyEcho(resultText)) {
                    // Es eco, lo ignoramos y seguimos escuchando
                    if (_isLiveMode.value && !_isLiveModePaused.value) {
                        viewModelScope.launch {
                            kotlinx.coroutines.delay(300)
                            startLiveModeListening()
                        }
                    }
                }"""
content = content.replace(echo_block_old, echo_block_new)

# Replace the direct call in onError
error_block_old = """                // Auto-retry in live mode on silent errors
                if (error == "No se entendió" || error == "Silencio corto" || error == "Vacío") {
                    startLiveModeListening()
                }"""

error_block_new = """                // Auto-retry in live mode on silent errors
                if (error == "No se entendió" || error == "Silencio corto" || error == "Vacío") {
                    viewModelScope.launch {
                        kotlinx.coroutines.delay(500)
                        startLiveModeListening()
                    }
                }"""
content = content.replace(error_block_old, error_block_new)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("Live mode patched")
