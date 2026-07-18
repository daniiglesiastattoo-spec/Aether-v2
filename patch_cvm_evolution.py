import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Add scanner instance if not present
if 'val evolutionScanner' not in content:
    content = content.replace(
        'private val reflexionEngine = com.example.manager.ReflexionEngine(context)',
        'private val reflexionEngine = com.example.manager.ReflexionEngine(context)\n    private val evolutionScanner = com.example.manager.EvolutionScanner(context)'
    )

old_instruction = """        val systemInstructionText = if (mode == ConnectionMode.ONLINE) {
            "$baseInstructionOnline\\n\\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState\\n\\n$veritasContext\\n$reflexionContext\\n\\nDIRECTIVA VERITAS: Siempre que el contexto de VERITAS contenga información sobre la consulta, DEBES usar esa información para verificar tus respuestas lógicas."
        } else {
            "$baseInstructionLocal\\n\\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState\\n\\n$veritasContext\\n$reflexionContext\\n\\nDIRECTIVA VERITAS: Siempre que el contexto de VERITAS contenga información sobre la consulta, DEBES usar esa información para verificar tus respuestas lógicas."
        }"""

new_instruction = """        val pendingProposals = evolutionScanner.getPendingProposalsPrompt()
        if (pendingProposals.isNotEmpty()) {
            evolutionScanner.markCommunicated()
        }
        val evolutionContext = if (pendingProposals.isNotEmpty()) "\\n\\n$pendingProposals" else ""

        val systemInstructionText = if (mode == ConnectionMode.ONLINE) {
            "$baseInstructionOnline\\n\\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState\\n\\n$veritasContext\\n$reflexionContext$evolutionContext\\n\\nDIRECTIVA VERITAS: Siempre que el contexto de VERITAS contenga información sobre la consulta, DEBES usar esa información para verificar tus respuestas lógicas."
        } else {
            "$baseInstructionLocal\\n\\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState\\n\\n$veritasContext\\n$reflexionContext$evolutionContext\\n\\nDIRECTIVA VERITAS: Siempre que el contexto de VERITAS contenga información sobre la consulta, DEBES usar esa información para verificar tus respuestas lógicas."
        }"""

content = content.replace(old_instruction, new_instruction)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)

print("Evolution integrated into ChatViewModel")
