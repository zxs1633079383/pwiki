# LLM Wiki Pattern — Full Reference

> The compact summary lives in your project's `CLAUDE.md` / `AGENTS.md` /
> `.cursor/rules/pwiki.md` (auto-written by `pwiki init`). This file is
> the deeper reference for v2 extensions and edge cases.

## Origin

Andrej Karpathy posted the [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
on April 1, 2026. Hit Hacker News front page (294 pts, 92 comments).
Multiple OSS implementations within 48 hours.

> *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."*

## Three-Layer Architecture

| Layer | Mutability | Holds | Lives at |
|---|---|---|---|
| Raw     | strictly immutable | source documents, code, transcripts | the project tree itself |
| Wiki    | mutable, LLM-maintained | summary / entity / concept / comparison / synthesis pages | `docs/wiki/` |
| Schema  | semi-mutable, human + LLM co-evolve | conventions, workflows, page types | `CLAUDE.md` / `AGENTS.md` / `docs/wiki/索引.md` / `docs/wiki/log.md` |

Compile knowledge into Wiki once → the LLM stops re-discovering it on every
query. Knowledge accumulates instead of evaporating.

## Three Core Operations

### Ingest

User adds a new source. Agent:

1. Reads the source end-to-end.
2. Discusses findings (3-5 bullets), pauses for steering.
3. Writes a Summary page (one source, one summary).
4. Updates / creates Entity / Concept / Comparison / Synthesis pages.
5. Revises `索引.md`.
6. Appends to `log.md` with parseable prefix:
   `## [2026-04-15] ingest | <source title>`
7. Runs `pwiki sync` to push to Vault.

One ingest typically touches 5-15 pages.

### Query

User asks a question. Agent:

1. Searches relevant wiki pages (`pwiki query --rag` for semantic).
2. Synthesizes answer with `[[wikilink]]` citations.
3. **If the question is high-value**, files the synthesized answer back
   as a permanent Synthesis page. Treats explorations as sources.

### Lint

Periodic / on demand. Agent scans for:

- **Orphans** — pages with no incoming `[[wikilinks]]`. Fix: link from
  `索引.md` or delete if low-value.
- **Stale** — pages where `last_synced` is >90d old AND source files
  changed. Mark with `> stale: <reason>`.
- **Contradictions** — opposing claims about the same entity. Surface,
  don't auto-resolve.
- **Broken wikilinks** — `[[slug]]` with no matching file/alias. Add or
  remove.
- **Citation gaps** — claims without source paths. Add or delete.

Logs to `log.md`:
```
## [2026-04-15] lint
- orphans: 3 (fixed 2)
- stale: 5
- contradictions: 1 (surfaced)
- broken: 0
```

## Page Types

| Type | Folder | Holds |
|---|---|---|
| Summary    | `概要/` (optional) | one source distilled |
| Entity     | `实体/` | concrete things: packages, classes, services, products, people |
| Concept    | `概念/` | algorithms, models, abstract patterns, design principles |
| Operation  | `操作/` | flows, pipelines, runbooks, how-tos |
| Comparison | `对比/` | tradeoff tables: this vs that |
| Synthesis  | `综合/` | thesis pages: "what we believe and why" |

Pages connect via `[[english-slug]]` wikilinks. `pwiki aliases` resolves
slugs to whatever filename actually holds the page (Chinese, mixed, etc).

## Immutability Rules

| Layer | Rule |
|---|---|
| Raw | Never edit. Reference by path. |
| Wiki | LLM-maintained. Human can hand-edit, the LLM treats hand edits as authoritative on next ingest. |
| Schema | Co-evolves. New page type? Update CLAUDE.md and the Wiki together in the same session. |

## Key Files

### `docs/wiki/索引.md`

Content-oriented catalog. Auto-updated on every ingest. One line per
page, grouped by type:

```markdown
## 实体（Entities）
- [[short-slug]] — **中文名**: one-line hook ≤ 80 chars
- [[other-slug]] — **中文名**: ...

## 概念（Concepts）
- [[concept-slug]] — **中文名**: ...
```

### `docs/wiki/log.md`

Append-only chronological record. Parseable prefixes:
```
## [YYYY-MM-DD] ingest | <title>
## [YYYY-MM-DD] lint
## [YYYY-MM-DD] bootstrap | <project_name>
## [YYYY-MM-DD] decision | <choice>
```

The log lets future-you reconstruct *when* knowledge entered the wiki and
*why* — irreplaceable when reviewing months later.

### `CLAUDE.md` / `AGENTS.md` / `.cursor/rules/pwiki.md`

The Schema. Defines page types, naming rules, workflow steps, quality
standards, contradiction handling. Co-evolves with operator experience.

## Quality Bar

A stranger reading the wiki should answer in 10 minutes:

1. What does this project do?
2. What are its 5 main pieces?
3. How do those pieces fit together?

If a page just paraphrases code comments or restates filenames, **delete
it**. Each page must make a non-obvious claim and back it with a source
path citation.

## v2 Extensions (Roadmap)

### Confidence Scoring

Each fact carries a confidence (0-1) tracking source count, recency,
contradictions. Decays temporally; strengthens via reinforcement.

```yaml
---
title: Auth Flow
confidence: 0.85   # 4 sources, 2 weeks old, 0 contradictions
last_reinforced: 2026-04-10
---
```

Architecture decisions decay slowly. Transient bugs decay fast.

### Supersession (version control for knowledge)

```yaml
---
supersedes: [old-auth-flow-v1, old-auth-flow-v2]
superseded_by: null
---
```

New info explicitly replaces old. Timestamped. Version-linked.

### Forgetting (Ebbinghaus Decay)

stage 0 → +1d, stage 1 → +3d, stage 2 → +7d, stage 3 → +15d, stage 4 →
+30d, stage 5 → +60d, stage 6+ → +120d. Successful review increments
stage; failed review resets to `max(0, stage-1)`. `pwiki brief` surfaces
due-for-review pages each morning.

### Consolidation Tiers (Memory Pyramid)

```
Working ─→ Episodic ─→ Semantic ─→ Procedural
(low compression, low confidence)   (high compression, high confidence)
```

Routine information climbs the pyramid; one-off events stay in Episodic
and decay.

### Typed Relationships

Replace generic `[[wikilink]]` with semantic types:

```markdown
[[redis|uses]]
[[postgres|depends-on]]
[[mongodb|contradicts]]
[[old-cache|supersedes]]
```

Enables graph traversal: "what breaks if we upgrade Redis?" → walk
`uses` and `depends-on` edges from `[[redis]]`.

### Hybrid Search (3 streams)

BM25 (keyword) + Vector (semantic, fastembed multilingual MiniLM) +
Graph (relationship traversal) → fused via Reciprocal Rank Fusion.
`pwiki query --rag` already gives you the semantic stream.

### Automation Hooks

| Trigger | Hook |
|---|---|
| `on new source` | auto-ingest |
| `on session start` | context loading from `索引.md` |
| `on session end` | compression / consolidation |
| `on query` | answer filing if high-value |
| `on memory write` | contradiction detection |
| `on schedule` | weekly lint, monthly consolidation, daily decay |

## Critical Limits

- **Context pollution**: ~200 pages / ~400K tokens practical ceiling.
  Selective loading via `索引.md` is key — never load whole wiki into
  context.
- **Error propagation**: wrong wiki entries contaminate downstream
  queries. Mitigate with confidence scoring + regular lint + vault
  separation per project.
- **Self-healing lint** (v2) auto-corrects (links orphans, marks stale,
  fixes broken refs); v1 is suggestion-only.

## Scaling Beyond ~400K Words

| Scale | Approach |
|---|---|
| <100 pages | `索引.md` is the index |
| 100-200 | add qmd or `pwiki query --rag` (BM25 + vector) |
| >200 | split into sub-wikis (one per project repo); `pwiki canvas` shows the cross-wiki graph |
| >1000 sources | hybrid: LLM Wiki for core + LlamaIndex/GraphRAG for long tail |

## RAG vs LLM Wiki Decision Matrix

| Choose RAG when... | Choose LLM Wiki when... |
|---|---|
| 1000+ documents | 10-200 documents |
| Real-time updates needed | Knowledge should accumulate |
| One-off queries | Repeated deep exploration |
| Multi-tenant | Personal / small team |

They are complementary. Once `docs/wiki/` is large, layer RAG
(`pwiki query --rag`) on top of it.

## Multi-Agent Collaboration (Roadmap)

- Mesh sync: parallel agent observations merge.
- Conflict resolution: last-write-wins + timestamp.
- Scoping: shared vs private; private can promote to shared via Synthesis.

## Schema as Product

The Schema document (CLAUDE.md / AGENTS.md) is the system's true value.
It encodes domain entity / relationship types, ingest workflows, quality
standards. Transferable across similar domains. Sharable as the
"operational manual" for your project's wiki.

## References

- [Karpathy's gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the original idea file (April 2026)
- [HN discussion](https://news.ycombinator.com/) — 294 pts, 92 comments
- [pwiki repo](https://github.com/zxs1633079383/pwiki) — this project
- [Vannevar Bush's Memex (1945)](https://en.wikipedia.org/wiki/Memex) — the philosophical root
