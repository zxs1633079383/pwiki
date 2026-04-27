# Changelog

All notable changes to pwiki will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.5] — 2026-04-27

The "AI agent 也要看到新行为" 补丁。0.3.4 给 `pwiki brief` 加了
拒绝覆盖 + 时间戳 .bak 后，但 `pwiki init` 生成的 5 个 AI 工具
instruction 文件（CLAUDE.md / AGENTS.md / GEMINI.md / .clinerules /
.cursor/rules/pwiki.md）还在告诉 AI 无脑跑 `pwiki brief`——
AI 不知道 exit 1 是预期，会以为出错。

### Changed

- `pwiki/init.py` 的 `INSTRUCTIONS_TEMPLATE`：
  - 「今天的早报」表行后加注 `——见下方 brief safety note`。
  - 新增独立行「重新生成今天的早报」`pwiki brief --force` —— 仅在
    用户明确要求覆盖手填内容时使用。
  - 新增 **Brief safety note (0.3.4+)** 子段，4 步流程告诉 AI：
    exit 0 = 填新骨架；exit 1 + "refuse to overwrite" = 今天已填，
    直接读，**禁止**自动 `--force`，除非用户显式说"重做"；`--force`
    时旧文件已自动归档到 `.bak.<HHMMSS>`，可恢复。

### Why this matters

AI agent 与 CLI 的"行为契约"必须同步。0.3.4 改了 CLI 行为却没改
agent 指令 = 升级后 agent 报错 → 用户以为 pwiki 坏了。0.3.5 之后
任何装了新版 pwiki 的项目，重跑 `pwiki init` 后 AI 立刻认得
exit 1 是"今天已填"信号，不会乱用 `--force` 覆盖手填内容。



The "别把我手填的早报吞掉" 补丁。维护者今天踩坑：早上手填了
`daily/2026-04-27.md` 的 §②③④（10 个前沿方向 / 深度商机 / 自我演进），
后来在 `cses-client` 目录测试 `pwiki brief` 想看 CLI 是否随 cwd 工作——
`brief.py` 二话不说覆盖了 `.md`，**`.bak` 又把上一次的 `.bak` 抹了**，
手填的内容只能从对话记忆里重新打回去。

### Added

- **填充检测**：`pwiki/brief.py` 新增 `looks_like_scaffold()` 与
  `SCAFFOLD_MARKERS = ("1. ...\\n2. ...", "**主题：** ...", "_待 LLM 填", "## 素材区")`
  四个哨兵，只要存在任意一个就视为骨架，否则视为已编辑。
- **`pwiki brief --force`**：当 `daily/<today>.md` 已脱离骨架时，默认拒绝
  覆盖并 `exit 1`，错误信息含具体修复指引；`--force` 显式声明覆盖意图。
- **时间戳备份**：`rotate_backup()` 把旧 `.md` 写到
  `daily/<today>.md.bak.<HHMMSS>`（同秒内重跑追加 `-1`/`-2` 等后缀），
  不再只有一个 `.bak` 槽位。
- **回归测试**：`tests/test_smoke.py` 新增 4 条
  （`--force` flag / `looks_like_scaffold` 真假分支 / `rotate_backup` 不
  覆写已有备份 / 同秒重跑唯一性），pytest 14 → 全绿 0.45s。

### Why this matters

OSS CLI 的"幂等"和"无副作用"是底线之二。0.3.3 的 `pwiki brief`：
1) 默认覆盖 daily 不问；2) 单槽 `.bak` 同名覆盖。这两条叠在一起 = 用户
手填半小时的早报被一条命令静默吞掉，且无任何文件系统恢复路径。0.3.4
之后：填好的早报需要 `--force` 才会被覆盖，且每次覆盖都按时间戳归档，
重跑多少次都能找到任意一次旧版本。



The "stop polluting people's projects" patch. Real-user feedback：
"我本地没有 codex 还给我生成了 AGENTS.md 什么的"——`pwiki init` 之前
无脑给 5 种 AI 工具全部生成 instruction 文件，不管你本地是否实际装了。

### Added

- **`_tool_installed()` 本地检测函数**：
  - **Claude Code**：`shutil.which("claude")` PATH 查找
  - **Codex CLI**：`shutil.which("codex")`
  - **Gemini CLI**：`shutil.which("gemini")`
  - **Cursor**：macOS 检查 `/Applications/Cursor.app`，其他系统 `which cursor`
  - **Cline**：扫 `~/.vscode/extensions`、`~/.vscode-insiders/extensions`、
    `~/.cursor/extensions`、`~/.windsurf/extensions` 找 `saoudrizwan.claude-dev*`
  - **保底信号**：项目里已有该工具的配置文件（CLAUDE.md / AGENTS.md / .clinerules
    / .cursor/）也算"用户在用"
- **`--all` flag**：强制写所有 5 个文件（恢复 0.3.2 之前的行为，给在远程 server
  init 又想 push 给本地用的场景用）
- **`--only=claude,cursor` flag**：手动指定写哪几个

### Changed

- `pwiki init` 输出第二段标题改成
  "🔍 AI agent tools **detected on this machine + in this project**"
  ——明确告诉用户这是本地检测结果，不是无脑列表
- 检测命中显示 `✓` + 命中原因（"claude on PATH" / "Cursor.app installed" /
  "config file present"），未命中显示 `⊘` + "not detected — skipping;
  pass --all to force"
- 0 个工具命中时直接 exit 1，并提示用 `--all` 或 `--only`

### Why this matters

OSS 工具的"客户端尊重"是底线之一——往用户项目里塞他根本不用的 AI 工具
配置文件等于擅自污染。0.3.3 之后 `pwiki init` 只动你实际装了的工具的
配置文件。

## [0.3.2] — 2026-04-27

The "wiped the leftover crumbs" patch. Two real-user reports back-to-back:

1. New user running `pwiki init` saw the prompt **"Bootstrap docs/wiki/
   scaffold + LLM prompt?"** and asked "what's an LLM prompt? do I need
   one?" — turns out 0.3.0 already removed `_llm-prompt.md` generation,
   but three printout strings inside `pwiki/init.py` still mentioned it.
   Pure stale-text confusion.
2. Front-end project at `~/Downloads/venus` reported **1,396,520 LOC**
   (across "0 modules") on a JavaScript repo — same root cause as the
   cses-client bug found yesterday: `SKIP_DIRS` doesn't include `assets/`
   `public/` `static/`, where front-end projects routinely vendor Monaco /
   TinyMCE / AceEditor / fonts (100K+ LOC each).

### Fixed

- **Removed three stale `_llm-prompt.md` references** in `pwiki/init.py`:
  - line 8 docstring — corrected to describe scaffold (no prompt file)
  - prompt text — `"Bootstrap docs/wiki/ scaffold + LLM prompt?"` →
    `"Bootstrap docs/wiki/ scaffold (4 category dirs + 索引.md + log.md)?"`
  - post-bootstrap "next" tip — now points at the AI tool directly
  - final summary line — now reads `"帮我填 wiki" / "fill the wiki"` →
    AI reads CLAUDE.md protocol
- **`SKIP_DIRS` now includes `assets`, `public`, `static`** — front-end
  vendored bundles no longer inflate the LOC count by 10×-100×.
- **`scale:` line suppresses `across N modules` when N == 0** — small
  flat-layout projects (no `src/` / `lib/` / `packages/`) no longer print
  the misleading "across 0 modules".

### Why this matters

0.3.1 was the protocol upgrade. 0.3.2 is the pre-flight check for the
launch tweet — every new user runs `pwiki init` first, and a confusing
prompt at step 4 is enough for them to bounce. Patching the rough edge
costs less than re-acquiring the user.

## [0.3.1] — 2026-04-27

The "stop writing stubs" release. Real-user dogfood on a 50K+ LOC
Angular+Tauri project (cses-client) showed AI agents writing 8 thin pages
when they should have written 25-30 deep pages. Root cause: the Bootstrap
protocol said "5-15 pages" with no project-scale awareness, no required
page structure, and no citation density target. AI agents took the
permissive read.

### Added

- **Project scale awareness in `pwiki init`** — counts LOC across common
  code extensions, top-level modules, and detects `ARCHITECTURE.md` /
  `CONVENTIONS.md` / `DESIGN.md` style docs. Recommends page count based
  on scale:
  - <2K LOC → 5-8 pages
  - 2K-10K → 10-15
  - 10K-50K → **20-30** (cses-client / GitNexus class)
  - 50K+ → 35-50

- **Mandatory per-page structure** in INSTRUCTIONS_TEMPLATE Bootstrap
  protocol. Every leaf .md must now contain (no skipping):
  1. Frontmatter line with `Confidence:` + `Sources:` + `关联:`
  2. `## TL;DR` (1-2 sentences)
  3. ≥2 content sections (architecture / mechanism / data flow / etc.)
  4. **`## 源码锚点（Source Anchors）` table** with ≥3 rows
     `<file:line> | <description>`
  5. **`## 常见问题 / 边缘情况`** with ≥2 Q&A pairs
  6. **`## 与其他页的关联`** with ≥2 [[wikilink]] cross-references

  Pages without all six sections are explicitly rejected output.

- **Citation density target**: ≥3 source-path citations per page,
  with line numbers when feasible (`src/foo.ts:123`, `src/bar.ts:56-89`,
  or `ARCHITECTURE.md (§1.2 能力清单)`).

- **Page length target**: 400-800 words (was 200-600). 200-word stubs are
  insufficient for 20K+ LOC projects.

- **`init` output now reports scale** + recommended page count + detected
  arch docs, so the user immediately knows what to expect.

### Changed

- Bootstrap protocol expanded from 8 brief steps to 9 detailed steps
  (~150 lines → ~250 lines), each with explicit acceptance criteria.
- Quality bar upgraded from "10 minutes for a stranger to understand" to
  "a smart new hire could land a PR after reading these N pages".
- Step 6 (索引.md) now requires a `## 还没写的（Roadmap pages）` section
  listing items considered but deferred — the contract for the next
  ingest session.

### Why this matters

The wiki layer is only useful if it answers questions the source code
itself cannot quickly answer. Stub pages that just rename file paths add
zero value; deep pages with source anchors + tradeoff Q&A turn the wiki
into a reference a contributor can actually use to land a PR. 0.3.1 makes
the AI agent default to deep, not shallow.

## [0.3.0] — 2026-04-27

The "no separate prompt file" release. User feedback: writing
`_llm-prompt.md` and asking the AI to "go read it" is still a manual hop.
0.3.0 puts the **full LLM Wiki pattern** (Karpathy's full system —
3 layers, 3 operations, 6 page types, immutability rules, lint protocol,
v2 extensions roadmap) directly into the per-tool instruction sections.
The AI loads it once at session start; no external file to chase.

### Removed

- `docs/wiki/_llm-prompt.md` is no longer generated by `pwiki init`.
- `WIKI_PROMPT_TEMPLATE` removed from `pwiki/init.py`.

### Added

- **Full LLM Wiki Schema embedded in INSTRUCTIONS_TEMPLATE** (~150 lines):
  - Three-Layer Architecture (Raw / Wiki / Schema) with immutability
    gradient
  - Three Core Operations: Ingest / Query / Lint with explicit step lists
  - Six Page Types: Summary / Entity / Concept / Operation / Comparison /
    Synthesis with folder mapping
  - Bootstrap protocol (8 steps for empty `docs/wiki/`)
  - Ingest protocol (7 steps for new sources)
  - Lint protocol (5 categories: orphans / stale / contradictions /
    broken / citation gaps)
  - Quality bar enforcement
  - Optional confidence scoring guidance
- **`docs/wiki/log.md` auto-bootstrapped** alongside `索引.md` (append-only
  chronological record with parseable `## [YYYY-MM-DD] op | title` lines).
- **`docs/llm-wiki-pattern.md`** — the deep reference (v2 extensions:
  confidence scoring, supersession, forgetting/Ebbinghaus, consolidation
  tiers, typed relationships, hybrid search, automation hooks, scaling
  beyond 400K words, RAG vs LLM Wiki decision matrix). Linked from the
  Schema section so the agent can dive in if needed but isn't forced to
  read it for the basic protocols.

### Why this is "100% automation, finally"

After `pwiki init`:
1. User says "fill the wiki" / "帮我填 wiki" / etc. (one phrase, any tool).
2. AI's existing context already contains: 3-layer model, 6 page types,
   8-step bootstrap protocol, 5-category lint, citation rules, quality bar.
3. AI reads README + manifest + src/ → writes pages → runs `pwiki sync` →
   reports back.

No `_llm-prompt.md` to read. No external doc to chase. The Schema **is**
the contract — exactly what Karpathy described.

### Migration from 0.2.x

Re-run `pwiki init -y` in any project. The marker pair updates the
section in place; existing `_llm-prompt.md` is left as-is (you can delete
it manually if you want).

## [0.2.1] — 2026-04-27

Closes the last manual gap in the "init → wiki content" flow. After 0.2.0,
the user still had to know to say something like "open docs/wiki/_llm-prompt.md
and follow it". 0.2.1 makes `"fill the wiki"` (or any natural variant) a
top-level trigger in every AI tool's instruction file — the AI handles the
rest, including running pwiki sync at the end.

### Added

- **"fill the wiki" trigger** in every per-tool instruction file (CLAUDE.md /
  AGENTS.md / GEMINI.md / .clinerules / .cursor/rules/pwiki.md). Triggers on:
  - English: "fill the wiki" / "scan my code and write the wiki" / "generate the wiki from my code"
  - Chinese: "帮我填 wiki" / "扫一下源码写 wiki"
  - Implicit: when `docs/wiki/` exists but leaf files are empty
- **6-step "Wiki bootstrap protocol"** in the AI instruction template, plus
  an explicit quality bar ("a stranger reading should be able to answer
  what / 5 pieces / how they fit together in under 10 minutes; skip pages
  that just paraphrase comments").

### Changed

- **`docs/wiki/_llm-prompt.md` template** rewritten for AI agents
  (not humans) — explicit Step 1-6 sequence, file format requirements,
  citation expectations.

### Migration

Re-run `pwiki init -y` in any project that was init'd with 0.2.0. The
marker pair `<!-- pwiki:begin --> ... <!-- pwiki:end -->` will update the
instruction sections in place; existing CLAUDE.md / AGENTS.md content
outside those markers is preserved.

## [0.2.0] — 2026-04-27

The "100% automation, not 95%" release. Real-user feedback was that 0.1.x
required ~7 manual CLI steps to get going, plus the user had to know what a
`docs/wiki/` directory is supposed to contain. Both barriers gone.

### Added

- **`pwiki init`** — first-time setup that aims for zero further CLI use:
  1. Detects project metadata (Python / Node / Go / Rust / Java + git).
  2. Detects 5 AI agent tools and writes per-tool instructions:
     - `CLAUDE.md` (Claude Code, append-or-update an injected section)
     - `AGENTS.md` (Codex CLI)
     - `GEMINI.md` (Gemini CLI)
     - `.clinerules` (Cline)
     - `.cursor/rules/pwiki.md` (Cursor)
  3. Bootstraps `docs/wiki/` with category dirs + an `_llm-prompt.md` the
     user pastes into their AI to fill real content.
  4. Saves `./.pwikirc.json` (project_name, vault_path, written tools).
  5. (Optional) Runs first `sync + aliases + canvas` against the chosen Vault.

  After `pwiki init`, the user shouldn't need to type pwiki commands —
  they say "sync this wiki" / "今天的早报" to their AI tool, which reads
  the per-tool instructions file and runs the right command.

- **Per-tool instructions template** — same content, formatted for each
  agent's loading convention. Marker pair `<!-- pwiki:begin --> ... <!-- pwiki:end -->`
  lets re-running `pwiki init` update the section in place without
  clobbering other content in `CLAUDE.md` / `AGENTS.md`.

- **`pwiki init -y`** non-interactive mode for CI / scripted setup.

- **Smoke test for `init` subcommand**.

### Changed

- README Quick Start now leads with `pip install -U "pwiki-cli[rag,serve]" && pwiki init` —
  the recommended flow. The 5 manual subcommands moved to "Manual mode" appendix.

## [0.1.1] — 2026-04-27

Patch release fixing two issues found during real-world dogfood verification.

### Fixed

- **`examples/setup-demo.sh` templates were English placeholders** that didn't
  match the Chinese 4-section daily-brief promised in the README and launch
  tweets. New users running the demo would see "## ① Review queue (Ebbinghaus)"
  instead of "## ① 今日复习（艾宾浩斯到期）", causing confusion vs the
  marketing copy. Templates now match production layout 1:1, including the
  full 4-section daily, repo-index, ebbinghaus rules, and opportunity scaffold.

- **`pwiki query --rag` printed a fastembed UserWarning** on every invocation:
  > UserWarning: The model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  > now uses mean pooling instead of CLS embedding...

  fastembed 0.8 changed the pooling strategy; the embeddings remain functional
  for our use, so the warning is pure noise. Silenced via `warnings.filterwarnings`
  inside the lazy `_import_deps()` so the user-facing output is clean.

### Internal

- Updated install command in the `[rag]`-missing error message: `pip install 'pwiki[rag]'` → `pip install 'pwiki-cli[rag]'` (matches PyPI distribution name).

## [0.1.0] — 2026-04-27

Initial release.

### Added

- 7 orthogonal subcommands: `sync`, `aliases`, `canvas`, `brief`, `evolution`, `query`, `serve`
- Multi-repo Vault layout under `repos/<name>/`
- `pwiki sync` — copy any wiki/ directory into the Vault with managed YAML frontmatter
- `pwiki aliases` — resolve `[[english-slug]]` ↔ Chinese-named files via 4-pass matcher (filename / H1 / EN→ZH dict / raw token); `--dict` to extend with custom JSON
- `pwiki canvas` — JSON Canvas v1.0 multi-repo graph; alias-aware wikilink edge resolution
- `pwiki brief` — 4-section daily brief: Ebbinghaus review queue + 10 frontier directions + 1 deep opportunity + 1 self-evolution insight (rotates 4 quadrants by weekday)
- `pwiki evolution` — weekly rollup of self-evolution entries by quadrant
- `pwiki query` — grep-based search with frontmatter-aware ranking; `--rag` mode for local semantic search via fastembed multilingual MiniLM (offline, no API key)
- `pwiki serve` — local web UI: home / per-repo / note rendering / D3 Canvas viewer / inline grep+RAG search
- Optional extras: `[rag]` (fastembed + numpy), `[serve]` (fastapi + uvicorn + markdown-it-py), `[dev]` (pytest)
- 10 smoke tests; GitHub Actions CI matrix Python 3.10–3.13
- MIT license; full docs in `README.md`, `docs/ARCHITECTURE.md`, `docs/COMPARISON.md`
