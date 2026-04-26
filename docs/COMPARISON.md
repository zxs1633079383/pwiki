# pwiki vs the other Karpathy LLM Wiki implementations

In the 30 days since Andrej Karpathy posted his [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (April 2026), at least six community implementations have appeared. Here's how they relate, and where pwiki fits.

## TL;DR

| | Install | Multi-repo | JSON Canvas | Daily brief | Cross-repo wikilinks | Status |
|---|---|---|---|---|---|---|
| **pwiki** | `pip install pwiki` | ✅ | ✅ | ✅ | ✅ alias-resolved | OSS, this repo |
| Karpathy gist | copy-paste prompt | — | — | — | — | reference |
| Ar9av/obsidian-wiki | clone + Claude skill | ✅ | — | — | — | OSS |
| AgriciDaniel/claude-obsidian | clone + slash commands | single | — | — | — | OSS |
| NicholasSpisak/second-brain | clone + Claude skill | single | — | — | — | OSS |
| DeepWiki (Cognition) | URL only, hosted | single | — | — | — | hosted, read-only |
| Obsidian Sync | paid SaaS | n/a | n/a | n/a | n/a | $10/mo, generic sync |

## What each one is, in one paragraph

### Karpathy's [original gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
The pattern. A 200-line prompt that turns Claude Code into an LLM that maintains a markdown wiki for you, with three slash commands: `/wiki`, `/save`, `/autoresearch`. **Strength**: pure, hackable, zero infrastructure. **Limit**: you copy-paste the prompt into your project; managing 5+ projects becomes 5+ copy-pastes; no cross-project graph; no daily review; no spaced repetition.

### [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)
A skill-based framework that codifies Karpathy's pattern as Claude skills with a proper Raw → Wiki → Schema lint pipeline. **Strength**: clean separation of source vs distilled vs schema. **Limit**: still single-vault, single-repo focus; no graph rendering; needs you to clone and configure the skill.

### [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
Karpathy's pattern + autoresearch loop. Scans web for sources, distills them into the vault. **Strength**: the autoresearch is a real differentiator if you're building a knowledge base from public sources. **Limit**: tightly coupled to Claude Code's slash command UX; harder to use outside that workflow.

### [NicholasSpisak/second-brain](https://github.com/NicholasSpisak/second-brain)
Personal vault skill set focused on the read/save loop. **Strength**: minimal, follows Karpathy's gist closely. **Limit**: single-repo; no Canvas, no daily brief.

### [DeepWiki](https://deepwiki.com) (Cognition)
Hosted service that scans any GitHub repo and generates a wiki you can chat with. **Strength**: zero install, instant gratification, URL-as-feature for sharing. **Limit**: read-only, single repo, regenerated wholesale (no commit-rooted "rolling" updates), can't sink your own decisions back in. **Different category** — DeepWiki is "explore someone else's code"; pwiki is "compound your own knowledge over time."

### [Obsidian Sync](https://obsidian.md/sync)
Generic encrypted multi-device sync from the Obsidian team. Doesn't generate wikis, doesn't reason about your content. Solves the "I edit on laptop and want it on phone" problem only. **Complementary to pwiki**, not a competitor.

## When to choose pwiki

- You have **multiple repos** with generated wikis (or want to). pwiki's `repos/<name>/` layout was built for this.
- You want a **visual graph** across all repos. JSON Canvas + alias-resolved wikilinks give you that out of the box.
- You want **spaced repetition + daily review** integrated. The brief command + Ebbinghaus frontmatter contract handle this with no extra plugins.
- You want **install in 10 seconds**. `pip install pwiki` then run.

## When to choose something else

- You want a **single-prompt setup** that works with any markdown editor. Use Karpathy's gist directly.
- You want **research-from-the-web** to drop straight into your vault. Use `claude-obsidian`'s autoresearch.
- You want a **hosted, no-install experience** for a public repo. Use DeepWiki.
- You want **encrypted multi-device sync**. Pair pwiki with Obsidian Sync or [Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync).

## Combining pwiki with others

These compose well:

- **pwiki + Karpathy's gist**: use the gist's `/wiki` and `/save` slash commands inside Claude Code to generate `<repo>/wiki/`, then `pwiki sync <repo>/wiki <repo>` to ferry the result into your central Vault.
- **pwiki + Self-hosted LiveSync**: pwiki writes to `Vault/`, LiveSync syncs `Vault/` to CouchDB to phone/tablet. We've measured ~5s propagation per file.
- **pwiki + obsidian-skills (kepano)**: the [obsidian-skills](https://github.com/kepano/obsidian-skills) collection (`obsidian-cli`, `obsidian-bases`, `json-canvas`, `defuddle`) plays nicely with pwiki — pwiki produces the data, obsidian-skills are how you query it from agents.

## Honest weak points (where pwiki loses)

- **No autoresearch**: pwiki ingests wikis, doesn't generate them from web sources. Use `claude-obsidian` for that, then sync the output with pwiki.
- **No public sharing UX**: DeepWiki's `deepwiki.com/owner/repo` is a great share-with-strangers feature pwiki has no answer for (and won't, in v0.x).
- **Wikilink resolution is heuristic**: pwiki's EN→ZH token dictionary handles GitNexus-style wikis with 100% match rate, but a wiki with totally different naming conventions might need manual `aliases:` curation.
- **Single-machine in v0.x**: hosted version (LiveSync-as-a-service) is on the 0.4 roadmap.

If pwiki doesn't fit your shape, one of the projects above will. The community is small enough that all six maintainers know about each other; nobody's fighting for a market — there is no market yet, only an emerging pattern.
