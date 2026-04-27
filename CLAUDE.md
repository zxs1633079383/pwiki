# CLAUDE.md — Project Context for Claude Code

This file is auto-loaded when Claude Code works in this repo. Read it before
proposing changes.

## What is pwiki

> *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."*
> — Andrej Karpathy, [LLM Wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), April 2026

pwiki packages [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) as
a brew-install-ready CLI. Five orthogonal subcommands turn any folder of
generated markdown wikis into a self-maintaining, cross-repo knowledge base.

**One-line elevator pitch**: pip install + 5 commands beats clone + 50-line
tutorial. That's the entire delta vs the 6+ existing OSS implementations.

## Funnel position (read before scope-creeping)

This is **product ① of a 3-stage funnel** the maintainer is running:

```
①pwiki (OSS, this repo)  →  ②DailyBrain ($9/mo subscription)  →  ⑤Team Wiki SaaS ($29/seat/mo)
   引流（free forever）           留存                                       主收入
```

Implications:

- pwiki itself **does not generate revenue**. Don't add paywalls to CLI features.
- pwiki's job is **GitHub stars and Twitter signal** to feed ② and ⑤.
- The hosted version (0.4) is gated on **GitHub ⭐ ≥ 300 by 2026-05-24** — see [`docs/0.4-hosted-spec.md`](docs/0.4-hosted-spec.md). **Don't write 0.4 code yet.**
- The full thesis lives in `~/Documents/Obsidian Vault/opportunities/pwiki.md` (in the maintainer's local Obsidian Vault, not in this repo). Decision day: **2026-05-24**.

## Architecture in 60 seconds

Five orthogonal Python modules under `pwiki/`. **Vault is source of truth.
Frontmatter is the contract.** Each module reads / writes only what its
contract says.

| Module | Reads | Writes | Lines (approx) |
|---|---|---|---|
| `sync.py` | source `wiki/` dir | `Vault/repos/<repo>/` | ~150 |
| `aliases.py` | `Vault/repos/<repo>/索引.md` (or `index.md`) | same files (frontmatter only) | ~250 |
| `canvas.py` | `Vault/repos/` | `Vault/canvas/all-repos.canvas` | ~180 |
| `brief.py` | `Vault/repos/` + `~/workspace/*` git logs | `Vault/daily/<today>.md` | ~190 |
| `evolution.py` | `Vault/daily/*.md` (past 7) | `Vault/evolution/<YYYY>-W<WW>.md` | ~120 |
| `query.py` (0.2-B/C) | `Vault/repos/` + (`.pwiki/embeddings.npy`) | stdout | ~250 |
| `index_embed.py` (0.2-C) | `Vault/repos/` | `Vault/.pwiki/{embeddings.npy,meta.jsonl,index.json}` | ~180 |
| `serve.py` (0.3) | the whole Vault | HTTP responses | ~340 |
| `cli.py` | argv | dispatch to modules | ~50 |

Full architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Conventions and constraints

### Coding style

- **Python 3.10+**, type-annotated where it adds clarity (not religiously).
- **No external runtime deps for core 0.1 features.** Stdlib only — pathlib, re, json, datetime, argparse. The whole point is `pip install pwiki` is small + fast.
- Optional features go behind `pip install 'pwiki[<extra>]'`:
  - `[rag]` → fastembed + numpy
  - `[serve]` → fastapi + uvicorn + markdown-it-py
  - `[dev]` → pytest + pytest-cov
- **Lazy imports inside the optional modules**: `index_embed.py` and `serve.py` import their heavy deps inside `_import_deps()` so the OSS install doesn't break if extras are missing. Keep this pattern.
- Functions ≤ 50 lines. Files ≤ 400 lines. If a module wants to grow past 400, split it.
- No mutable globals. No singletons.
- Errors: prefer `sys.exit("clear message")` for CLI paths; raise typed exceptions only inside library code.

### Frontmatter contract (the most important invariant)

Every note pwiki writes has YAML frontmatter with these fields. **Never
rewrite a file without preserving the user's hand-edited fields.**

```yaml
---
source_repo: <name>          # managed by sync; safe to overwrite
source_path: <rel>           # managed by sync; safe to overwrite
last_synced: <YYYY-MM-DD>    # managed by sync; safe to overwrite
ebbinghaus_stage: <0..6>     # managed by brief; user may hand-edit; merge, don't overwrite
last_reviewed: <YYYY-MM-DD>  # managed by brief; user may hand-edit; merge, don't overwrite
tags: [...]                  # auto-seeded by sync; user may add; merge
aliases: [...]               # added by aliases; user may add; merge
---
```

`pwiki sync` is idempotent: it merges new fields into existing frontmatter,
**never deletes fields it didn't add**.

### Tests

```bash
pip install -e ".[dev]"
pytest -q                 # 10 smoke tests (~0.5s); CI runs same
```

CI matrix: Python 3.10, 3.11, 3.12, 3.13. **Do not add 3.14 to the matrix
yet** — onnxruntime ships no 3.14 wheels (as of 2026-04), so `[rag]` extra
will fail to resolve.

### Smoke tests philosophy

Tests in `tests/test_smoke.py` are **CLI dispatch checks only**. They verify
every subcommand has a working `--help` and the package imports clean. They
do NOT exercise the full Vault flow — that requires a real Vault fixture and
is intentionally manual (run on `examples/sample-wiki/` + `/tmp/demo-vault/`).

## Adding a new subcommand

1. Create `pwiki/<name>.py` with a `main()` that uses `argparse`.
2. Register in `pwiki/cli.py` `SUBCOMMANDS` dict.
3. Add `<name>` to `pwiki/__init__.py` `__all__`.
4. Add `test_<name>_help` to `tests/test_smoke.py`.
5. Update `pwiki/__init__.py` docstring with the one-line description.
6. Update README's Quick Start section if it's user-facing.

## Things to NOT do

- ❌ Don't make a CLI feature paywalled — would break the funnel design.
- ❌ Don't move heavy deps (fastembed, fastapi, torch, numpy) to `dependencies` from `optional-dependencies`.
- ❌ Don't write to anywhere outside `<vault>/` — the user's filesystem is theirs, not ours.
- ❌ Don't paraphrase Karpathy's quote in marketing — it's verbatim or omit ("Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.").
- ❌ Don't start writing 0.4 hosted code before the decision gate (⭐ ≥ 300). Premature SaaS without OSS validation is the named failure mode.
- ❌ Don't import torch / sentence-transformers — fastembed (ONNX) is intentional, ~10x smaller install.
- ❌ Don't bump `version` in `pyproject.toml` without also tagging git + writing a `CHANGELOG.md` entry.
- ❌ Don't change the GitHub URL away from `zxs1633079383/pwiki` — multiple files reference it; use `grep -rn` to verify.

## Release flow

OSS releases:
1. Bump `version` in `pyproject.toml`
2. Update `CHANGELOG.md`
3. `git commit -m "release: 0.x.y"` + `git tag v0.x.y` + `git push --tags`
4. `bash scripts/release.sh` → builds + uploads to PyPI (requires `~/.pypirc`)

See [`RELEASE.md`](RELEASE.md) for the first-time PyPI token setup.

## Useful commands while iterating

```bash
# Reinstall after editing
pip install -e .                          # core only
pip install -e ".[rag,serve,dev]"         # full

# Run the demo end-to-end against /tmp/demo-vault
bash examples/setup-demo.sh /tmp/demo-vault
pwiki sync     examples/sample-wiki demo --vault /tmp/demo-vault
pwiki aliases  demo --vault /tmp/demo-vault
pwiki canvas   --vault /tmp/demo-vault
pwiki brief    --vault /tmp/demo-vault --repos-root /tmp/demo-vault

# Re-record the demo gif
vhs demo.tape   # → docs/demo.gif

# Test the web UI (requires [serve] extra)
pwiki serve --port 8080 --open
```

## Maintainer's broader system

The maintainer runs an Obsidian Vault at `~/Documents/Obsidian Vault` with
Self-hosted LiveSync to a local CouchDB (`~/.obsidian-livesync/`). pwiki was
extracted from the four skills under `~/.claude/skills/`:

- `obsidian-bridge` → `pwiki sync` + `pwiki aliases`
- `morning-brief`   → `pwiki brief`
- `vault-canvas`    → `pwiki canvas`
- `evolution-tracker` → `pwiki evolution`

The originals stay in `~/.claude/skills/` and remain canonical for the
maintainer's personal workflow; this repo is the OSS extraction.

## When in doubt

The two source-of-truth docs:

- `docs/ARCHITECTURE.md` — how it works, contracts, composition rules
- `docs/COMPARISON.md` — vs Karpathy's gist + 6 OSS implementations + DeepWiki + Obsidian Sync

Both are kept in sync with code. If a code change makes one stale, update both
in the same commit.
