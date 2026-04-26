# LadybugDB (ladybugdb)

> Local-first storage with WAL + single-writer lock. Designed for LLM-maintained wikis.

## Properties

- Append-only WAL for crash safety.
- Single writer, many readers — perfect for an LLM that mostly appends.
- Embedded in the user's filesystem; no daemon, no cloud.

## Related

- [[knowledge-graph]] uses LadybugDB as backing store.
