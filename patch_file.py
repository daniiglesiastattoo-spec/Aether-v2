import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

old_logic = """                if (mimeType.startsWith("image/")) {
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

new_logic = """                if (mimeType.startsWith("image/") || mimeType.startsWith("video/") || mimeType.contains("pdf")) {
                    addMessage(Message(
                        text = "He adjuntado el archivo visual: $fileName. Por favor, analízalo.",
                        sender = Sender.USER,
                        fileUri = uri.toString()
                    ))
                    
                    try {
                        var swBitmap: android.graphics.Bitmap? = null
                        if (mimeType.startsWith("image/")) {
                            val bitmap = if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.P) {
                                android.graphics.ImageDecoder.decodeBitmap(android.graphics.ImageDecoder.createSource(context.contentResolver, uri))
                            } else {
                                android.provider.MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
                            }
                            swBitmap = bitmap.copy(android.graphics.Bitmap.Config.ARGB_8888, true)
                        } else if (mimeType.startsWith("video/")) {
                            val retriever = android.media.MediaMetadataRetriever()
                            context.contentResolver.openFileDescriptor(uri, "r")?.use { fd ->
                                retriever.setDataSource(fd.fileDescriptor)
                                swBitmap = retriever.getFrameAtTime(1000000, android.media.MediaMetadataRetriever.OPTION_CLOSEST_SYNC)
                                if (swBitmap == null) {
                                    swBitmap = retriever.getFrameAtTime(0, android.media.MediaMetadataRetriever.OPTION_CLOSEST_SYNC)
                                }
                            }
                            retriever.release()
                        } else if (mimeType.contains("pdf")) {
                            context.contentResolver.openFileDescriptor(uri, "r")?.use { fd ->
                                val pdfRenderer = android.graphics.pdf.PdfRenderer(fd)
                                if (pdfRenderer.pageCount > 0) {
                                    val page = pdfRenderer.openPage(0)
                                    val bitmap = android.graphics.Bitmap.createBitmap(page.width * 2, page.height * 2, android.graphics.Bitmap.Config.ARGB_8888)
                                    val canvas = android.graphics.Canvas(bitmap)
                                    canvas.drawColor(android.graphics.Color.WHITE)
                                    page.render(bitmap, null, null, android.graphics.pdf.PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                                    page.close()
                                    swBitmap = bitmap
                                }
                                pdfRenderer.close()
                            }
                        }

                        if (swBitmap != null) {
                            val isOnline = _connectionMode.value == ConnectionMode.ONLINE
                            val prompt = if (mimeType.startsWith("video/")) {
                                "Describe detalladamente la primera escena de este video y dime qué contiene."
                            } else if (mimeType.contains("pdf")) {
                                "Describe detalladamente la primera página de este documento PDF y dime qué contiene."
                            } else {
                                "Describe detalladamente esta imagen y dime qué contiene."
                            }
                            val responseText = generateGeminiVisionResponse(swBitmap!!, prompt, isOnline, fileName)
                            
                            addMessage(Message(
                                text = responseText,
                                sender = Sender.AETHER,
                                status = MessageStatus.VERIFIED
                            ))
                            
                            val cleanFileName = fileName.lowercase().substringBeforeLast(".")
                            com.example.LocalKnowledgeLibrary.addKnowledge(cleanFileName, responseText)
                        } else {
                            addMessage(Message(
                                text = "SISTEMA AETHER: No pude extraer información visual de $fileName.",
                                sender = Sender.AETHER,
                                status = MessageStatus.UNCERTAIN
                            ))
                        }
                    } catch (e: Exception) {
                        addMessage(Message(
                            text = "Error al procesar el archivo $fileName: ${e.message}",
                            sender = Sender.AETHER,
                            status = MessageStatus.UNCERTAIN
                        ))
                    }
                    return@launch
                } else if (mimeType.startsWith("audio/") || mimeType.contains("octet-stream") || mimeType.contains("zip")) {
                    addMessage(Message(
                        text = "SISTEMA: El archivo $fileName ($mimeType) ha sido recibido. Es un archivo binario/multimedia no soportado actualmente para procesamiento.",
                        sender = Sender.AETHER,
                        status = MessageStatus.VERIFIED
                    ))
                    return@launch
                }"""

content = content.replace(old_logic, new_logic)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("Updated handleRealFileAttachment logic for video and pdf")
