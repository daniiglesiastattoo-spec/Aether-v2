import re
with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

# We find the 'else if (currentMode == ConnectionMode.LOCAL) {'
old_block = """            } else if (currentMode == ConnectionMode.LOCAL) {
                if ((com.example.manager.LocalLlmEngine.state.value == com.example.manager.LocalLlmEngine.State.READY || com.example.manager.LocalLlmEngine.state.value == com.example.manager.LocalLlmEngine.State.LOADED)) {
                    val nameInst = if (userName != null) "El usuario se llama $userName. Dirígete a él como tal." else "NO sabes el nombre del usuario. Pregúntale cómo se llama. Si te lo dice, añade <SAVE_NAME: SuNombre> al final de la respuesta."
                    val baseInstructionLocal = "Eres AETHER, asistente IA local privado. Respondes breve y preciso. $nameInst"
                    val recentHistory = _allDbMessages.value.filter { 
                        !it.text.startsWith("FOTO CAPT") && !it.text.startsWith("SISTEMA:")
                    }.takeLast(6)
                    val historyPrompt = recentHistory.joinToString("\n") { (if(it.sender == Sender.USER) "USER: " else "AETHER: ") + it.text }
                    val fullPrompt = "$baseInstructionLocal\\n\\nConversación:\\n$historyPrompt\\nUSER: $text\\nAETHER:"
                    
                    val streamingMsgId = java.util.UUID.randomUUID().toString()
                    val initialMsg = Message(id = streamingMsgId, text = "Cargando modelo local...", sender = Sender.AETHER, status = MessageStatus.UNCERTAIN)
                    _messages.value = _messages.value + initialMsg
                    
                    val responseBuilder = java.lang.StringBuilder()
                    
                    try {
                        com.example.manager.LocalLlmEngine.generateStreaming(
                            context = context,
                            prompt = fullPrompt,
                            onPartial = { token ->
                                responseBuilder.append(token)
                                val currentText = responseBuilder.toString()
                                _messages.value = _messages.value.map { 
                                    if (it.id == streamingMsgId) it.copy(text = currentText) else it 
                                }
                            },
                            onDone = {
                                var finalText = responseBuilder.toString()
                                val saveNameRegex = "<SAVE_NAME:\\s*(.+?)>".toRegex(RegexOption.IGNORE_CASE)
                                val matchResult = saveNameRegex.find(finalText)
                                if (matchResult != null) {
                                    userName = matchResult.groupValues[1].trim()
                                    prefs.edit().putString("USER_NAME", userName).apply()
                                    finalText = finalText.replace(matchResult.value, "").trim()
                                    _nodes.value = _nodes.value + com.example.model.NodeItem("Usuario: $userName", "entity", 1.8f)
                                }
                                val isVerified = verifyResponseWithVeritas(finalText, text)
                                val finalMsg = initialMsg.copy(text = finalText, status = isVerified)
                                _messages.value = _messages.value.map { 
                                    if (it.id == streamingMsgId) finalMsg else it 
                                }
                                
                                viewModelScope.launch {
                                    _allDbMessages.value = _allDbMessages.value + finalMsg.copy(id = java.util.UUID.randomUUID().toString())
                                    db.messageDao().insertMessage(finalMsg.copy(id = java.util.UUID.randomUUID().toString()))
                                    updateEmotionalStateAndMentalModel(text)
                                    parseAgentsIntent(text)
                                }
                                speakAndListen(finalText, false)
                            },
                            onError = { errorMsg ->
                                _messages.value = _messages.value.map { 
                                    if (it.id == streamingMsgId) it.copy(text = "Error del motor local: $errorMsg", status = MessageStatus.REJECTED) else it 
                                }
                            }
                        )
                    } catch (e: Exception) {
                        _messages.value = _messages.value.map { 
                            if (it.id == streamingMsgId) it.copy(text = "Crash del motor local: ${e.message}", status = MessageStatus.REJECTED) else it 
                        }
                    }
                } else {
                    val responseText = generateHeuristicResponse(text, currentMode)
                    val isVerified = verifyResponseWithVeritas(responseText, text)
                    val aetherMsg = Message(
                        text = responseText,
                        sender = Sender.AETHER,
                        status = isVerified
                    )
                    addMessage(aetherMsg)
                    speakAndListen(responseText, currentMode == ConnectionMode.ONLINE)
                }
            } else {
                val responseText = generateHeuristicResponse(text, currentMode)
                val isVerified = verifyResponseWithVeritas(responseText, text)
                val aetherMsg = Message(
                    text = responseText,
                    sender = Sender.AETHER,
                    status = isVerified
                )
                addMessage(aetherMsg)
                speakAndListen(responseText, currentMode == ConnectionMode.ONLINE)
            }"""

new_block = """            } else {
                val responseText = generateHeuristicResponse(text, currentMode)
                val isVerified = verifyResponseWithVeritas(responseText, text)
                
                var finalText = responseText
                val saveNameRegex = "<SAVE_NAME:\\s*(.+?)>".toRegex(RegexOption.IGNORE_CASE)
                val nameMatch = saveNameRegex.find(finalText)
                if (nameMatch != null) {
                    userName = nameMatch.groupValues[1].trim()
                    prefs.edit().putString("USER_NAME", userName).apply()
                    finalText = finalText.replace(nameMatch.value, "").trim()
                    _nodes.value = _nodes.value + com.example.model.NodeItem("Usuario: $userName", "entity", 1.8f)
                }

                val aetherMsg = Message(
                    text = finalText,
                    sender = Sender.AETHER,
                    status = isVerified
                )
                addMessage(aetherMsg)
                speakAndListen(finalText, currentMode == ConnectionMode.ONLINE)
            }"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
        f.write(content)
        print("Patched sendMessage")
else:
    print("Not found old_block")
