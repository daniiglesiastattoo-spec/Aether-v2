import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Replace the binary file check
old_binary_check = """                if (mimeType.startsWith("image/") || mimeType.startsWith("video/") || mimeType.startsWith("audio/") || mimeType.contains("pdf") || mimeType.contains("octet-stream") || mimeType.contains("zip")) {
                    addMessage(Message(
                        text = "SISTEMA: El archivo $fileName ($mimeType) ha sido recibido. Es un archivo binario/multimedia. Procesamiento bimodal en desarrollo.",
                        sender = Sender.AETHER,
                        status = MessageStatus.VERIFIED
                    ))
                    return@launch
                }"""

new_binary_check = """                if (mimeType.startsWith("image/")) {
                    addMessage(Message(
                        text = "He adjuntado la imagen: $fileName. Por favor, analízala.",
                        sender = Sender.USER,
                        fileUri = uri.toString()
                    ))
                    
                    try {
                        val bitmap = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                            android.graphics.ImageDecoder.decodeBitmap(android.graphics.ImageDecoder.createSource(context.contentResolver, uri))
                        } else {
                            android.provider.MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
                        }
                        
                        // Convert hardware bitmap to software for processing if needed
                        val swBitmap = bitmap.copy(android.graphics.Bitmap.Config.ARGB_8888, true)
                        
                        val isOnline = _connectionMode.value == ConnectionMode.ONLINE
                        val responseText = generateGeminiVisionResponse(swBitmap, "Describe detalladamente esta imagen y dime qué contiene.", isOnline, fileName)
                        
                        addMessage(Message(
                            text = responseText,
                            sender = Sender.AETHER,
                            status = MessageStatus.VERIFIED
                        ))
                        
                        val cleanFileName = fileName.lowercase().substringBeforeLast(".")
                        com.example.LocalKnowledgeLibrary.addKnowledge(cleanFileName, responseText)
                        
                    } catch (e: Exception) {
                        addMessage(Message(
                            text = "Error al procesar la imagen $fileName: ${e.message}",
                            sender = Sender.AETHER,
                            status = MessageStatus.UNCERTAIN
                        ))
                    }
                    return@launch
                } else if (mimeType.startsWith("video/") || mimeType.startsWith("audio/") || mimeType.contains("pdf") || mimeType.contains("octet-stream") || mimeType.contains("zip")) {
                    addMessage(Message(
                        text = "SISTEMA: El archivo $fileName ($mimeType) ha sido recibido. Es un archivo binario/multimedia no soportado actualmente para visión directa.",
                        sender = Sender.AETHER,
                        status = MessageStatus.VERIFIED
                    ))
                    return@launch
                }"""

content = content.replace(old_binary_check, new_binary_check)


old_text_check = """                    val prompt = "Contenido del archivo $fileName:\\n\\n[...]\\n\\nPor favor, confírmame que lo has procesado."
                    addMessage(Message(
                        text = prompt,
                        sender = Sender.USER,
                        fileUri = uri.toString()
                    ))
                    
                    val cleanFileName = fileName.lowercase().substringBeforeLast(".")
                    com.example.LocalKnowledgeLibrary.addKnowledge(cleanFileName, fileContent)
                    
                    val responseText = "SISTEMA AETHER: He interiorizado el documento '$fileName'. He indexado sus contenidos bajo el concepto clave '$cleanFileName' en mi base de conocimientos locales. Estará disponible para futuras referencias en mis reflexiones heurísticas."
                    
                    addMessage(Message(
                        text = responseText,
                        sender = Sender.AETHER,
                        status = MessageStatus.VERIFIED
                    ))"""

new_text_check = """                    val prompt = "Contenido del archivo $fileName:\\n\\n$fileContent"
                    addMessage(Message(
                        text = "He adjuntado el archivo: $fileName. Analiza su contenido y dame un resumen o descripción de lo que trata.",
                        sender = Sender.USER,
                        fileUri = uri.toString()
                    ))
                    
                    val cleanFileName = fileName.lowercase().substringBeforeLast(".")
                    com.example.LocalKnowledgeLibrary.addKnowledge(cleanFileName, fileContent)
                    
                    // We send a request to generate a summary
                    _isTyping.value = true
                    try {
                        val isOnline = _connectionMode.value == ConnectionMode.ONLINE
                        val summaryPrompt = "El usuario acaba de subir un archivo llamado '$fileName' con el siguiente contenido:\\n\\n$fileContent\\n\\nProporciona una descripción clara y detallada de lo que contiene el archivo."
                        val responseText = if (isOnline) {
                            val groqApiKey = BuildConfig.GROQ_API_KEY
                            if (groqApiKey.isNotBlank() && groqApiKey != "MY_GROQ_API_KEY") {
                                val groqMessages = listOf(
                                    com.example.manager.GroqMessage(role = "system", content = "Eres AETHER. Resume el contenido del archivo proporcionado."),
                                    com.example.manager.GroqMessage(role = "user", content = summaryPrompt)
                                )
                                val req = com.example.manager.GroqRequest(messages = groqMessages)
                                val resp = com.example.manager.GroqRetrofitClient.service.generateContent("Bearer $groqApiKey", req)
                                resp.choices.firstOrNull()?.message?.content ?: "SISTEMA AETHER: He indexado el contenido de '$fileName'."
                            } else {
                                "SISTEMA AETHER: (Modo Online Sin Clave) He interiorizado '$fileName'."
                            }
                        } else {
                            "SISTEMA AETHER: He interiorizado el documento '$fileName' en modo local. Lo he indexado para futuras referencias."
                        }
                        
                        addMessage(Message(
                            text = responseText,
                            sender = Sender.AETHER,
                            status = MessageStatus.VERIFIED
                        ))
                    } catch (e: Exception) {
                        addMessage(Message(
                            text = "SISTEMA AETHER: He interiorizado el documento '$fileName', pero ocurrió un error al resumirlo: ${e.message}",
                            sender = Sender.AETHER,
                            status = MessageStatus.UNCERTAIN
                        ))
                    } finally {
                        _isTyping.value = false
                    }"""

content = content.replace(old_text_check, new_text_check)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("Updated handleRealFileAttachment in ChatViewModel.kt")
