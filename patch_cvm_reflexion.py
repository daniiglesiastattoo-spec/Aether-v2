import re

with open('app/src/main/java/com/example/ChatViewModel.kt', 'r') as f:
    content = f.read()

# Add reflexionEngine
engine_decl = '    private val reflexionEngine = com.example.manager.ReflexionEngine(context)'
if engine_decl not in content:
    content = content.replace('    private val _messages = MutableStateFlow<List<Message>>(emptyList())', engine_decl + '\n    private val _messages = MutableStateFlow<List<Message>>(emptyList())')

# Add reflexion trigger in sendMessage
send_msg_start = '        addMessage(userMsg)'
if 'reflexionEngine.reflexionar()' not in content:
    content = content.replace(send_msg_start, send_msg_start + '\n\n        viewModelScope.launch { reflexionEngine.reflexionar() }')

# Add reflexionContext to generateSciFiResponse
sci_fi = '        val veritasContext = if (knowledgeMatches.isNotEmpty()) {'
if 'val reflexionContext' not in content:
    content = content.replace(sci_fi, '        val reflexionContext = reflexionEngine.conclusionesParaPrompt(prompt)\n' + sci_fi)

# Inject reflexionContext into systemInstructionText
sys_online = '            "$baseInstructionOnline\\n\\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState\\n\\n$veritasContext\\n\\nDIRECTIVA VERITAS:'
if 'reflexionContext' in sys_online:
    pass
else:
    sys_online_new = sys_online.replace('$veritasContext', '$veritasContext\\n$reflexionContext')
    content = content.replace(sys_online, sys_online_new)

sys_local = '            "$baseInstructionLocal\\n\\nTU MODELO DE MUNDO ACTUAL (Conceptos Clave Analizados Recientemente): $worldModelState\\n\\n$veritasContext\\n\\nDIRECTIVA VERITAS:'
if 'reflexionContext' in sys_local:
    pass
else:
    sys_local_new = sys_local.replace('$veritasContext', '$veritasContext\\n$reflexionContext')
    content = content.replace(sys_local, sys_local_new)

with open('app/src/main/java/com/example/ChatViewModel.kt', 'w') as f:
    f.write(content)
print("ChatViewModel patched for ReflexionEngine")
