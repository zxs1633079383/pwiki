# pwiki Launch Tweet — Thread (English)

> **v3 — 2026-04-27, post 0.3.0 ship.** Reflects the real differentiator:
> AI auto-fills the wiki from code; user types one phrase.
> 6 main thread + 1 reply（links in reply to avoid algorithm hit）.

## 主推荐 Hook（A v3 — post-0.3.0）

```
1/

30 days ago Karpathy posted his LLM Wiki gist.
6 open-source implementations followed.

None of them auto-fill the wiki from your code.
You still write every markdown page by hand.

I shipped `pwiki` 0.3.0. It embeds Karpathy's full pattern (3 layers / 6 page types / 8-step protocol) into your CLAUDE.md.

You say "fill the wiki" — your AI writes 8 pages and runs sync, in 60 seconds.

🧵
```

**字符数**：~246 (含换行，<280 ✓)
**v1 → v2 改动**：
- "dropped" → "posted" (passive "drop" 在 dev 圈被滥用)
- 加 "have shipped since" 体现"已经发生"的时态
- 加 **"But every single one still makes you…"** 反转节奏
- "I built" → "So I shipped" + 收尾 "That's the entire delta"（dev 高密度词）

---

## Thread 完整 7 条（润后 v2，搭配主 Hook A v2）

### Tweet 2 — How `pwiki init` works
```
2/

`pwiki init` does 3 things:

1. detects 5 AI agent dotfiles in your project (CLAUDE.md / AGENTS.md / GEMINI.md / .clinerules / .cursor/rules) and writes per-tool instructions
2. injects Karpathy's full LLM Wiki Schema — 6 page types, 8-step bootstrap, 5-category lint — inside <!-- pwiki:begin --> markers (your existing content untouched)
3. bootstraps docs/wiki/ scaffold

Marker pair = re-running init updates in place, never clobbers.
```

### Tweet 3 — Verified on a real Angular+Tauri repo
```
3/

Just ran it on cses-client (4205-line ARCHITECTURE.md, Angular 20 + Tauri 2):

→ 8 wiki pages distilled (5 entities / 1 concept / 1 operation / 1 comparison)
→ 38 internal cross-page edges (every [[wikilink]] resolved through aliases)
→ 168 edges across 4 repos in the global canvas
→ Every claim cites a real `src-tauri/...` or `src/...` path
→ ~60 seconds end-to-end, zero hand-typed CLI commands after `pwiki init`
```

### Tweet 4 — Why nobody else does this
```
4/

The 6 existing implementations all stop at "here's a Claude skill, copy-paste this prompt".

You still drive every page generation by hand.

pwiki 0.3.0 puts the *full Schema* into your AI tool's loaded context — Three-Layer Architecture, 6 page types, immutability rules, citation requirements, quality bar.

Your AI doesn't read an external prompt. It already knows.
```

### Tweet 5 — Karpathy callback
```
5/

Karpathy framed it best:

"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

The pattern is his. The packaging is mine.

MIT-licensed. v0.1.1 — early but dogfood-tested on 33 real notes. Issues welcome.
```

### Tweet 6 — CTA（双轨）
```
6/

What would you ferry into your Vault first?

Reply with the messiest docs/wiki/ folder you've got — I'll show you what pwiki produces on it.

Or just star the repo and try it later when you have a vault to feed it.

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

## 备选 Hooks（如果 A v2 24h 表现 < 50 likes，换其中一个重发）

### 备选 Hook A v1（原版）
```
Karpathy dropped his "LLM Wiki" gist 30 days ago.

6 open-source implementations followed.

Every single one needs you to clone, configure paths, and read a 50-line tutorial.

I built `pwiki` so you can pip install it instead.

🧵
```

### 备选 Hook B（直接价值型）
```
Your messy docs/wiki/ folder + Obsidian + Claude Code = a self-maintaining knowledge base.

I packaged Karpathy's LLM Wiki pattern as a CLI:

  pip install -U pwiki-cli
  pwiki sync ./repo/wiki repo
  pwiki canvas

30 days after the gist. 🧵
```

### 备选 Hook C（反共识型）
```
Everyone is building RAG.

Karpathy's 200-line "LLM Wiki" gist suggests the opposite: compile your knowledge into structured markdown ahead of time, let the LLM navigate it.

It's better for personal KBs. I shipped a CLI tonight.

🧵 ↓
```

---

## 质量自检（按 quality-analytics.md 清单）

| 维度 | 检查 | 评分 |
|---|---|---|
| **算法层** | 主 thread 0 外链（放 reply）；0 hashtag；含媒体（GIF 在第 1 条） | ✅ |
| **Hook 层** | 可信度锚点（Karpathy）+ 数字（30/6）+ **反转**（But…still…）+ 价值 + dev 高密度词（"delta"） | **9/10** ↑ |
| **内容层** | 1/3/1 节奏（功能→数据→差异→致敬→CTA）；每条推进；Rate of Revelation 在 Tweet 3 数字爆点 | ✅ |
| **CTA 层** | **双轨**（高门槛 reply 文件夹 + 低门槛 star repo）；具体行动召唤 | ✅ |
| **品牌叙事** | 致敬 Karpathy 不抢功劳；明确"pattern 是他的，packaging 是我的" | ✅ |

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
- [x] PyPI 已上线（pwiki-cli 0.1.0）
- [x] README 卖货级 + Karpathy quote + Quick Start
- [x] LICENSE = MIT
- [ ] CI 跑通（GitHub Actions 首次 run，push 后看）
- [ ] 发完 Twitter pin 主 thread

## 发布后跟帖策略（24h）

- **不要**主动 @karpathy。让他自然刷到。**只有 24h 内 ≥100 likes** 时才在自己的回复里 @ 他（"FWIW @karpathy this is built on your gist."）
- 发布 24h 后看数据：
  - ≥100 likes / ≥10 RT → 写个"What I learned shipping pwiki" 复盘 thread 引第二波
  - <30 likes / <5 RT → **不要再发同一 hook**，换 B 或 C 的 hook 重写发新 thread
- 周末扩散：HN ShowHN（重写文案）+ r/ObsidianMD + r/LocalLLaMA（每个重写）
