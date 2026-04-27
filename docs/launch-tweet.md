# pwiki Launch Tweet — Thread (English)

> **v4 — 2026-04-27, post 0.3.1 ship.** Hook upgraded from feature-list ("AI auto-fills wiki") to
> reverse-narrative ("shipped 0.3.0 → real-user dogfood embarrassed me → 0.3.1 fixes it").
> Dev Twitter rewards honest post-mortem hooks ~3× the engagement of feature-list hooks.
> 6 main thread + 1 reply (links in reply to avoid algorithm hit).

## 主推荐 Hook（A v4 — post-0.3.1 reverse hook）

```
1/

Shipped pwiki 0.3.0 last week. You say "fill the wiki", your AI writes the pages.

Ran it on a 50K LOC Angular+Tauri repo. It wrote 8 stubs.

That codebase needs 25-30 deep pages. My bootstrap protocol said "5-15", so the AI took the lazy read.

0.3.1 fixes it.

🧵
```

**Char count**: ~265 (含换行，<280 ✓)
**v3 → v4 改动**：
- 抛弃 "30 days ago Karpathy posted…" 这种 history-recap 开头 — 已经被 6 个项目用烂
- 改用 **reverse hook**：承认 0.3.0 翻车 → 引出 0.3.1 修复 — dev 圈最吃这种诚实复盘叙事
- 加入 **具体反差数字**：50K LOC / 8 stubs / 25-30 deep pages — 可信度锚点 + 好奇缺口
- "took the lazy read" — dev 高密度词，能瞬间识别

---

## Thread 完整 6 条（v4）

### Tweet 2 — What 0.3.1 changed
```
2/

Three forced upgrades inside the AI's instruction file:

1. Scale awareness — `pwiki init` counts LOC and recommends a page range: <2K → 5-8 / 2K-10K → 10-15 / 10K-50K → 20-30 / 50K+ → 35-50

2. Mandatory 6-section page structure (TL;DR + source-anchor table + Q&A + cross-refs)

3. Citation density: ≥3 src-path citations per page, with line numbers

Pages missing any of the 6 sections are rejected output.
```

### Tweet 3 — Before / after on the same repo
```
3/

cses-client (same Angular+Tauri repo), 0.3.0 vs 0.3.1:

Before: 8 pages, 200-400 words each. No source anchors. No Q&A. Pure paraphrase of the README.

After: scale signal says 35-50 pages. Each page has TL;DR + ≥3 `src-tauri/*` citations with line numbers + ≥2 edge-case Q&A + ≥2 cross-references.

The wiki finally answers what the source can't quickly answer itself.
```

### Tweet 4 — Why this matters
```
4/

The wiki layer is only valuable if it answers questions the source code itself can't quickly answer.

Stub pages that just rename file paths add zero value.

Deep pages with source anchors + tradeoff Q&A turn the wiki into something a new hire can actually use to land a PR.

0.3.1 makes the AI default to deep, not shallow.
```

### Tweet 5 — Karpathy callback
```
5/

Karpathy's original framing still holds:

"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

But code review applies to wiki pages too. 0.3.1 is the linter that says "no source anchors — rejected".

Pattern is his. Packaging + the quality bar is mine.

MIT-licensed, on PyPI. Issues welcome.
```

### Tweet 6 — CTA（双轨）
```
6/

Got a 10K+ LOC repo with thin or no docs?

Reply with the repo URL — I'll run pwiki 0.3.1 on it and post what comes out.

Or just `pip install -U pwiki-cli && pwiki init` — it'll tell you exactly how many pages your codebase needs.

Repo + Karpathy's gist in the first reply ↓
```

### First Reply（链接放这里 — 算法友好）
```
pip install -U pwiki-cli && pwiki init

Repo: github.com/zxs1633079383/pwiki
PyPI: pypi.org/project/pwiki-cli/
Karpathy's original gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
```

---

## 备选 Hooks（如果 A v4 24h < 50 likes，换其中一个重发）

### 备选 Hook A v3（post-0.3.0 — 上一版主 hook，备用）
```
30 days ago Karpathy posted his LLM Wiki gist.
6 open-source implementations followed.

None of them auto-fill the wiki from your code. You still write every markdown page by hand.

I shipped `pwiki` 0.3.1. It embeds Karpathy's full pattern (3 layers / 6 page types / 9-step protocol) into your CLAUDE.md.

You say "fill the wiki" — your AI writes the pages and runs sync.

🧵
```

### 备选 Hook B（直接价值型）
```
Your messy docs/wiki/ folder + Obsidian + Claude Code = a self-maintaining knowledge base.

I packaged Karpathy's LLM Wiki pattern as a CLI:

  pip install -U pwiki-cli
  pwiki init       # writes the schema into your CLAUDE.md
  # then say "fill the wiki" to your AI

30 days after the gist. 🧵
```

### 备选 Hook C（反共识型）
```
Everyone is building RAG.

Karpathy's 200-line "LLM Wiki" gist suggests the opposite: compile your knowledge into structured markdown ahead of time, let the LLM navigate it like a codebase.

It's better for personal KBs. I shipped a CLI that does it.

🧵 ↓
```

### 备选 Hook D（极简反差型 — 新增）
```
The AI wrote 8 wiki pages for a 50K LOC codebase.

It needed 25-30.

Turns out my own AI-instruction file said "5-15 pages" and the AI took the lazy read.

pwiki 0.3.1 makes the page-count scale with the codebase, and forces a 6-section structure on every page.

🧵 ↓
```

---

## 质量自检（按 quality-analytics.md 清单 — v4）

| 维度 | 检查 | 评分 |
|---|---|---|
| **算法层** | 主 thread 0 外链（放 reply）；0 hashtag；含 GIF/媒体 | ✅ |
| **Hook 层** | 反承认开头（dev 圈最吃这种）+ 具体数字（50K / 8 / 25-30）+ 好奇缺口（"lazy read"）+ dev 高密度词（ship / dogfood / lazy read） | **9.5/10** ↑ |
| **内容层** | 1/3/1 节奏（翻车→修法→对比→为什么→致敬→CTA）；Rate of Revelation 在 Tweet 3 数字爆点 | ✅ |
| **CTA 层** | 双轨（高门槛 reply repo URL + 低门槛 pip install） | ✅ |
| **品牌叙事** | 致敬 Karpathy 不抢功劳；"pattern 是他的，质量门槛是我的"——比 v3 更明确自己的增量 | ✅ |
| **诚实度** | 公开承认 0.3.0 不够好 → 提升信任度（"我不卖 demo，我修翻车"） | **新增维度 ✅** |

**v3 → v4 评分对比**：
- Hook 9 → 9.5（反承认 + 数字爆点 + dev 词密度全部上来了）
- 诚实度从隐式变显式 — dev 圈最大的信任货币

## 发帖时间建议

**目标受众**：AI 开发者 + Obsidian 重度用户（多分布在美国 / 欧洲 / 中国）

| 时区 | 最佳时段 | 说明 |
|---|---|---|
| US East (EST) | Tue–Thu 9–11am 或 1–3pm | dev 早晨刷 X 高峰 |
| US West (PST) | Tue–Thu 8–10am | 同上 |
| 中国 (CST) | 周二 / 周三 / 周四晚 22:00–24:00 | 国内 dev 习惯睡前刷 X |

**双发推荐**：周二 22:00 CST（= 周二 09:00 EST）双高峰，同时发英文 thread 和中文 thread。

## 发布前 checklist

- [x] demo.gif 已 commit 进 repo（`docs/demo.gif`，348KB）
- [x] GitHub repo 已 public（github.com/zxs1633079383/pwiki）
- [x] PyPI 已上线（pwiki-cli **0.3.1**）
- [x] CHANGELOG 0.3.1 entry written ("stop writing stubs")
- [x] README 卖货级 + Karpathy quote + Quick Start
- [x] LICENSE = MIT
- [x] CI 跑通（GitHub Actions Python 3.10–3.13 全绿）
- [x] tag v0.3.1 已推 origin
- [ ] 发完 Twitter pin 主 thread

## 发布后跟帖策略（24h）

- **不要**主动 @karpathy。让他自然刷到。**只有 24h 内 ≥100 likes** 时才在自己的回复里 @ 他（"FWIW @karpathy this is built on your gist."）
- 发布 24h 后看数据：
  - ≥100 likes / ≥10 RT → 写"What I learned shipping 0.3.1 — three failure modes the AI defaults to" 复盘 thread 引第二波
  - <30 likes / <5 RT → **不要再发同一 hook**，换 B / C / D 的 hook 重写发新 thread
- 周末扩散：HN ShowHN（重写文案，hook 改成"Show HN: pwiki — the linter that rejects shallow wiki pages"）+ r/ObsidianMD + r/LocalLLaMA（每个重写）
