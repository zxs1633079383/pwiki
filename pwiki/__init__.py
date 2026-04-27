"""pwiki - Karpathy's LLM Wiki, brew-install ready.

Five thin commands turn a folder into a self-maintaining knowledge base
that Claude Code (or any LLM) can reason over.

    pwiki sync <wiki_dir> <repo>     # ingest a generated wiki/ into your Vault
    pwiki aliases <repo>             # resolve [[english-slug]] to Chinese-named files
    pwiki canvas                     # render Vault → multi-repo JSON Canvas
    pwiki brief                      # build today's morning brief skeleton
    pwiki evolution                  # weekly rollup of self-evolution entries
    pwiki query "<text>"             # search Vault notes (grep + frontmatter)

The Vault layout this assumes (auto-created on first sync):

    ~/Documents/Obsidian Vault/
    ├── repos/<repo>/                # synced wiki dirs with frontmatter
    ├── daily/<YYYY-MM-DD>.md        # morning briefs
    ├── canvas/all-repos.canvas      # JSON Canvas knowledge graph
    ├── opportunities/               # promoted business hypotheses
    ├── evolution/<YYYY>-W<WW>.md    # weekly self-evolution digests
    ├── _meta/ebbinghaus.md          # spaced-repetition rules
    └── _templates/                  # daily / opportunity / repo-index

Karpathy's framing:
    "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
"""

__version__ = "0.2.1"
__all__ = ["init", "sync", "aliases", "canvas", "brief", "evolution", "query", "serve"]
