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

## Release flow（自动 ship —— 不要每次问用户）

**硬性规则**：只要修改了 `pwiki/*.py` 或任何会进 PyPI 包的代码并且**验证通过**，
就**主动**完成完整 release 流——不用每次问用户"要不要 push"。维护者已明确授权。

### 什么算"代码改动"（触发自动 ship）
- `pwiki/**.py` 任何改动
- `pyproject.toml` 依赖 / 元数据
- `examples/setup-demo.sh` 之类用户会跑的脚本
- 模板字符串（INSTRUCTIONS_TEMPLATE 等）

### 什么**不**触发自动 ship（只 commit + push，不发 PyPI）
- 仅 `README.md` / `README-zh.md` / `docs/**.md` / `CHANGELOG.md` 的文档改动
- `.github/`、CI 配置
- `tests/` 的纯测试改动（无生产代码）

### "验证通过"的最低门槛
1. **Smoke test 必须跑**：`~/.pwiki-venv/bin/pwiki init -y --no-first-run` 在
   `/tmp/pwiki-smoke-<version>` 临时目录，输出**不能**包含
   `_llm-prompt` / `LLM prompt` 等已知 stale 词，所有 5 个 AI 工具
   instruction 文件都得 `created`。
2. **真实环境冒烟**：在 `/Users/mac28/workspace/angular/cses-client` 跑一次
   `pwiki init -y --no-first-run`，确认 scale 行格式正常、不再报已知数字 bug、
   `<!-- pwiki:begin --> ... <!-- pwiki:end -->` 段更新成功（`grep` 关键 marker
   关键词如 `源码锚点` / `400-800` 全部命中）。
3. **测试套件**：`~/.pwiki-venv/bin/python -m pytest -q` 全绿（如果改动碰
   了 `pwiki/init.py` 的逻辑而非纯打印文本）。

任何一项没过 → **停下、报告维护者**，不要继续 ship。

### 自动 ship 步骤（验证全过后无需问，按顺序自动执行）
1. **Bump version**：`pwiki/__init__.py` 和 `pyproject.toml` 同步改 semver
   （bug 修 → patch；新功能但兼容 → minor；破坏性 → major + 邮件通知）。
2. **CHANGELOG.md**：在顶部追加新版本 entry，按现有格式（标题 + 故事段
   + Added/Changed/Fixed 子段 + Why this matters）。**用中文写**。
3. **Commit**：按 `~/.claude/rules/common/git-workflow.md` 的 Conventional
   Commits 中文格式，type 选 `feat` / `fix` / `refactor` 等。Body 用中文
   解释**为什么这么改**（reference 真实用户反馈、dogfood 翻车、issue 编号）。
4. **Tag**：`git tag v0.x.y`。
5. **Push**：`git push origin main --tags` 一条命令同时推 commit 和 tag。
6. **Build + upload**：
   ```
   rm -rf dist build pwiki_cli.egg-info
   ~/.pwiki-venv/bin/python -m build
   ~/.pwiki-venv/bin/python -m twine upload dist/pwiki_cli-X.Y.Z*
   ```
   PyPI token 在 `~/.pypirc`，已配好；不会要密码。
7. **报告**：用一张表给维护者复盘 ship 状态（PyPI URL / commit hash /
   tag / 验证结果）。

### 什么时候**不要**自动 ship（即使验证通过）
- 维护者明确说"先别 push" / "先放着" / "等下" / "WIP"
- 当前在 plan 模式或 dry-run 模式
- 改动还包含未完成的 TODO / FIXME / `pass` 占位
- 维护者刚说"先看看效果" → 等 demo 反馈再 ship

### 第一次 PyPI token 配置见 [`RELEASE.md`](RELEASE.md)。

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
