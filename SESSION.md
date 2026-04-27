# SESSION.md — 2026-04-26 → 2026-04-27 build session

> One-night session: built the full Obsidian-Vault knowledge system AND
> shipped pwiki v0.1 → 0.3 (OSS) + 0.4 spec to a public GitHub repo.
> This file is the post-mortem so the next session resumes without re-deriving context.

## Timeline (≈9.5 hours)

| Local time | Phase | Output |
|---|---|---|
| 19:00–19:30 | Obsidian system scoping | Decision: LiveSync (CouchDB) + 4 skills |
| 19:30–20:00 | CouchDB Docker bring-up | container `obsidian-livesync` healthy, CORS configured |
| 20:00–20:30 | Vault skeleton + GitNexus import | 33 wiki files synced, frontmatter added |
| 20:30–21:30 | obsidian-bridge / morning-brief / vault-canvas / evolution-tracker skills | each `~/.claude/skills/<name>/SKILL.md + .py` |
| 21:30–22:00 | LiveSync setup (user) | wizard cancelled wrong path, manual Remote DB config worked |
| 22:00–22:30 | Verify sync (write file → CouchDB ≤5s) | doc_count 506, size 812KB |
| 22:30–23:00 | CLAUDE.md 早安段升级 + memory dump | obsidian-vault-system.md memory written |
| 23:00–23:50 | aliases EN→ZH dict (Pass 3) + canvas alias-aware index | 130 wikilinks resolved, only 2 unresolved |
| 23:50–00:30 | last30days-cn + last30days WebSearch ×5 → 10 market-driven directions | rewrote `daily/2026-04-26.md` + `opportunities/pwiki.md` |
| 00:30–02:30 | pwiki v0.1.0 — package, README, vhs demo.gif, GitHub push | https://github.com/zxs1633079383/pwiki |
| 02:30–04:00 | 中文 launch-tweet 4 平台版 + RELEASE.md + scripts/release.sh | docs/launch-tweet-zh.md |
| 04:00–05:00 | Disk cleanup (background agent) | net 12GB recovered (gradle 7G + npm 3.8G + Docker 4.9G) |
| --- next day --- | | |
| 00:00–00:15 | 0.2-A: aliases Pass 4 (English filenames) + `--dict` | en-demo 3/3 match |
| 00:15–00:30 | 0.2-B: pwiki query (grep + frontmatter rank) | 10 tests pass; real "blast" → 5 hits |
| 00:30–01:00 | 0.2-C: pwiki query --rag via fastembed multilingual MiniLM | 235 chunks → 352KB index; mixed-lang queries work |
| 01:00–01:30 | 0.3-A/B: pwiki serve FastAPI + D3 Canvas inline | /api/canvas.json → 42 nodes / 130 edges |
| 01:30–01:45 | 0.4-spec: hosted SaaS architecture | docs/0.4-hosted-spec.md (gated on ⭐ ≥ 300) |
| 01:45–02:00 | CLAUDE.md + SESSION.md (this file) | shipping the post-mortem |

## What got built (final state)

### Personal infrastructure (`~/Documents/Obsidian Vault/`)
- 50+ notes synced from GitNexus + mattermost + LatticeAI
- daily/2026-04-26.md (4-section morning brief, market-driven version)
- canvas/all-repos.canvas (130 cross-repo wikilink edges)
- opportunities/pwiki.md (4-week kill criteria, 2026-05-24 decision day)
- evolution/2026-W17.md (weekly digest stub)
- _meta/ebbinghaus.md, _templates/{daily,opportunity,repo-index}.md

### CouchDB (`~/.obsidian-livesync/`)
- docker-compose.yml + .env (chmod 600) + init-couchdb.sh
- container `obsidian-livesync`, port 127.0.0.1:5984, ~5s file propagation
- ~876 docs / 1.5MB at session end

### Skills (`~/.claude/skills/`)
- obsidian-bridge / morning-brief / vault-canvas / evolution-tracker
- Each has SKILL.md + .py and works via the Skill tool in Claude Code

### CLAUDE.md modifications (`~/.claude/CLAUDE.md`)
- 早安复盘 (Step 3) extended with Steps 1-3:
  Step 1: log retro from /workspace/java/logs/
  Step 2: morning-brief skill (4 sections)
  Step 3: Sunday evolution-tracker
- Ebbinghaus state-machine update rule (success → stage++; unfamiliar → max(0, stage-1))

### pwiki public repo (https://github.com/zxs1633079383/pwiki)
5 commits, 34 tracked files, 1.6MB:

| Commit | What |
|---|---|
| `f0ee825` | v0.1.0: 5-command CLI + JSON Canvas + Ebbinghaus + weekly evolution + demo.gif (348KB / 44s) |
| `991c7c7` | docs: 中文文案 + RELEASE.md + scripts/release.sh |
| `1a122e1` | 0.2-A aliases Pass 4 + 0.2-B pwiki query (grep) |
| `b69de43` | 0.2-C pwiki query --rag (fastembed multilingual MiniLM) |
| `1826742` | 0.3 pwiki serve (FastAPI + D3 Canvas) + docs/0.4-hosted-spec.md |

## Key decisions and why

| Decision | Pick | Reason |
|---|---|---|
| Sync mode | Self-hosted LiveSync | Real-time bidirectional; user already has Docker |
| GitHub username | `zxs1633079383` (not `zlc`) | the user's actual GitHub handle; README, pyproject, launch-tweet all updated |
| Embedding stack | fastembed (ONNX) over sentence-transformers (torch) | ~10x smaller install (220MB vs 2GB), no torch ecosystem hell |
| Embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384-dim) | mixed Chinese/English vault; intfloat/multilingual-e5-small isn't supported by fastembed 0.8 |
| Web framework | FastAPI + jinja-free inline templates | maintainer dogfoods Python; D3 from CDN avoids npm |
| 0.4 implementation | NOT NOW | gated on ⭐ ≥ 300 + 5 hosted-version asks; premature SaaS = named anti-pattern |
| OSS model | freemium with funnel | CLI free forever (Karpathy gist + 6 OSS make CLI paywalls dead); $9/mo Hosted Pro replaces CouchDB ops; $29/seat Team Pro for 5+ teams |
| Demo recording | vhs (charmbracelet) | declarative .tape, GIT-friendly, repeatable |
| Disk cleanup | background general-purpose agent | non-blocking, zero context cost |

## Validation evidence (so we don't doubt it later)

- ✅ `pwiki --version` → 0.1.0 in venv
- ✅ all 7 subcommand `--help` work via dispatcher
- ✅ 10 smoke tests pass in 0.47s (`pytest -q`)
- ✅ demo run on `/tmp/demo-vault`: sync 4 → aliases 3/3 → canvas 5 nodes / 7 edges → brief OK
- ✅ real GitNexus run: sync 33 → aliases 30/30 → canvas 33 nodes / 127 edges
- ✅ RAG: "什么是爆炸半径分析" → sim=0.546 hits `repos/GitNexus/概念/影响范围.md` H1 "爆炸半径分析（Blast Radius）— 深度分组与置信度"
- ✅ `pwiki serve` boots, `/healthz` returns vault path, `/api/canvas.json` returns 42 nodes / 130 edges
- ✅ LiveSync round-trip: write smoke file → CouchDB doc visible in 5s
- ✅ 5 git commits all pushed to origin/main

## What's NOT done (and why)

| Item | Why not | When |
|---|---|---|
| PyPI publish | maintainer hasn't created token yet | next maintainer login → `~/.pypirc` + `bash scripts/release.sh` |
| Twitter post | maintainer's call (英中文案 ready) | 周二 9-11am EST 英文 + 22:00 CST 中文 |
| 0.4 implementation | gated on ⭐ ≥ 300 | 2026-05-24 decision day |
| demo.gif re-record (with serve) | serve is bg process, harder to record cleanly | post-launch when there's value to add a UI demo |
| `pwiki query` hybrid (grep + RAG blended) | nice-to-have, not v0.x | 0.5+ |
| `pwiki serve` reload mode QA | --reload flag exists, didn't fully QA | when someone files an issue |

## Death conditions to watch (from `opportunities/pwiki.md`)

Trigger any → kill current direction:

- [ ] Week 1 end (2026-05-03): GitHub ⭐ < 50 → README/hook didn't catch
- [ ] Week 2 end (2026-05-10): Twitter thread < 100 likes / < 10 RT → market not interested
- [ ] Week 2 end (2026-05-10): 14 days self-use, < 2 things promoted to `opportunities/` → tool itself useless
- [ ] Week 4 end (2026-05-24): a competitor ships a CLI version of Karpathy's gist → window closed
- [ ] Any time: Karpathy publishes an official CLI → fork into upstream

## Resume next session

In any new session, the maintainer (or Claude Code) can resume by:

1. Reading the two memory files:
   - `~/.claude/projects/-Users-mac28-workspace-ai-workspace-obsidian/memory/obsidian-vault-system.md`
   - `~/.claude/projects/-Users-mac28-workspace-ai-workspace-obsidian/memory/pwiki-launch.md`
2. Reading this file (`SESSION.md`) for the chronological narrative.
3. Reading `CLAUDE.md` for project conventions and don'ts.
4. Reading `~/Documents/Obsidian Vault/opportunities/pwiki.md` for the 4-week kill criteria.
5. Running `git log --oneline` to see what's shipped vs the spec.

Default first-action when "continue pwiki": check star count + scan GitHub Issues + decide whether to keep 0.x improvements going or jump to 0.4 implementation gate.

## One-line summary

> **Tonight: built a Karpathy-LLM-Wiki-pattern OSS CLI from scratch, validated it on 50+ real notes across 3 repos, drew 130 cross-repo wikilink edges, indexed 235 chunks for multilingual semantic search, served the lot through a local FastAPI + D3 Canvas, and published v0.1 → 0.3 (5 commits) to a public GitHub repo. 0.4 hosted SaaS spec'd but gated on validation. Pricing locked. Decision day 2026-05-24.**
