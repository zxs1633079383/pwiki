# pwiki Launch Tweet — Thread

> 6 条主 thread + 1 条 reply（links 放 reply 防降权）。
> Hook 用 "可信度锚点（Karpathy）+ 数字（30 天 / 6 仓）+ 反差（都需配置）+ 价值（pip install）" 公式。

## 主推荐 Hook（A 版本）

```
1/

Karpathy dropped his "LLM Wiki" gist 30 days ago.

6 open-source implementations followed.

Every single one needs you to clone, configure paths, and read a 50-line tutorial.

I built `pwiki` so you can pip install it instead.

🧵
```

**字符数**：~225（含换行，<280 ✓）
**公式**：可信度锚点 + 数字 + 反差 + 价值

## 备选 Hook B（直接价值型）

```
Your messy docs/wiki/ folder + Obsidian + Claude Code = a self-maintaining knowledge base.

I packaged Karpathy's LLM Wiki pattern as a CLI:

  pip install pwiki
  pwiki sync ./repo/wiki repo
  pwiki canvas

30 days after the gist. 🧵
```

## 备选 Hook C（反共识型）

```
Everyone is building RAG.

Karpathy's 200-line "LLM Wiki" gist suggests the opposite: compile your knowledge into structured markdown ahead of time, let the LLM navigate it.

It's better for personal KBs. I shipped a CLI tonight.

🧵 ↓
```

---

## Thread 完整 6 条（搭配主 Hook A）

### Tweet 2 — What it does

```
2/

Five subcommands. That's the whole API.

  pwiki sync       ferry a wiki/ dir into your Vault
  pwiki aliases    resolve [[english-slugs]] → Chinese-named files
  pwiki canvas     render every repo as a JSON Canvas
  pwiki brief      morning brief: review queue + cross-repo signals
  pwiki evolution  weekly self-evolution rollup

Each one is idempotent. Compose them in any order.
```

### Tweet 3 — Demo GIF

```
3/

60-second demo (GIF):

[demo.gif]

Point it at any docs/wiki/. Get:
• Vault/repos/<name>/ with managed YAML frontmatter
• Cross-repo JSON Canvas (130+ wikilinks resolved against Chinese-named files via an EN→ZH token dict)
• Daily brief: ① review queue ② 10 directions ③ deep opportunity ④ self-evolution
```

### Tweet 4 — Why not the others

```
4/

Why not the 6 existing implementations?

They're great patterns. But each one needs you to clone, configure paths, copy-paste the gist into Claude Code.

pwiki is one pip install and 5 orthogonal commands.

That's the entire delta. No more, no less.
```

### Tweet 5 — Karpathy callback

```
5/

Karpathy framed it best:

"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

The pattern is his. The packaging is mine.

MIT-licensed. Production-ready. Does what it says on the tin.
```

### Tweet 6 — CTA

```
6/

What would you ferry into your Vault first?

Drop your messiest docs/wiki/ folder in the replies — I'll show you what pwiki produces on it.

Repo + Karpathy's original gist in the first reply ↓
```

### First Reply (links go here, not in thread — algorithm-friendly)

```
Repo: github.com/zxs1633079383/pwiki
Karpathy's original gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

pip install pwiki-cli && pwiki --help
```

---

## 质量自检（按 quality-analytics.md 清单）

| 维度 | 检查 | 评分 |
|---|---|---|
| **算法层** | 主 thread 0 外链（放 reply）；0 hashtag；含媒体（GIF） | ✅ |
| **Hook 层** | 可信度锚点（Karpathy）+ 数字（30 天 / 6 仓）+ 反差（都需配置）+ 价值（pip install） | 8/10 |
| **内容层** | 1/3/1 节奏（功能→demo→差异→致敬→CTA）；每条推进 | ✅ |
| **CTA 层** | 具体行动召唤（drop your messiest docs/wiki/）；引导互动 | ✅ |
| **品牌叙事** | 致敬 Karpathy（不是抢功劳）；明确"pattern 是他的，packaging 是我的" | ✅ |

## 发帖时间建议

**目标受众**：AI 开发者 + Obsidian 重度用户（多分布在美国 / 欧洲 / 中国）

| 时区 | 最佳时段 | 说明 |
|---|---|---|
| US East (EST) | Tue–Thu 9–11am 或 1–3pm | dev 早晨刷 X 高峰 |
| US West (PST) | Tue–Thu 8–10am | 同上 |
| 中国 (CST) | 周二 / 周三 / 周四晚 22:00–24:00 | 国内 dev 习惯睡前刷 X |

**双发推荐**：先在美国 EST 周三上午发英文 thread；同时在中国 CST 周三晚 22:00 发一条精简中文版到推特中文圈。

## 发布前 checklist

- [ ] demo.gif 已 commit 进 repo（README 引用 docs/demo.gif）
- [ ] GitHub repo 已 public
- [ ] README 卖货级 + Karpathy quote + Quick Start 完整
- [ ] LICENSE = MIT
- [ ] CI 跑通（GitHub Actions）
- [ ] Twitter / X 上 pin 这条 thread

## 可选：跟帖策略（发布后 24h）

- @ 提到 [@karpathy](https://x.com/karpathy)（让原作者看到，他可能 quote-tweet 放大）
- 在 [r/ObsidianMD](https://reddit.com/r/ObsidianMD)、[r/LocalLLaMA](https://reddit.com/r/LocalLLaMA)、HN 同步发（不是同一文案，重写一遍照搬扣分）
- 引用刚导入的 GitNexus 作为真实使用例：截图 / GIF
