# vhs script — record pwiki demo.gif
# Run: vhs demo.tape  →  emits docs/demo.gif

Output docs/demo.gif

Require pwiki
Require bash

Set Shell bash
Set FontSize 14
Set Width 1200
Set Height 720
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms
Set PlaybackSpeed 1.0
Set Padding 20

# Pre-flight: build the demo vault scaffolding (silent)
Hide
Type "bash examples/setup-demo.sh /tmp/demo-vault > /dev/null 2>&1"
Enter
Sleep 500ms
Type "clear"
Enter
Show

Type "# pwiki — Karpathy's LLM Wiki, brew-install ready"
Sleep 800ms
Enter
Type "pwiki --version"
Enter
Sleep 1500ms

Type "# 1. Sync a wiki/ folder into the Vault"
Sleep 600ms
Enter
Type "pwiki sync examples/sample-wiki demo --vault /tmp/demo-vault"
Enter
Sleep 2500ms

Type "# 2. Resolve [[english-slugs]] against Chinese-named files"
Sleep 600ms
Enter
Type "pwiki aliases demo --vault /tmp/demo-vault"
Enter
Sleep 2000ms

Type "# 3. Render multi-repo JSON Canvas (open in Obsidian)"
Sleep 600ms
Enter
Type "pwiki canvas --vault /tmp/demo-vault"
Enter
Sleep 2000ms

Type "# 4. Build today's morning brief"
Sleep 600ms
Enter
Type "pwiki brief --vault /tmp/demo-vault --repos-root /tmp/demo-vault"
Enter
Sleep 2500ms

Type "# What pwiki produced:"
Sleep 600ms
Enter
Type "ls /tmp/demo-vault"
Enter
Sleep 1500ms

Type "find /tmp/demo-vault/repos -name '*.md' | head"
Enter
Sleep 2000ms

Type "# Five orthogonal commands. github.com/zlc/pwiki"
Sleep 2500ms
Enter
