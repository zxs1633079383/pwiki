# Changelog

All notable changes to pwiki will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
