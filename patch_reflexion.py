with open('app/src/main/java/com/example/manager/ReflexionEngine.kt', 'r') as f:
    content = f.read()

content = content.replace(
    '        val allMessages = db.messageDao().getAllMessages().firstOrNull() ?: emptyList()',
    '        // Llamar a EvolutionScanner (asíncronamente o aquí)\n        try {\n            val scanner = EvolutionScanner(context)\n            scanner.runScan()\n        } catch (e: Exception) {\n            Log.e(TAG, "Error en EvolutionScanner", e)\n        }\n\n        val allMessages = db.messageDao().getAllMessages().firstOrNull() ?: emptyList()'
)

with open('app/src/main/java/com/example/manager/ReflexionEngine.kt', 'w') as f:
    f.write(content)
