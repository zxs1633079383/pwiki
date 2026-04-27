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
## pwiki — Karpathy LLM Wiki, brew-install ready

This project uses [pwiki](https://github.com/zxs1633079383/pwiki) for
LLM-readable knowledge management. When the user makes any of the
following requests, run the corresponding command instead of writing
custom code:

| User intent (any of these phrasings) | Action |
|---|---|
| **"fill the wiki" / "帮我填 wiki" / "扫一下源码写 wiki" / "generate the wiki from my code"** — and especially when `docs/wiki/` exists but is empty/stub | **Multi-step** (see "Wiki bootstrap protocol" below) |
| "sync wiki" / "同步 wiki" / "推 wiki 到 vault" / after editing `docs/wiki/` | `pwiki sync ./docs/wiki {project_name}` |
| "解析 wikilink" / unresolved `[[slug]]` after sync | `pwiki aliases {project_name}` |
| "看图谱" / "canvas" / "knowledge graph" | `pwiki canvas` (then open `Vault/canvas/all-repos.canvas` in Obsidian) |
| "今天的早报" / "morning brief" / "今日复习" | `pwiki brief` |
| "搜笔记" / "查 X" / "what did I write about Y" / "find my notes on Z" | `pwiki query --rag "<question>"` |
| "本地启 web UI" / "看 vault 在浏览器" | `pwiki serve --open` |
| "周回顾" / "weekly evolution" | `pwiki evolution` |

**Vault path**: `{vault_path}`
**Project name** (use as `<repo>` arg): `{project_name}`

### Wiki bootstrap protocol (when the user asks "fill the wiki")

If `docs/wiki/` exists but most leaf `.md` files are empty (only frontmatter
or only category-stub `_llm-prompt.md`), follow these steps without further
prompting:

1. **Read** `docs/wiki/_llm-prompt.md` for the project-specific instructions.
2. **Read** the project's README, top-level source directory listing, and
   primary package metadata (`package.json` / `pyproject.toml` / `go.mod` /
   `Cargo.toml` / `pom.xml`). Infer the architecture in 1-2 paragraphs.
3. **Pick 5-15 significant modules / classes / flows** from the source.
   Group them as 实体 (entities) / 概念 (concepts) / 操作 (operations) /
   对比 (comparisons).
4. **Write one markdown file per item** under
   `docs/wiki/{{实体|概念|操作|对比}}/<short-chinese-name>.md`. Each file:
   - starts with `# <Title>` matching the file stem
   - 200-600 words, plain markdown, no JSX/HTML widgets
   - cite specific source paths inline (e.g. ``src/foo/bar.ts:123``) for
     every load-bearing claim
   - link related pages with `[[english-slug]]` (the slug must be a stable,
     URL-safe lowercase token; `pwiki aliases` will resolve it later)
5. **Write `docs/wiki/索引.md`** listing every page once, grouped by
   category, in the format `- [[english-slug]] — **中文名**: one-line hook`.
6. **Run** `pwiki sync ./docs/wiki {project_name}` then
   `pwiki aliases {project_name}` to push everything into the Vault.
7. **Tell the user** how many files were generated, the canvas command, and
   one suggested next question they could ask the wiki via `pwiki query --rag`.

**Quality bar**: a stranger reading the wiki should be able to answer
"what does this project do, what are its 5 main pieces, and how do they
fit together" in under 10 minutes. Pages that just paraphrase comments
or restate filenames are zero-value — skip them.

Install (if missing): `pip install -U "pwiki-cli[rag,serve]"`
Full docs: https://github.com/zxs1633079383/pwiki
"""


def render_instructions(project_name: str, vault_path: str) -> str:
    return INSTRUCTIONS_TEMPLATE.format(
        project_name=project_name,
        vault_path=vault_path,
    )


WIKI_PROMPT_TEMPLATE = """\
# LLM prompt — fill this `docs/wiki/` for project `{project_name}`

You are an AI agent (Claude / Cursor / Codex / Gemini / etc.) running in
this project's working directory. The user has just initialized pwiki and
is asking you to populate `docs/wiki/` from the source code.

> *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."*
> — Andrej Karpathy

## What to do (in order — do not skip steps)

**Step 1. Read project context.**
- `README.md` (or `README.*` if non-md) at the project root
- The package manifest: `package.json` / `pyproject.toml` / `go.mod` /
  `Cargo.toml` / `pom.xml` — whichever exists
- The top-level source directory listing (`src/`, `app/`, `lib/`, `cmd/`,
  `internal/` — whichever exists). Don't read every file; just understand the
  layout.

**Step 2. Pick 5-15 significant items.** Group them as:
- **实体 (entities)** — concrete packages / modules / classes / services
- **概念 (concepts)** — algorithms / models / abstract patterns
- **操作 (operations)** — flows / pipelines / step-by-step how-tos
- **对比 (comparisons)** — this project's choice vs the alternatives

Skip trivial items (test fixtures, generated files, third-party vendor dirs).

**Step 3. Write one markdown file per item** at
`docs/wiki/{{实体|概念|操作|对比}}/<short-name>.md`. Each file:

- Starts with `# <Title>` matching the file stem.
- 200-600 words. Plain markdown only — no JSX, HTML widgets, mermaid that
  doesn't render in plain Obsidian.
- Cite source paths inline for every load-bearing claim:
  `<src/foo/bar.ts:123>` or just `src/foo/bar.ts`.
- Link related pages using `[[english-slug]]` (the slug must be lowercase,
  URL-safe, hyphenated; pwiki's `aliases` command resolves these to the
  actual filenames you wrote).

**Step 4. Write `docs/wiki/索引.md`** that lists every page once, grouped by
category, in this exact format (one line per page):

```markdown
## 概念（Concepts）
- [[short-slug]] — **中文名**: one-line hook ≤ 80 chars
- ...

## 实体（Entities）
- [[other-slug]] — **中文名**: ...
```

**Step 5. Run pwiki commands** to push the wiki into the user's Vault:

```bash
pwiki sync ./docs/wiki {project_name}
pwiki aliases {project_name}
pwiki canvas
```

**Step 6. Tell the user** in one short message:
- How many pages you wrote (e.g. "11 pages: 4 实体 / 3 概念 / 3 操作 / 1 对比")
- One sample interesting cross-link (e.g. "`[[auth-flow]]` references `[[token-store]]`")
- One example query they can run: ``pwiki query --rag "how does X work"``

## Quality bar (skip pages that fail this)

A stranger reading your output should be able to answer in under 10 minutes:
1. What does this project do?
2. What are its 5 main pieces?
3. How do those pieces fit together?

If a page just paraphrases code comments or restates filenames, skip it.
Each page should make a non-obvious claim and back it with code citation.

## Frontmatter

`pwiki sync` adds YAML frontmatter (source_repo / last_synced /
ebbinghaus_stage etc.) automatically — you write only the body content.
"""


def render_wiki_prompt(project_name: str) -> str:
    return WIKI_PROMPT_TEMPLATE.format(project_name=project_name)


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
    """Create docs/wiki/ scaffold with category dirs and an LLM prompt."""
    wiki = cwd / "docs" / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    for sub in ("概念", "实体", "操作", "对比"):
        (wiki / sub).mkdir(exist_ok=True)
        gitkeep = wiki / sub / ".gitkeep"
        if not gitkeep.is_file():
            gitkeep.write_text("", encoding="utf-8")
    index = wiki / "索引.md"
    if not index.is_file():
        index.write_text(
            f"# {project_name} — Wiki Index\n\n"
            f"> 由 `pwiki init` 生成。让你的 LLM 读 `_llm-prompt.md` 然后填充每页。\n\n"
            f"## 概念（Concepts）\n_（空，等待 LLM 填充）_\n\n"
            f"## 实体（Entities）\n_（空，等待 LLM 填充）_\n\n"
            f"## 操作（Operations）\n_（空，等待 LLM 填充）_\n\n"
            f"## 对比（Comparisons）\n_（空，等待 LLM 填充）_\n",
            encoding="utf-8",
        )
    prompt = wiki / "_llm-prompt.md"
    if not prompt.is_file():
        prompt.write_text(render_wiki_prompt(project_name), encoding="utf-8")
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
