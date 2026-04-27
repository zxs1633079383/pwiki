"""pwiki init — first-time setup that aims for 100% automation.

What it does (in order):
  1. Detect project metadata (language, git, existing docs/wiki).
  2. Detect AI agent tooling (CLAUDE.md, AGENTS.md, .cursor/, GEMINI.md, .clinerules).
  3. Ask 4 yes/no questions (defaults reasonable so just `pwiki init -y` works).
  4. Write per-tool instructions so the user's AI can call pwiki without manual CLI.
  5. Bootstrap docs/wiki/ if absent: minimal scaffold + an `_llm-prompt.md` the
     user pastes into their AI to fill in real content.
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

def detect_project(cwd: pathlib.Path) -> dict:
    info = {"path": str(cwd), "lang": "unknown", "name": cwd.name,
            "is_git": (cwd / ".git").is_dir(), "wiki_dir": None}
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


def detect_ai_tools(cwd: pathlib.Path) -> list[dict]:
    """For each known tool, decide whether we WILL/CAN write to it."""
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
        out.append({"tool": name, "rel": rel, "target": target,
                    "mode": mode, "action": action})
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
| "今天的早报" / "morning brief" | `pwiki brief` |
| "搜笔记" / "查 X" / "find my notes on Z" | `pwiki query --rag "<question>"` |
| "本地启 web UI" | `pwiki serve --open` |
| "周回顾" / "weekly evolution" | `pwiki evolution` |

### Bootstrap protocol (empty `docs/wiki/`, first time)

1. Read `README*` + package manifest (`package.json` / `pyproject.toml` /
   `go.mod` / `Cargo.toml` / `pom.xml`) + top-level source directory listing.
   Infer the architecture in 1-2 internal paragraphs (don't write yet).
2. Identify 5-15 significant items from the codebase. Classify each as
   Entity / Concept / Operation / Comparison. Skip vendored code, generated
   files, test fixtures, third-party libs.
3. **Create the wiki tree** if missing: `docs/wiki/{{实体,概念,操作,对比}}/`.
4. For each item, write **one** markdown file:
   - filename: `<short-chinese-or-english-stem>.md`
   - body starts with `# <Title>` (matching stem)
   - 200-600 words, plain markdown only (no JSX, no HTML widgets, no
     mermaid that won't render in vanilla Obsidian)
   - **every load-bearing claim cites a source path inline**: `src/foo/bar.ts:123`
     or just `src/foo/bar.ts`. No citation = delete the sentence.
   - link related pages with `[[english-slug]]`
   - **must make at least one non-obvious claim** — pages that paraphrase
     comments / restate filenames are zero-value, skip them
5. Write `docs/wiki/索引.md` (the index) listing every page once, grouped
   by type, format:
   ```
   ## 实体（Entities）
   - [[short-slug]] — **中文名**: one-line hook ≤ 80 chars
   ## 概念（Concepts）
   - [[other-slug]] — **中文名**: ...
   ```
6. Append to `docs/wiki/log.md` (create if absent):
   ```
   ## [{{date}}] bootstrap | initial wiki for {project_name}
   N pages: {{count by type}}
   ```
7. Run `pwiki sync ./docs/wiki {project_name}` then `pwiki aliases {project_name}`.
8. Tell the user: count of pages by type, one interesting cross-link, one
   example query they can run via `pwiki query --rag "..."`.

**Bootstrap quality bar**: a stranger reading your output should be able
to answer in under 10 minutes — what does this project do, what are its
5 main pieces, how do they fit together. If a page fails this, delete it.

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


def render_instructions(project_name: str, vault_path: str) -> str:
    return INSTRUCTIONS_TEMPLATE.format(
        project_name=project_name,
        vault_path=vault_path,
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
    args = ap.parse_args()

    cwd = pathlib.Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        sys.exit(f"not a directory: {cwd}")

    print(f"\n🐦 pwiki init  (v{__version__})\n")
    print(f"  project root: {cwd}")

    # 1. detect project
    proj = detect_project(cwd)
    print(f"  language    : {proj['lang']}  (git: {'yes' if proj['is_git'] else 'no'})")
    if proj["wiki_dir"]:
        print(f"  found wiki  : {proj['wiki_dir']}")
    else:
        print(f"  found wiki  : (none — will offer to bootstrap)")

    # 2. detect AI tools
    tools = detect_ai_tools(cwd)
    print()
    print("🔍 AI agent tools in this project:")
    for t in tools:
        glyph = {"append": "✓", "create": "⚪", "create-with-parent": "⚪",
                 "skip-exists": "✓", None: "✗"}.get(t["action"], "✗")
        suffix = {"append": "(will inject section)",
                  "create": "(will create)",
                  "create-with-parent": "(will create dir + file)",
                  "skip-exists": "(already has pwiki section — will update)"
                  }.get(t["action"], "(skip)")
        print(f"   {glyph} {t['tool']:<13} → {t['rel']:<30} {suffix}")

    print()
    vault_path = _ask_path("Vault path?", args.vault, args.yes)
    do_bootstrap = (
        proj["wiki_dir"] is None
        and not args.no_bootstrap
        and _ask("Bootstrap docs/wiki/ scaffold + LLM prompt?", "Y", args.yes)
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
        print(f"  next: open _llm-prompt.md in Cursor/Claude/Codex and let your AI fill the pages")

    # 4. write AI instructions
    written: list[tuple[str, str, str]] = []
    if do_write_tools:
        body = render_instructions(proj["name"], vault_path)
        for t in tools:
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
    print("     • 'help me fill docs/wiki' — AI reads _llm-prompt.md, generates pages")
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
