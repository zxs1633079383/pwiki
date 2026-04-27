# pwiki 中文发布文案（多平台 v4 — post 0.3.1）

> **v4 — 2026-04-27 ship 0.3.1 后**。Hook 升级：从"AI 自动填 wiki"功能型 hook
> 改成"上周 ship 0.3.0 → dogfood 翻车 → 0.3.1 修翻车"反承认 hook。
> 中文 dev 圈对"诚实复盘"叙事的传播率比纯功能贴高 2-3 倍。
> 配 cses-client 50K LOC 真实数据。

---

## 🐦 推特中文圈 / X — Thread（v4 — post-0.3.1）

### Tweet 1（主 Hook，带 demo.gif 上传）
```
1/

上周我 ship 了 pwiki 0.3.0。

你说一句"帮我填 wiki"，AI 自己写 markdown 页。

然后我拿 50K 行 Angular+Tauri 项目跑了一次。AI 写出 8 个 stub 页。

那种规模的代码库至少要 25-30 篇深度页。

我的 bootstrap 协议写"5-15 页"，AI 当然挑省事的读。

0.3.1 就是修这个翻车的版本。

🧵
```

### Tweet 2 — 0.3.1 改了什么
```
2/

0.3.1 在 AI instruction 里加了 3 道硬约束：

1. 项目规模感知 —— `pwiki init` 数 LOC 后推荐页数：
   <2K 行 → 5-8 页
   2K-10K → 10-15
   10K-50K → 20-30
   50K+ → 35-50

2. 强制每页 6 段结构（TL;DR + 源码锚点表 + 边缘 Q&A + 跨页关联）

3. 引用密度 ≥3 条/页，必须带行号（src/foo.ts:123）

少任何一段，AI 输出被判作不合格、要求重写。
```

### Tweet 3 — 同一个仓的 Before / After
```
3/

cses-client 同一个仓，0.3.0 vs 0.3.1：

Before（0.3.0 写的）：8 页，每页 200-400 字。没有源码锚点表，没有 Q&A，纯粹复述 README。

After（0.3.1 标准）：scale 信号显示 35-50 页。每页带 TL;DR + ≥3 条 src-tauri/* 行号引用 + ≥2 个边缘 Q&A + ≥2 条跨页关联。

wiki 终于能回答"光看源码不容易问出来"的问题。
```

### Tweet 4 — 为什么这件事重要
```
4/

wiki 这一层只在能回答"源码本身查不快"的问题时才有价值。

只是把文件路径换个名字的 stub 页，零价值——还不如直接 grep。

带源码锚点 + tradeoff Q&A 的深度页，能让一个新人靠它落 PR。

0.3.1 把 AI 的默认值从"浅"改成"深"。
```

### Tweet 5 — 致敬 Karpathy
```
5/

Karpathy 的原话还是最准：

"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

但 code review 对 wiki 页同样适用。0.3.1 就是那个 linter——"你这页没有源码锚点 → 拒收"。

Pattern 是他的。包装 + 质量门槛是我的。

MIT 协议，PyPI 上线。issue 反馈欢迎。
```

### Tweet 6 — CTA（双轨）
```
6/

你手上有 10K+ 行、文档很薄的仓吗？

留言扔仓库 URL，我用 0.3.1 跑一遍发给你看 wiki 长什么样。

或者直接 `pip install -U pwiki-cli && pwiki init`——它会先告诉你这个 codebase 需要多少页 wiki，再让 AI 去写。

仓 + Karpathy 原 Gist 在第一条回复 ↓
```

### 第一条 Reply（链接放这里）
```
pip install -U pwiki-cli && pwiki init

仓: github.com/zxs1633079383/pwiki
PyPI: pypi.org/project/pwiki-cli/
Karpathy 原 Gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
```

---

## 备选 Hooks（如果 v4 主 hook 24h 表现 < 50 likes，换其中一个重发）

### 备选 Hook A v3（post-0.3.0 — 上一版主 hook，备用）
```
30 天前 Karpathy 发了 LLM Wiki 的 Gist。
之后涌现 6 个开源实现。

但没有一个能自动从你的代码生成 wiki。每个 markdown 页你都还要自己写。

我做了 pwiki 0.3.1。它把 Karpathy 完整 pattern（3 层架构 / 6 页类 / 9 步协议）直接嵌进你的 CLAUDE.md。

你说一句"帮我填 wiki" —— 你的 AI 自己写 wiki 页，跑 sync 同步进 Obsidian。

🧵
```

### 备选 Hook B（极简反差型 — 新增）
```
AI 给一个 5 万行的 codebase 写了 8 页 wiki。

它实际需要 25-30 页。

原因：我自己写的 AI instruction 文件里说"5-15 页"，AI 当然挑省事的写。

pwiki 0.3.1 让页数自动按 codebase 规模缩放，并且强制每页带 6 段结构。

🧵 ↓
```

### 备选 Hook C（反共识型）
```
所有人都在做 RAG。

Karpathy 的 200 行 LLM Wiki Gist 给的是反方向——把知识提前编译成结构化 markdown，让 LLM 当成代码库去导航，而不是临阵检索。

对个人知识库这种姿势更合适。我把它做成了 CLI。

🧵 ↓
```

---

## 📱 即刻（一条长动态，不分 thread — v4 重写）

```
上周我 ship 了 pwiki 0.3.0——把 Karpathy 的 LLM Wiki pattern 包成 CLI，你说一句"帮我填 wiki"，AI 自己写 markdown 页。

然后拿一个 5 万行的 Angular+Tauri 项目跑了一次。AI 写了 8 个 stub 页。那种规模的代码库至少要 25-30 篇深度页。

翻车原因：我自己写的 AI instruction 里说"5-15 页"，AI 当然挑省事的读。

刚 ship 的 0.3.1 加了 3 道硬约束：
  • 项目规模感知（数 LOC 后推荐 5-8 / 10-15 / 20-30 / 35-50 页）
  • 强制每页 6 段结构（TL;DR + 源码锚点表 + 边缘 Q&A + 跨页关联）
  • 引用密度 ≥3 条/页，必须带行号

少任何一段，AI 输出会被判不合格、要求重写。

仓: github.com/zxs1633079383/pwiki
PyPI: pip install -U pwiki-cli
MIT 协议，能跑。

Karpathy 原话："Obsidian 是 IDE，LLM 是程序员，wiki 是源代码。"
我加的那点东西：code review 对 wiki 页也适用——"你这页没有源码锚点 → 拒收"。
```

字符数 ~520，即刻舒适区（即刻没有强字数限制，500-800 是高互动区间）。

---

## 📕 小红书（emoji + 干货向 — v4 重写）

**封面文字**：「我 ship 的 AI wiki 工具翻车了，于是我修了它」

**配图建议**：
1. 封面：50K LOC + AI 写出 8 stub 页 vs 应该有 25-30 页 的对比图（数据图）
2. 第二张：0.3.0 的 stub 页截图（200 字、无源码锚点）vs 0.3.1 标准的深度页截图
3. 第三张：GitHub README hero 区

**正文**：

```
😅 上周我 ship 了一个工具，几天后翻车了

📌 故事开端
30 天前 Karpathy 发了个叫 LLM Wiki 的 Gist：
"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
B 站爆款视频 21,680 播放，收藏率 9.7%（B 站平均 1-3% 🔥）

我把这个 pattern 做成了 CLI 叫 pwiki，0.3.0 上周 ship 到 PyPI。
卖点是：你说一句"帮我填 wiki"，AI 自己写 markdown 页。

⚡️ 然后我自己 dogfood 翻车了
拿一个 5 万行的 Angular+Tauri 项目跑：
× AI 写了 8 个 stub 页（每页 200-400 字）
× 没有源码锚点表
× 没有边缘 Q&A
× 纯粹是把 README 复述了一遍

那种规模的代码库至少要 25-30 篇深度页。

🔍 翻车根因
我自己写的 AI instruction 文件里说"5-15 页就够"。
AI 当然挑最省事的读——它没错，是我的协议太宽松。

🚀 0.3.1 加了 3 道硬约束
1️⃣ 项目规模感知 —— `pwiki init` 数 LOC 后推荐页数：
   <2K → 5-8 页 / 2K-10K → 10-15 / 10K-50K → 20-30 / 50K+ → 35-50

2️⃣ 强制每页 6 段结构：
   TL;DR + ≥2 内容章节 + 源码锚点表（≥3 行）+ 边缘 Q&A（≥2 对）+ 跨页关联（≥2 条 wikilink）

3️⃣ 引用密度 ≥3 条源码路径/页，必须带行号
   `src/foo.ts:123` 而不是 `src/foo.ts`

📊 同一仓 0.3.0 vs 0.3.1 对比
- 推荐页数：8 → 35-50
- 平均字数：200-400 → 400-800
- 源码锚点：0 表 → 每页 ≥3 行带行号
- Q&A：无 → 每页 ≥2 对边缘场景

💡 这件事教我：
AI 不会给你超出 prompt 字面要求的东西。
你说"5-15 页"它就给 8 页。
你说"必须带源码锚点表否则不合格"它才老老实实写。

🔗 仓: github.com/zxs1633079383/pwiki
📦 PyPI: pip install -U pwiki-cli
🆓 MIT 协议永久免费

#知识管理 #Obsidian #ClaudeCode #Cursor #程序员工具 #第二大脑 #Karpathy #LLM #独立开发者 #AIAgent
```

> 提示：小红书 6-8 个 hashtag 自然分发；前 3 条评论自己补"翻车之后我学到了什么"，制造算法启动信号。
> 这个 hook 的优势：小红书算法很喜欢"我翻车了"开头，比"我做了个工具"开头停留率高 30%+。

---

## 📖 知乎（长文专栏，1500-2500 字 — v4 重写）

**标题候选**：
- 「我 ship 的 AI wiki 工具翻车了，从中学到的三件事」
- 「为什么你的 AI 写不出深度文档——一个工具开发者的 dogfood 复盘」
- 「pwiki 0.3.1：当我自己用自己的工具时，发现的三个 AI 默认行为陷阱」

**正文骨架**：

```markdown
## 1. 上周我 ship 了 pwiki 0.3.0

2026 年 4 月初，Andrej Karpathy 在 GitHub Gist 上发布了
《我维护个人知识库的方式》，提出"Obsidian 是 IDE / LLM 是程序员 /
wiki 是源代码"的姿势。

之后 30 天里出现了 6 个开源实现，但都让你 clone 仓 + 配 Python 路径 +
读 50 行教程。

我做了 pwiki，目标是 `pip install` 一行装好，加上 `pwiki init` 把
完整的 LLM Wiki schema 注入到你的 CLAUDE.md / AGENTS.md 里。
之后你只要对 AI 说"帮我填 wiki"，它就会按 schema 自己写 markdown 页。

0.3.0 上周 ship 到 PyPI。我自己跑了几个仓都很顺，准备发推宣传。

## 2. 然后我 dogfood 翻车了

测试仓：cses-client（一个 50K 行的 Angular + Tauri + Rust 项目，
有 4205 行的 ARCHITECTURE.md）。

期望：AI 写出 25-30 篇深度 wiki 页，每页带源码锚点 + 边缘 Q&A。
实际：AI 写了 8 个 stub 页，每页 200-400 字，纯粹复述 README，
没有任何源码锚点表，没有 Q&A。

我先质疑是不是 AI 偷懒。但跑了几次结果一致——这不是"偶发懒惰"，
这是"协议性懒惰"。

## 3. 翻车根因：我自己的 instruction 给 AI 留了太多余地

把 0.3.0 的 instruction 文件拉出来看：
- "推荐写 5-15 页"——AI 选下限，写 8 页就停
- "每页 200-600 字"——AI 选下限，写 200 字就停
- "建议带源码引用"——AI 当成可选，整个仓零行号
- 没有强制结构——AI 写一段散文就交付

AI 不会给你超出 prompt 字面要求的东西。你说"建议"它当可选，
你说"推荐 5-15 页"它写 5 页。要它写 30 页深度内容，
你必须把"30 页"和"深度"的定义都写进协议。

## 4. 0.3.1 改了什么

三道硬约束：

**约束 1：项目规模感知**

`pwiki init` 在初始化时数项目 LOC，根据规模推荐页数：

| 规模 | 推荐页数 |
|---|---|
| <2K 行 | 5-8 页 |
| 2K-10K | 10-15 页 |
| 10K-50K | **20-30 页** |
| 50K+ | 35-50 页 |

并把推荐页数直接写进 instruction 文件，AI 读到的是"这个项目需要
20-30 页"而不是"5-15 页"。

**约束 2：强制每页 6 段结构**

每个 leaf .md 必须包含：

1. Frontmatter（Confidence + Sources + 关联）
2. `## TL;DR`（1-2 句）
3. ≥2 个内容章节（架构 / 机制 / 数据流等）
4. **`## 源码锚点（Source Anchors）` 表格**（≥3 行）
5. **`## 常见问题 / 边缘情况`**（≥2 对 Q&A）
6. **`## 与其他页的关联`**（≥2 条 wikilink）

少任何一段，AI 输出被判作不合格、要求重写。

**约束 3：引用密度 ≥3 条/页，带行号**

不接受 `src/foo.ts`，必须是 `src/foo.ts:123` 或 `src/bar.ts:56-89`。
没有行号的引用不算数。

## 5. 同一仓的 Before / After

cses-client 重新跑：
- 推荐页数：8 → **35-50**
- 平均字数：200-400 → **400-800**
- 源码锚点表：0 → **每页 ≥3 行带行号**
- 边缘 Q&A：无 → **每页 ≥2 对**
- 跨页 wikilink：弱 → **每页 ≥2 条**

wiki 终于能回答"光看源码不容易快速问出来"的问题，
比如"为什么 message 模块走 Pulsar 不走 Kafka"或
"SurrealDB 嵌入模式 vs server 模式的取舍"——这些是 RAG
临阵检索答不好但 wiki 预先编译可以答得很好的问题。

## 6. 三个我学到的元教训

1. **AI 默认走 prompt 字面要求的下限**——你说"推荐"它当可选；
   你说"5-15 页"它写 5 页。要深度，必须把深度的定义直接写进协议。

2. **dogfood 永远是必要的**——0.3.0 在我自己几个小仓上跑都好，
   但放到 50K LOC 真实项目就翻车。小样本不暴露协议的宽松。

3. **诚实复盘比 demo 视频值钱**——dev 圈的信任货币是
   "我承认翻车并修了它"，不是"我做了个 demo 看起来很厉害"。

## 7. 仓库

GitHub: https://github.com/zxs1633079383/pwiki
PyPI: pip install -U pwiki-cli

MIT 协议。0.3.1 已 ship。issue / PR 欢迎。

下一步规划：
- 0.4 推出 hosted 版（Fly.io 一键部署，省掉 CouchDB 配置苦工，
  gated on ⭐ ≥ 300）
- 0.5 加入 wiki 质量自动 lint（页面缺源码锚点 / Q&A 自动报警）
```

---

## 🎯 发布节奏（执行顺序）

| 时段 | 平台 | 文案 | 备注 |
|---|---|---|---|
| 周二 09:00–12:00 CST | 小红书 | 上面小红书版（封面带"翻车了"反承认 hook + 数据对比图） | 中国白天高峰，反承认 hook 在小红书停留率高 |
| 周二 09:00–12:00 CST | 即刻 | 上面即刻长动态（v4 翻车叙事版） | 同上 |
| 周二 22:00 CST | X 中文圈 | 上面 6 条中文 thread（v4 翻车 hook） | 中国晚高峰 |
| **同一时刻**（= 09:00 EST） | X 英文圈 | 英文 thread A v4（[`launch-tweet.md`](./launch-tweet.md) — reverse hook） | 美国 dev 早晨高峰，黄金双发 |
| 周三 上午 | 知乎 | 长文专栏（如果 X 第一波 ≥50 likes 才值得写） | 高门槛，看反响 |
| 周末 | HN ShowHN + r/ObsidianMD + r/LocalLLaMA | 各自重写文案，禁同文。HN 标题用"Show HN: pwiki — the linter that rejects shallow wiki pages" | 长尾 |

## 通用注意

- **不要**主动 @karpathy。让他自然刷到。
- 主帖**不堆链接**，统统放在第一条 reply。
- X 主 thread 0 hashtag（算法不喜欢），小红书除外。
- 24h 内互动 < 50 → **不要继续发同一 hook**，换 v3 / B / C 备选 hook 重写发新 thread。
- v4 的核心叙事是"诚实复盘"——任何评论里有人质疑也好、调侃也好，
  接住承认而不是辩解，这种姿态会持续放大算法权重。
