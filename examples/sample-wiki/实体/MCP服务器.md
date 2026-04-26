# MCP Server (mcp-server)

> Model Context Protocol bridge — lets LLMs (Claude, etc.) read and write the wiki.

## Tools exposed

- `wiki_query(question)` — semantic search over the wiki
- `wiki_save(note, content)` — append a new note
- `wiki_link(from, to)` — record a relationship

## Related

- [[knowledge-graph]] is the model the MCP tools operate on.
