#!/usr/bin/env bash
# Set up /tmp/demo-vault with the minimal scaffolding pwiki needs,
# so the demo.tape recording can run end-to-end without prep noise.
set -euo pipefail

VAULT="${1:-/tmp/demo-vault}"
echo "==> setting up demo Vault at $VAULT"
rm -rf "$VAULT"
mkdir -p "$VAULT/repos" "$VAULT/daily" "$VAULT/canvas" \
         "$VAULT/_meta" "$VAULT/_templates" "$VAULT/.obsidian"

# Minimal Ebbinghaus rules (referenced by `pwiki brief`)
cat > "$VAULT/_meta/ebbinghaus.md" <<'EOF'
---
type: meta
purpose: spaced-repetition rules used by pwiki brief
---
# Ebbinghaus

| stage | next interval |
|-------|---------------|
| 0     | +1d           |
| 1     | +3d           |
| 2     | +7d           |
| 3     | +15d          |
| 4     | +30d          |
| 5     | +60d          |
EOF

# Repo-index template (referenced by `pwiki sync`)
cat > "$VAULT/_templates/repo-index.md" <<'EOF'
---
type: repo-index
repo: {{repo}}
source_path: {{source_path}}
last_synced: {{date}}
note_count: {{count}}
---
# {{repo}} · Index

- **Path**: `{{source_path}}`
- **Last synced**: {{date}}
- **Notes**: {{count}}

## Concepts
{{concepts_list}}

## Entities
{{entities_list}}

## All notes
{{full_list}}
EOF

# Daily template (referenced by `pwiki brief`)
cat > "$VAULT/_templates/daily.md" <<'EOF'
---
type: daily-brief
date: {{date}}
weekday: {{weekday}}
quadrant: {{quadrant}}
---

# {{date}} morning brief

## ① Review queue (Ebbinghaus)
{{review_list}}

## ② 10 frontier directions
1. ...

## ③ Deep opportunity (1)
...

## ④ Self-evolution — {{quadrant}}
{{evolution_block}}
EOF

# Minimal Obsidian config so the folder is recognized as a Vault
cat > "$VAULT/.obsidian/app.json" <<'EOF'
{}
EOF

echo "==> ready: $VAULT"
ls -la "$VAULT"
