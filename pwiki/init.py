"""pwiki init — first-time setup that aims for 100% automation.

What it does (in order):
  1. Detect project metadata (language, git, existing docs/wiki).
  2. Detect AI agent tooling (CLAUDE.md, AGENTS.md, .cursor/, GEMINI.md, .clinerules).
  3. Ask 4 yes/no questions (defaults reasonable so just `pwiki init -y` works).
  4. Write per-tool instructions so the user's AI can call pwiki without manual CLI.
  5. Bootstrap docs/wiki/ if absent: minimal scaffold (category dirs +
     索引.md + log.md). The AI reads the LLM Wiki protocol directly from
     CLAUDE.md / AGENTS.md / .cursor/rules — no separate prompt file.
  6. Run first `sync` + `aliases` + `canvas` against the chosen Vault.
  7. Save config to ./.pwikirc.json.

Goal: after `pwiki init`, the user never types `pwiki <subcommand>` again —
they just talk to their AI tool.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sys
from importlib import import_module

from . import __version__

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"


# ─────────────────────────────────────── detection

CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".kt",
    ".swift", ".cpp", ".cc", ".c", ".h", ".hpp", ".cs", ".rb", ".php",
    ".scala", ".vue", ".svelte", ".m", ".mm", ".dart", ".ex", ".exs",
}
SKIP_DIRS = {
    "node_modules", "target", "dist", "build", ".git", ".venv", "venv",
    "__pycache__", ".next", ".nuxt", "out", "vendor", ".pwiki", ".idea",
    ".vscode", "coverage", ".pytest_cache", ".mypy_cache", "site-packages",
    # 0.3.2: front-end projects often vendor third-party code (Monaco,
    # TinyMCE, AceEditor, fonts) under assets/ public/ static/. These can
    # add 100K+ phantom LOC and inflate the page-count recommendation.
    "assets", "public", "static",
}


def count_loc(cwd: pathlib.Path, max_files: int = 5000) -> int:
    """Best-effort LOC count across common code extensions. Capped to avoid
    pathological repos. Returns total physical lines (including blanks/comments)."""
    total = 0
    seen = 0
    for p in cwd.rglob("*"):
        if seen >= max_files:
            break
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in p.relative_to(cwd).parts[:-1]):
            continue
        if p.suffix.lower() not in CODE_EXTENSIONS:
            continue
        seen += 1
        try:
            with open(p, "rb") as fp:
                total += sum(1 for _ in fp)
        except Exception:
            pass
    return total


def count_top_modules(cwd: pathlib.Path) -> int:
    """Count top-level dirs under common source roots."""
    n = 0
    for cand in ("src", "src-tauri/src", "lib", "app", "cmd",
                 "internal", "packages", "apps"):
        p = cwd / cand
        if p.is_dir():
            n += sum(1 for c in p.iterdir() if c.is_dir() and c.name not in SKIP_DIRS)
    return n


def recommend_pages(loc: int) -> tuple[str, int]:
    """(range_label, target_count) for the page-count recommendation."""
    if loc < 2_000:   return ("5-8", 6)
    if loc < 10_000:  return ("10-15", 12)
    if loc < 50_000:  return ("20-30", 25)
    return ("35-50", 40)


def find_arch_docs(cwd: pathlib.Path) -> list[pathlib.Path]:
    """Find ARCHITECTURE.md / CONVENTIONS.md / DESIGN.md style files at root or under docs/."""
    out = []
    patterns = ("ARCHITECTURE.md", "CONVENTIONS.md", "DESIGN.md", "PLAN.md",
                "DECISIONS.md", "ARCH.md")
    for pat in patterns:
        for hit in list(cwd.glob(pat)) + list(cwd.glob(f"docs/{pat}")) + \
                   list(cwd.glob(f"src-tauri/{pat}")) + list(cwd.glob(f"docs/**/{pat}")):
            if hit.is_file():
                out.append(hit)
    # dedupe
    seen, uniq = set(), []
    for p in out:
        if p in seen:
            continue
        seen.add(p)
        uniq.append(p)
    return uniq


def detect_project(cwd: pathlib.Path) -> dict:
    info = {"path": str(cwd), "lang": "unknown", "name": cwd.name,
            "is_git": (cwd / ".git").is_dir(), "wiki_dir": None,
            "loc": 0, "n_modules": 0, "page_range": "5-8", "page_target": 6,
            "arch_docs": []}
    if (cwd / "pyproject.toml").is_file() or (cwd / "setup.py").is_file():
        info["lang"] = "python"
    elif (cwd / "package.json").is_file():
        info["lang"] = "javascript"
    elif (cwd / "go.mod").is_file():
        info["lang"] = "go"
    elif (cwd / "Cargo.toml").is_file():
        info["lang"] = "rust"
    elif (cwd / "pom.xml").is_file() or (cwd / "build.gradle").is_file():
        info["lang"] = "java"
    for cand in ("docs/wiki", "wiki", ".latticeai/wiki"):
        p = cwd / cand
        if p.is_dir() and any(p.glob("*.md")):
            info["wiki_dir"] = str(p)
            break
    info["loc"] = count_loc(cwd)
    info["n_modules"] = count_top_modules(cwd)
    info["page_range"], info["page_target"] = recommend_pages(info["loc"])
    info["arch_docs"] = [str(p.relative_to(cwd)) for p in find_arch_docs(cwd)]
    return info


# Each entry: (display name, target relative path under cwd, write mode)
# write mode: 'create' (file must not exist; create with template),
#             'append' (file may exist; append/inject our section),
#             'rules-dir' (write inside an existing rules directory only)
AI_TOOLS = [
    ("Claude Code", "CLAUDE.md", "append"),
    ("Codex CLI",   "AGENTS.md", "append"),
    ("Gemini CLI",  "GEMINI.md", "append"),
    ("Cline",       ".clinerules", "create"),
    ("Cursor",      ".cursor/rules/pwiki.md", "rules-dir"),
]


def _tool_installed(name: str, target: pathlib.Path) -> tuple[bool, str]:
    """Detect whether a given AI tool is plausibly used by this user.

    Two signals:
      1. project already has the tool's config file (or .cursor/ dir) → user uses it
      2. local install detected via PATH binary or known app/extension dir
    Returns (installed, reason). Reason is short string for the print line.
    """
    # Signal 1: project already has the tool's config file
    if target.is_file():
        return True, "config file present"
    if name == "Cursor" and target.parent.is_dir():
        return True, ".cursor/ dir present"

    # Signal 2: local install
    home = pathlib.Path.home()
    if name == "Claude Code" and shutil.which("claude"):
        return True, "claude on PATH"
    if name == "Codex CLI" and shutil.which("codex"):
        return True, "codex on PATH"
    if name == "Gemini CLI" and shutil.which("gemini"):
        return True, "gemini on PATH"
    if name == "Cursor":
        if pathlib.Path("/Applications/Cursor.app").exists():
            return True, "Cursor.app installed"
        if shutil.which("cursor"):
            return True, "cursor on PATH"
    if name == "Cline":
        # Cline is a VSCode/Cursor/Windsurf extension — check common ext dirs
        for vs in (".vscode", ".vscode-insiders", ".cursor", ".windsurf"):
            ext_dir = home / vs / "extensions"
            if ext_dir.is_dir():
                try:
                    for p in ext_dir.iterdir():
                        if p.name.startswith("saoudrizwan.claude-dev"):
                            return True, f"Cline ext in ~/{vs}"
                except OSError:
                    continue
    return False, ""


def detect_ai_tools(cwd: pathlib.Path, force_all: bool = False,
                    only: set[str] | None = None) -> list[dict]:
    """For each known tool, decide whether we WILL/CAN write to it.

    Eligibility rules (in order):
      • force_all=True → all tools eligible
      • only is a set → only those tools eligible (lowercase first-word match)
      • otherwise → eligible iff _tool_installed() returns True
    """
    out = []
    for name, rel, mode in AI_TOOLS:
        target = cwd / rel
        action = None
        if mode == "append":
            action = "append" if target.is_file() else "create"
        elif mode == "create":
            action = "create" if not target.is_file() else "skip-exists"
        elif mode == "rules-dir":
            parent = target.parent
            if parent.is_dir():
                action = "create" if not target.is_file() else "skip-exists"
            else:
                # Cursor rules dir doesn't exist; offer to create
                action = "create-with-parent"

        # Eligibility
        if force_all:
            eligible, reason = True, "forced via --all"
        elif only is not None:
            tool_key = name.lower().split()[0]
            eligible = tool_key in only
            reason = "explicit via --only" if eligible else "not in --only"
        else:
            eligible, reason = _tool_installed(name, target)

        out.append({"tool": name, "rel": rel, "target": target,
                    "mode": mode, "action": action,
                    "eligible": eligible, "reason": reason})
    return out


# ─────────────────────────────────────── instruction template

INSTRUCTIONS_TEMPLATE = """\
## pwiki — Karpathy LLM Wiki for this project

This project uses [pwiki](https://github.com/zxs1633079383/pwiki), an
implementation of [Andrej Karpathy's LLM Wiki pattern][gist] (April 2026).

[gist]: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

> *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."*

You (the AI agent reading this file) are now the wiki's maintainer. Read
the entire section below **once** at session start; thereafter you have
the full LLM Wiki pattern in context and need not re-read anything else.

### What an LLM Wiki is (compressed primer)

Three layers, immutability gradient:

| Layer | What | Mutability | Lives at |
|---|---|---|---|
| **Raw** | source articles, papers, code, transcripts | strictly immutable | the project's source tree itself |
| **Wiki** | LLM-compiled markdown summaries / entity / concept / comparison / synthesis pages | mutable — you maintain | `docs/wiki/` |
| **Schema** | structure, conventions, workflows | semi-mutable (human + LLM co-evolve) | this file you're reading + `docs/wiki/索引.md` + `docs/wiki/log.md` |

**Compile, don't retrieve.** RAG re-discovers per query; LLM Wiki compiles
once into persistent structured markdown so knowledge accumulates. They
are complementary — once `docs/wiki/` has >100 pages, layer RAG on top
(`pwiki query --rag` already does this).

### Three core operations

| Operation | When | What you do |
|---|---|---|
| **Ingest** | user adds a new source (paper / commit / decision / transcript) | read the source → write a Summary page → update / create related Entity / Concept / Comparison / Synthesis pages → revise `索引.md` → append a line to `log.md` (one ingest typically touches 5-15 pages) |
| **Query** | user asks "find my notes on X" / "what did I write about Y" | search wiki pages, synthesize answer with `[[wikilink]]` citations; if the question is high-value, file the synthesized answer back as a permanent Synthesis page |
| **Lint** | user says "lint the wiki" / weekly | scan for: contradictions, stale facts, orphan pages (no incoming links), missing cross-references, broken `[[wikilinks]]`, knowledge gaps. Self-heal: link orphans, mark stale, propose deletions |

### Page types (Karpathy's taxonomy)

| Type | Folder | Holds |
|---|---|---|
| Summary  | `docs/wiki/概要/` (optional) | one source → one page distilling its claims |
| Entity   | `docs/wiki/实体/` | concrete things: packages, modules, classes, services, people, products |
| Concept  | `docs/wiki/概念/` | algorithms, models, abstract patterns, design principles |
| Operation| `docs/wiki/操作/` | flows, pipelines, runbooks, step-by-step how-tos |
| Comparison| `docs/wiki/对比/` | tradeoff tables: this vs that, version A vs B |
| Synthesis | `docs/wiki/综合/` | ties multiple of the above into a thesis: "what we believe and why" |

Files connect through `[[english-slug]]` wikilinks. Slugs must be lowercase,
URL-safe, hyphenated; `pwiki aliases` later auto-resolves them to whatever
Chinese / mixed filename they actually live under.

### User-trigger → action table (run pwiki, don't write custom code)

| User intent (any of these phrasings) | Action |
|---|---|
| **"fill the wiki" / "帮我填 wiki" / "扫一下源码写 wiki"** — empty `docs/wiki/` or first run | follow **Bootstrap protocol** below |
| **"ingest <X>" / "把这篇 paper 整理进 wiki" / "把这次决策记下来"** | follow **Ingest protocol** below |
| **"lint the wiki" / "wiki 体检" / "检查矛盾"** | follow **Lint protocol** below |
| "sync" / "同步 wiki" / after editing `docs/wiki/` | `pwiki sync ./docs/wiki {project_name}` |
| "解析 wikilink" / `[[slug]]` 没连上 | `pwiki aliases {project_name}` |
| "看图谱" / "canvas" / "knowledge graph" | `pwiki canvas` (open `Vault/canvas/all-repos.canvas` in Obsidian) |
| "今天的早报" / "morning brief" | `pwiki brief` —— 见下方 brief safety note |
| "重新生成今天的早报" / "regenerate today's brief" | `pwiki brief --force` —— 仅在用户**明确**要求覆盖手填内容时用 |
| "搜笔记" / "查 X" / "find my notes on Z" | `pwiki query --rag "<question>"` |
| "本地启 web UI" | `pwiki serve --open` |
| "周回顾" / "weekly evolution" | `pwiki evolution` |

#### Brief safety note (0.3.4+)

`pwiki brief` is **idempotent** the first time each day, but **refuses to
overwrite** a daily that has been edited beyond the scaffold (no
`1. ...` / `_待 LLM 填` / `## 素材区` sentinels remain). When this happens
the CLI exits **1** with a message recommending `--force`. The expected
flow:

1. User says "今天的早报" → run `pwiki brief`.
2. If exit 0 → read the new scaffold and fill §②③④ in place.
3. If exit 1 with "refuse to overwrite" → today's daily is **already
   filled**. Just read it; do NOT re-run with `--force` unless the user
   explicitly asks to regenerate (e.g. "scrap today's brief and redo it").
4. When `--force` is invoked, the prior daily is auto-archived to
   `daily/<today>.md.bak.<HHMMSS>` (timestamped, never clobbered), so the
   user's hand-edits are always recoverable from that file.

### Bootstrap protocol (empty `docs/wiki/`, first time)

**Project scale signal**: this project measures ~**{loc:,} LOC** across
**{n_modules} top-level modules**. **Recommended page count: {page_range}
pages** (target {page_target}). Aim for the top of the range — denser is
better than sparser. Stub-level pages (200-word paraphrases of filenames)
are zero-value and must be skipped, not counted.

**Architecture docs detected**: {arch_docs_list}
Read these **in full**, not just headers — they are the project's own raw
layer and your most important grounding. Cite them heavily by named
section (e.g. `ARCHITECTURE.md (§1.2 能力清单)`).

#### Step 1 — Required reads (in order, in full)

| What | Why |
|---|---|
| `README*` at project root | high-level positioning |
| Package manifest (`pyproject.toml` / `package.json` / `go.mod` / `Cargo.toml` / `pom.xml`) | dependencies + scripts + intent |
| ARCHITECTURE / CONVENTIONS / DESIGN / PLAN / RFC*.md (root or `docs/`) — **full content** | the project's raw layer |
| `src/` (or equivalent) top-level listing | module map |
| **One representative file from each significant subdirectory** | confirm what each module actually does |

If `ARCHITECTURE.md` contains a capability table or module list, **each row
is a candidate Entity page**. Don't paraphrase the table — expand each row
into a full page.

#### Step 2 — Pick {page_target}±3 significant items

Group into:
- **实体 (entities)** — concrete packages / classes / services / capabilities (typically the largest bucket)
- **概念 (concepts)** — algorithms / patterns / design principles
- **操作 (operations)** — flows / pipelines / runbooks
- **对比 (comparisons)** — this vs that, version 1 vs 2
- **综合 (synthesis)** — *required* for projects ≥10K LOC; ties multiple pages into a thesis ("what we believe and why")

Skip: vendored deps, generated code, test fixtures, trivial DTOs,
single-line wrappers.

#### Step 3 — Write each page with this MANDATORY structure

**Every leaf .md must contain ALL of these sections.** No skipping. Stub
pages without these sections are rejected output.

```markdown
# <Title>

> Confidence: High|Medium|Low · Sources: `<file>` (`<section>`), `<file2>:<line>` · 关联：[[other-page]]

## TL;DR
<1-2 sentences: what is this, why does it exist, what does it do>

## <Section 1 — Architecture / Mechanism / Lifecycle>
<200-400 words. Plain markdown. The "core mechanism" of this entity/concept.>

## <Section 2 — Data flow / Protocol / Algorithm / the most non-obvious aspect>
<more depth. Pick whatever angle gives the highest information density.>

## 源码锚点（Source Anchors）

| 位置 | 作用 |
|------|------|
| `src/foo/bar.ts:123` | <one-line description> |
| `src/baz.rs:45-67` | <description> |
| `<at least 3-5 rows>` | ... |

## 常见问题 / 边缘情况

- **"X 时会发生什么？"** — <answer + code citation>
- **"为啥不直接 Y？"** — <reasoning + tradeoff cited from arch doc>
- <at least 2 Q&A pairs>

## 与其他页的关联

- [[some-slug]] — <one-line: how it connects>
- [[another-slug]] — <how it connects>
- <at least 2 cross-references>
```

**Target page length: 400-800 words** (longer is fine for hub Entity pages).
200-word stubs are insufficient for a {loc:,} LOC project.

#### Step 4 — Citation discipline (non-negotiable)

Every load-bearing claim cites a source path, line number when feasible:

- `src-tauri/src/lib.rs:142` — specific line
- `src/app/bridge/wsClient.ts:56-89` — range
- `ARCHITECTURE.md (§1.2 能力清单)` — named section in a raw doc

**No citation = delete the sentence.** "This module probably does X" without
opening the file is forbidden — either read the file and cite a line, or
skip the claim entirely.

Density target: **≥3 source-path citations per page** (more for Entity pages
that map to actual modules).

#### Step 5 — Quality bar (must pass before each page is included)

A stranger reading the page must be able to:

1. Explain what this thing does in 30 seconds (TL;DR)
2. Find the actual implementation in 1 minute (源码锚点 table)
3. Spot 1-2 non-obvious tradeoffs the team made (常见问题)
4. Navigate to 2+ related pages without backtracking (关联)

If a page fails any of the four, **rewrite or delete** before publishing.
The goal is not "we wrote a page about this module"; it is "a smart new
hire could land a PR after reading these {page_target} pages".

#### Step 6 — Write `docs/wiki/索引.md` (the navigation hub)

Every page listed once, grouped by type, format:

```
## 实体（Entities）
- [[english-slug]] — **中文名**: one-line hook ≤ 80 chars
- ...
## 概念（Concepts）
- ...
## 还没写的（Roadmap pages）
- 实体: `[[future-slug]]` — why it matters, deferred because <reason>
```

The roadmap section captures items you considered but didn't finish — it
is the contract for the next ingest session.

#### Step 7 — Append to `docs/wiki/log.md`

```
## [{{date}}] ingest | bootstrap for {project_name}
- N pages written: M 实体 / X 概念 / Y 操作 / Z 对比 / W 综合
- avg page length: K words (target: ≥400 for {loc:,} LOC project)
- citation density: J source-paths per page (target: ≥3)
- arch docs cited: list of ARCHITECTURE.md / etc references used
- skipped: <list of considered-but-rejected items + brief reason>
```

#### Step 8 — Run pwiki commands

```
pwiki sync ./docs/wiki {project_name}
pwiki aliases {project_name}
pwiki canvas
```

#### Step 9 — Report to user

One short message:
- Page count by type
- One sample 源码锚点 row from a strong page (proves you read source code with line numbers)
- One [[wikilink]] cross-reference example showing the graph density
- One `pwiki query --rag "..."` question they should try first

### Ingest protocol (a new source comes in)

1. Read the new source (paper / file / commit / transcript) end-to-end.
2. Surface findings to the user briefly (3-5 bullets). Pause for steering.
3. Decide where this source's content belongs:
   - new Summary page (always — one source, one summary)
   - existing pages to *update* (mark with edit comment "[ingest 2026-MM-DD]")
   - new pages to *create* (Entity / Concept / Comparison / Synthesis)
4. Write/edit those pages. Preserve existing wikilinks.
5. Update `docs/wiki/索引.md` if you added pages.
6. Append to `log.md`:
   ```
   ## [{{date}}] ingest | <source title>
   - touched: list of page slugs
   - new: list of new page slugs
   ```
7. Run `pwiki sync ./docs/wiki {project_name}` then `pwiki aliases {project_name}`.

### Lint protocol (periodic / on demand)

Scan `docs/wiki/` and report:
- **Orphans** — pages with no incoming `[[wikilinks]]`. Fix: link from
  `索引.md` or relevant pages, or delete if low-value.
- **Stale** — pages whose `last_synced` is >90 days old AND source files
  have changed since. Mark with `> stale: <reason>` near the top.
- **Contradictions** — pages making opposing claims about the same entity.
  Surface to user; do not auto-resolve.
- **Broken wikilinks** — `[[slug]]` with no matching file or alias. Fix
  by adding the missing page or removing the dead link.
- **Citation gaps** — claims without source paths. Add citations or delete.

After scanning, write a `docs/wiki/log.md` entry:
```
## [{{date}}] lint
- orphans: N (fixed M)
- stale: N
- contradictions: N (surfaced for user review)
- broken: N (fixed)
```

### Confidence (optional but recommended)

For high-stakes pages, add a `confidence: high|medium|low` field to the
frontmatter. Decay slowly for architecture decisions; fast for transient
bugs / specific version numbers.

### Project-specific

**Vault path**: `{vault_path}`
**Project name** (`<repo>` arg in CLI): `{project_name}`

### Install / Re-init

```bash
pip install -U "pwiki-cli[rag,serve]"
pwiki init -y --vault "{vault_path}"
```

Re-running `pwiki init` is safe — the section between
`<!-- pwiki:begin -->` and `<!-- pwiki:end -->` updates in place; your
own content elsewhere in this file is preserved verbatim.

Full docs and v2 extensions (confidence, supersession, hybrid search,
hooks): https://github.com/zxs1633079383/pwiki/blob/main/docs/llm-wiki-pattern.md
"""


def render_instructions(project: dict, vault_path: str) -> str:
    arch_docs = project.get("arch_docs") or []
    if arch_docs:
        arch_docs_list = ", ".join(f"`{p}`" for p in arch_docs[:6])
        if len(arch_docs) > 6:
            arch_docs_list += f", … ({len(arch_docs)} total)"
    else:
        arch_docs_list = "_(none found — recommend adding ARCHITECTURE.md as you discover the structure)_"
    return INSTRUCTIONS_TEMPLATE.format(
        project_name=project["name"],
        vault_path=vault_path,
        loc=project.get("loc", 0),
        n_modules=project.get("n_modules", 0),
        page_range=project.get("page_range", "5-8"),
        page_target=project.get("page_target", 6),
        arch_docs_list=arch_docs_list,
    )


# 0.3.0: _llm-prompt.md is no longer generated — the AI gets the full
# LLM Wiki pattern directly from CLAUDE.md / AGENTS.md / .cursor/rules
# via the marker section. No separate file to "go read first".



# ─────────────────────────────────────── writing

PWIKI_SECTION_MARKER_BEGIN = "<!-- pwiki:begin -->"
PWIKI_SECTION_MARKER_END = "<!-- pwiki:end -->"


def write_or_inject(target: pathlib.Path, body: str, mode: str) -> str:
    """Write per the action mode. Returns 'created' / 'updated' / 'skipped'."""
    target.parent.mkdir(parents=True, exist_ok=True)
    wrapped = f"{PWIKI_SECTION_MARKER_BEGIN}\n{body}{PWIKI_SECTION_MARKER_END}\n"

    if mode == "append" and target.is_file():
        existing = target.read_text(encoding="utf-8")
        if PWIKI_SECTION_MARKER_BEGIN in existing:
            # replace existing pwiki section
            before, _, rest = existing.partition(PWIKI_SECTION_MARKER_BEGIN)
            _, _, after = rest.partition(PWIKI_SECTION_MARKER_END)
            new = before.rstrip() + "\n\n" + wrapped + after.lstrip()
            target.write_text(new, encoding="utf-8")
            return "updated"
        sep = "\n\n" if existing and not existing.endswith("\n\n") else ""
        target.write_text(existing + sep + wrapped, encoding="utf-8")
        return "appended"

    target.write_text(wrapped, encoding="utf-8")
    return "created"


def bootstrap_wiki(cwd: pathlib.Path, project_name: str) -> pathlib.Path:
    """Create a minimal docs/wiki/ tree (category dirs + index.md + log.md).

    No `_llm-prompt.md` — the AI gets the full LLM Wiki protocol from
    CLAUDE.md / AGENTS.md / .cursor/rules/pwiki.md via the marker section.
    """
    wiki = cwd / "docs" / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    for sub in ("实体", "概念", "操作", "对比"):
        (wiki / sub).mkdir(exist_ok=True)
        gitkeep = wiki / sub / ".gitkeep"
        if not gitkeep.is_file():
            gitkeep.write_text("", encoding="utf-8")

    index = wiki / "索引.md"
    if not index.is_file():
        index.write_text(
            f"# {project_name} — Wiki Index\n\n"
            f"> Auto-bootstrapped by `pwiki init`. Tell your AI agent\n"
            f"> \"fill the wiki\" / \"帮我填 wiki\" — it has the full\n"
            f"> LLM Wiki protocol in CLAUDE.md / AGENTS.md / .cursor/rules.\n\n"
            f"## 实体（Entities）\n_(empty — agent fills on first ingest)_\n\n"
            f"## 概念（Concepts）\n_(empty)_\n\n"
            f"## 操作（Operations）\n_(empty)_\n\n"
            f"## 对比（Comparisons）\n_(empty)_\n",
            encoding="utf-8",
        )

    log = wiki / "log.md"
    if not log.is_file():
        log.write_text(
            f"# {project_name} — Wiki Log\n\n"
            f"> Append-only chronological record. Each entry uses parseable\n"
            f"> prefix: `## [YYYY-MM-DD] <op> | <title>` where op is one of\n"
            f"> ingest / lint / bootstrap / decision.\n\n"
            f"## [{dt.date.today().isoformat()}] bootstrap | {project_name} wiki initialized\n"
            f"- empty scaffold; awaiting first ingest from the AI agent\n",
            encoding="utf-8",
        )
    return wiki


# ─────────────────────────────────────── interactive flow

def _ask(prompt: str, default: str = "Y", auto_yes: bool = False) -> bool:
    if auto_yes:
        return default.upper().startswith("Y")
    suffix = "[Y/n]" if default.upper().startswith("Y") else "[y/N]"
    sys.stdout.write(f"? {prompt} {suffix} ")
    sys.stdout.flush()
    try:
        ans = input().strip()
    except EOFError:
        ans = ""
    if not ans:
        return default.upper().startswith("Y")
    return ans.lower().startswith("y")


def _ask_path(prompt: str, default: str, auto_yes: bool = False) -> str:
    if auto_yes:
        return default
    sys.stdout.write(f"? {prompt} [{default}] ")
    sys.stdout.flush()
    try:
        ans = input().strip()
    except EOFError:
        ans = ""
    return ans or default


# ─────────────────────────────────────── main

def main() -> int:
    ap = argparse.ArgumentParser(
        description="One-shot setup: detect project + AI tools, write per-tool "
                    "instructions so your AI calls pwiki for you."
    )
    ap.add_argument("--cwd", default=".",
                    help="project root to initialize (default: current dir)")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT),
                    help="Obsidian Vault path (default: ~/Documents/Obsidian Vault)")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="answer Yes to all prompts (CI / scripted use)")
    ap.add_argument("--no-bootstrap", action="store_true",
                    help="skip generating docs/wiki/ scaffold even if absent")
    ap.add_argument("--no-first-run", action="store_true",
                    help="skip the first sync+canvas after writing instructions")
    ap.add_argument("--all", action="store_true", dest="force_all",
                    help="write to all 5 AI tool files even if not detected on this machine")
    ap.add_argument("--only", default=None,
                    help="comma-separated subset, e.g. --only=claude,cursor "
                         "(keys: claude, codex, gemini, cline, cursor)")
    args = ap.parse_args()
    only_set = (
        {s.strip().lower() for s in args.only.split(",") if s.strip()}
        if args.only else None
    )

    cwd = pathlib.Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        sys.exit(f"not a directory: {cwd}")

    print(f"\n🐦 pwiki init  (v{__version__})\n")
    print(f"  project root: {cwd}")

    # 1. detect project
    proj = detect_project(cwd)
    print(f"  language    : {proj['lang']}  (git: {'yes' if proj['is_git'] else 'no'})")
    modules_part = f" across {proj['n_modules']} modules" if proj['n_modules'] > 0 else ""
    print(f"  scale       : {proj['loc']:,} LOC{modules_part} → recommend {proj['page_range']} wiki pages")
    if proj.get("arch_docs"):
        print(f"  arch docs   : {', '.join(proj['arch_docs'][:3])}{' …' if len(proj['arch_docs'])>3 else ''}")
    if proj["wiki_dir"]:
        print(f"  found wiki  : {proj['wiki_dir']}")
    else:
        print(f"  found wiki  : (none — will offer to bootstrap)")

    # 2. detect AI tools
    tools = detect_ai_tools(cwd, force_all=args.force_all, only=only_set)
    print()
    print("🔍 AI agent tools detected on this machine + in this project:")
    eligible_count = sum(1 for t in tools if t["eligible"])
    for t in tools:
        if t["eligible"]:
            glyph = {"append": "✓", "create": "⚪", "create-with-parent": "⚪",
                     "skip-exists": "✓", None: "✗"}.get(t["action"], "✗")
            suffix_action = {"append": "will inject section",
                             "create": "will create",
                             "create-with-parent": "will create dir + file",
                             "skip-exists": "already has pwiki section — will update"
                             }.get(t["action"], "skip")
            suffix = f"({t['reason']}; {suffix_action})"
        else:
            glyph = "⊘"
            suffix = "(not detected — skipping; pass --all to force)"
        print(f"   {glyph} {t['tool']:<13} → {t['rel']:<30} {suffix}")

    if eligible_count == 0:
        print()
        print("⚠️  no AI tools detected on this machine.")
        print("   if you do use one, re-run with --all  or  --only=claude,cursor,gemini,codex,cline")
        sys.exit(1)

    print()
    vault_path = _ask_path("Vault path?", args.vault, args.yes)
    do_bootstrap = (
        proj["wiki_dir"] is None
        and not args.no_bootstrap
        and _ask("Bootstrap docs/wiki/ scaffold (4 category dirs + 索引.md + log.md)?", "Y", args.yes)
    )
    do_write_tools = _ask("Write pwiki instructions to AI tools above?", "Y", args.yes)
    do_first_run = (
        not args.no_first_run
        and _ask("Run first sync + canvas now?", "Y", args.yes)
    )

    # 3. bootstrap wiki
    if do_bootstrap:
        wiki = bootstrap_wiki(cwd, proj["name"])
        proj["wiki_dir"] = str(wiki)
        print(f"\n✓ created scaffold at {wiki}")
        print(f"  next: open Cursor / Claude Code / Codex / Gemini CLI in this project and say '帮我填 wiki' / 'fill the wiki'")

    # 4. write AI instructions
    written: list[tuple[str, str, str]] = []
    if do_write_tools:
        body = render_instructions(proj, vault_path)
        for t in tools:
            # 0.3.3: skip tools that aren't installed on this machine
            if not t["eligible"]:
                continue
            if t["action"] in (None, "skip-exists"):
                # skip-exists: update existing pwiki section (handled by write_or_inject append mode)
                if t["action"] == "skip-exists" and t["mode"] == "append":
                    result = write_or_inject(t["target"], body, "append")
                    written.append((t["tool"], str(t["target"].relative_to(cwd)), result))
                continue
            if t["action"] == "create-with-parent":
                t["target"].parent.mkdir(parents=True, exist_ok=True)
            if t["mode"] == "append":
                result = write_or_inject(t["target"], body, "append")
            else:
                result = write_or_inject(t["target"], body, "create")
            written.append((t["tool"], str(t["target"].relative_to(cwd)), result))
        print()
        print("✓ AI instructions written:")
        for tool, rel, result in written:
            print(f"   {result:<8} {rel}  ({tool})")

    # 5. write .pwikirc.json
    config = {
        "version": __version__,
        "project_name": proj["name"],
        "language": proj["lang"],
        "wiki_dir": proj["wiki_dir"],
        "vault_path": vault_path,
        "ai_tools_written": [t for t, _, _ in written],
        "initialized_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    rc = cwd / ".pwikirc.json"
    rc.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✓ saved {rc.relative_to(cwd)}")

    # 6. first run sync + canvas
    if do_first_run and proj["wiki_dir"]:
        print()
        print("🚀 first run — sync + aliases + canvas...")
        try:
            sync_mod = import_module("pwiki.sync")
            aliases_mod = import_module("pwiki.aliases")
            canvas_mod = import_module("pwiki.canvas")
            argv_backup = sys.argv
            sys.argv = ["pwiki sync", proj["wiki_dir"], proj["name"], "--vault", vault_path]
            sync_mod.main()
            sys.argv = ["pwiki aliases", proj["name"], "--vault", vault_path]
            aliases_mod.main()
            sys.argv = ["pwiki canvas", "--vault", vault_path]
            canvas_mod.main()
            sys.argv = argv_backup
        except SystemExit as e:
            if e.code not in (0, None):
                print(f"  (first run halted; you can rerun manually)", file=sys.stderr)
        except Exception as e:
            print(f"  (first run error: {e}; you can rerun manually)", file=sys.stderr)

    # 7. summary + next steps
    print()
    print("─" * 60)
    print("✅ pwiki init complete")
    print()
    print("🎯 you should NOT need to type pwiki commands anymore. Open your")
    print("   AI tool (Cursor / Claude Code / Codex / Gemini CLI) in this project")
    print("   and try saying:")
    print()
    print("     • '帮我填 wiki' / 'fill the wiki' — AI reads CLAUDE.md protocol, writes pages")
    print("     • 'sync the wiki'           — AI runs `pwiki sync` for you")
    print("     • '今天的早报'              — AI runs `pwiki brief` and reads §①")
    print(f"     • 'find my notes on X'      — AI runs `pwiki query --rag '...'`")
    print()
    print("   if it doesn't trigger, the AI tool's instructions file may not be")
    print("   loaded — check your tool's docs.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
