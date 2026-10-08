with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

# I need to move `LaunchedEffect` and `val dlProgress...` inside `fun AetherAppScreen`.
# Let's just remove it from where it is and insert it inside the function block.
start_token = "    LaunchedEffect(Unit) {"
end_token = "val dlStatus by ModelDownloadState.status.collectAsStateWithLifecycle()"

if start_token in content and end_token in content:
    start_idx = content.find(start_token)
    end_idx = content.find(end_token) + len(end_token)
    extracted = content[start_idx:end_idx]
    
    # Remove from original
    content = content[:start_idx] + content[end_idx:]
    
    # Reinsert correctly
    target = "fun AetherAppScreen(viewModel: ChatViewModel) {"
    target_idx = content.find(target)
    if target_idx != -1:
        insert_pos = target_idx + len(target)
        content = content[:insert_pos] + "\n" + extracted + "\n" + content[insert_pos:]

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
