# pwiki Architecture

One sentence: **pwiki is five thin Python modules around one shared assumption — your Obsidian Vault is the source of truth, and every file's YAML frontmatter is the contract.**

## The Vault contract

pwiki creates and reads this layout:

```
~/Documents/Obsidian Vault/        # configurable via --vault on every command
├── .obsidian/                     # Obsidian's own config; pwiki never touches
├── repos/<name>/                  # one folder per ingested wiki
│   ├── _index.md                  # auto-generated; do not hand-edit
│   └── …                          # mirrored .md files with managed frontmatter
├── daily/<YYYY-MM-DD>.md          # morning briefs
├── canvas/all-repos.canvas        # JSON Canvas v1.0
├── opportunities/                 # promoted business / project hypotheses
├── evolution/<YYYY>-W<WW>.md      # weekly self-evolution digests
├── _meta/                         # rules referenced by morning-brief
│   └── ebbinghaus.md
└── _templates/                    # used by sync + brief + opportunity creation
    ├── daily.md
    ├── opportunity.md
    └── repo-index.md
```

Every command can be re-pointed at a different Vault with `--vault PATH` or by setting `OBSIDIAN_VAULT` in env. Default path is `~/Documents/Obsidian Vault` (matches Obsidian's own default).

## The frontmatter contract

Every note pwiki writes has a YAML frontmatter block with these fields:

```yaml
---
source_repo: GitNexus              # which repo this came from (managed by sync)
source_path: 概念/影响范围.md       # original path in the source wiki (managed by sync)
last_synced: 2026-04-26            # ISO date of last sync (managed by sync)
ebbinghaus_stage: 0                # 0..6, increases on review-success (managed by brief)
last_reviewed: 2026-04-26          # ISO date of last review (managed by brief)
tags: [repo/GitNexus, 概念]         # auto-tag for category + repo
aliases: [blast-radius]            # added by `pwiki aliases` to resolve wikilinks
---
```

`pwiki sync` is conservative: it merges new fields into existing frontmatter, never overwrites human-edited fields except `last_synced`.

`pwiki aliases` only adds; never removes existing aliases.

## The five modules

### `pwiki sync`
Mirrors `<source>/*.md` → `Vault/repos/<repo>/`. For each file, parses existing frontmatter (if any), merges in `source_repo`, `source_path`, `last_synced`. If new file, also seeds `ebbinghaus_stage=0`, `last_reviewed=today`, `tags`. Re-renders `_index.md` from `_templates/repo-index.md`. **Never modifies the body text.**

### `pwiki aliases`
Solves the "wiki uses English slugs but files use Chinese (or other) names" problem. Reads `repos/<repo>/索引.md` (or `index.md`), extracts `[[slug]] — name` pairs, then matches each `slug` to the actual file by:
1. Filename stem exact / contains match against the parsed Chinese name
2. H1 heading match
3. EN→ZH token dictionary match (e.g. `mcp-server` → `mcp` + `server` → `MCP服务器`)

Unmatched slugs are reported but not fabricated. Handles GitNexus-style wikis with 100% match rate.

### `pwiki canvas`
Renders `Vault/repos/` → `Vault/canvas/all-repos.canvas` (JSON Canvas 1.0). Each repo becomes a labeled group node in a 3-per-row grid. Each note is a file node arranged in a √N grid inside its group. **Edges resolve through aliases** — so `[[blast-radius]]` from one repo correctly draws an edge to `repos/GitNexus/概念/影响范围.md` if that file declared `aliases: [blast-radius]`.

The output is regenerated wholesale every run. If you've manually arranged a canvas in Obsidian, save it under a different filename.

### `pwiki brief`
Builds today's morning brief at `Vault/daily/<today>.md`:
- **§① Review queue**: scans every file under `repos/`, computes `today >= last_reviewed + interval(stage)` per `_meta/ebbinghaus.md`, lists due notes.
- **Materials block**: collects last N days of git log (`--lookback-days`, default 7) from every git repo found under `~/workspace` (or configurable `--repos-root`). Identifies today's quadrant by `weekday()`.
- **§②③④ scaffolding**: pre-fills §① with real data, leaves §②③④ as a structured template for an LLM to populate in-place.

The script writes deterministic output. The LLM (you, in your editor or in Claude Code) fills the rest from the materials block.

### `pwiki evolution`
On Sunday — or any day with `--week-of YYYY-MM-DD` — reads the past 7 days of `daily/<date>.md`, extracts each `## ④ 自我演进` block, groups by quadrant (思维 / 知识宽度 / 产品视野 / 创业 & 风投), writes `Vault/evolution/<YYYY>-W<WW>.md`.

Carries entries verbatim. Never paraphrases. The point is to preserve the original "concrete + verifiable" voice of each entry.

## Composition

The five modules are intentionally orthogonal:

| Reads from | Writes to | Module |
|---|---|---|
| Source wiki dir | `Vault/repos/<repo>/` | `sync` |
| `Vault/repos/<repo>/` | Same files (frontmatter only) | `aliases` |
| `Vault/repos/` | `Vault/canvas/all-repos.canvas` | `canvas` |
| `Vault/repos/` + `~/workspace/*` git logs | `Vault/daily/<today>.md` | `brief` |
| `Vault/daily/*.md` | `Vault/evolution/<YYYY>-W<WW>.md` | `evolution` |

You can run any subset, in any order, idempotently. `pwiki canvas` works on whatever's in `repos/` right now. `pwiki brief` doesn't require sync to have run today.

## Sync (multi-device, optional)

pwiki itself is single-machine. For multi-device:

- **[Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync)** — recommended. CouchDB backend, real-time bidirectional, ~5s file propagation in our measurements.
- **[Obsidian Sync](https://obsidian.md/sync)** — $10/month, zero ops.
- **[Obsidian Git](https://github.com/Vinzent03/obsidian-git)** — git-based, simple but conflict-prone for two simultaneous editors.

pwiki's roadmap 0.4 will provide a one-click LiveSync deploy (Fly.io + Cloudflare Tunnel) to remove the CouchDB-config friction.

## What pwiki is *not*

- Not a Notion replacement. It's a CLI that ferries LLM-generated wikis into a vault you already own.
- Not RAG. Karpathy's pattern compiles knowledge ahead of time into structured markdown; the LLM reasons over the wiki at query-time. RAG retrieves chunks at query-time. Different architectures.
- Not a wiki generator. pwiki ingests wikis you've already generated (with Claude Code, autoReSearch, llm-wiki-knowledge, deep-wiki, or any LLM that produces markdown).
- Not multi-tenant or multi-user. That's the team SaaS roadmap, not v0.x.
