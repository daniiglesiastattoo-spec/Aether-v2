with open("app/src/main/java/com/example/ChatViewModel.kt", "r") as f:
    content = f.read()

bad_str = '                                    "SISTEMA AETHER: He interiorizado el documento \'$fileName\' en modo local. (No se pudo procesar online: ${e.message})"\n                                }"'

good_str = '                                    "SISTEMA AETHER: He interiorizado el documento \'$fileName\' en modo local. (No se pudo procesar online: ${e.message})"\n                                }'

if bad_str in content:
    content = content.replace(bad_str, good_str)
    with open("app/src/main/java/com/example/ChatViewModel.kt", "w") as f:
        f.write(content)
        print("Fixed quote")
else:
    print("Not found")
