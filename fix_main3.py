with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

# Extract from where it currently is
start_token = "    LaunchedEffect(Unit) {\n        LocalLlmEngine.checkModelState(context)"
end_token = "val dlStatus by ModelDownloadState.status.collectAsStateWithLifecycle()\n"

if start_token in content and end_token in content:
    start_idx = content.find(start_token)
    end_idx = content.find(end_token) + len(end_token)
    extracted = content[start_idx:end_idx]
    
    # Remove from original
    content = content[:start_idx] + content[end_idx:]
    
    # Reinsert into AetherAppScreen after its `val context = LocalContext.current`
    target = "fun AetherAppScreen(viewModel: ChatViewModel) {"
    target_idx = content.find(target)
    if target_idx != -1:
        # Find the next LocalContext.current after AetherAppScreen
        context_target = "val context = LocalContext.current"
        context_idx = content.find(context_target, target_idx)
        if context_idx != -1:
            end_of_line = content.find("\n", context_idx)
            content = content[:end_of_line+1] + extracted + content[end_of_line+1:]

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
