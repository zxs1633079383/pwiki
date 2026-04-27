# pwiki 中文发布文案（多平台 v3 — 后 0.3.0）

> **v3 — 2026-04-27 ship 0.3.0 后**。核心差异点升级：AI 自动填 wiki，你只说一句话。
> 配 cses-client 真实数据（8 页 / 38 跨页边 / 60 秒）。

---

## 🐦 推特中文圈 / X — Thread（v3 — post-0.3.0）

### Tweet 1（主 Hook，带 demo.gif 上传）
```
1/

30 天前 Karpathy 发了 LLM Wiki 的 Gist。
之后涌现 6 个开源实现。

但没有一个能自动从你的代码生成 wiki。每个 markdown 页你都还要自己写。

我做了 pwiki 0.3.0。它把 Karpathy 完整 pattern（3 层架构 / 6 页类 / 8 步协议）直接嵌进你的 CLAUDE.md。

你说一句"帮我填 wiki" —— 你的 AI 自己写 8 页，跑 sync，60 秒搞定。

🧵
```

### Tweet 2 — pwiki init 做什么
```
2/

pwiki init 做 3 件事：

1. 检测项目里 5 种 AI 工具配置（CLAUDE.md / AGENTS.md / GEMINI.md / .clinerules / .cursor/rules），按它们的格式写指令
2. 把 Karpathy 完整 LLM Wiki Schema —— 6 页类 / 8 步引导 / 5 类 lint —— 注入到 <!-- pwiki:begin --> 标记内（你已有内容一字不动）
3. bootstrap docs/wiki/ 骨架

marker 包裹意味着重跑 init 是原地更新，永远不会破坏你的现有 instruction。
```

### Tweet 3 — 真实 Angular+Tauri 仓跑通
```
3/

刚在 cses-client 跑了一遍（4205 行 ARCHITECTURE.md，Angular 20 + Tauri 2）：

→ 8 篇 wiki 页（5 实体 / 1 概念 / 1 操作 / 1 对比）
→ 38 条 [[wikilink]] 内部跨页边（aliases 全部解析通）
→ 168 条边在跨 4 仓的全局 canvas 里
→ 每条 claim 都引真实 src-tauri/... 或 src/... 路径
→ ~60 秒端到端，pwiki init 之后零手敲 CLI
```

### Tweet 4 — 别人为啥没做到这一步
```
4/

现有 6 个开源实现都停在"装个 Claude skill，拿这条 prompt 复制粘贴"。

每页 wiki 还是你手动驱动 AI 一条一条写。

pwiki 0.3.0 把完整 Schema 直接放进 AI 工具的已加载上下文 —— 三层架构 / 6 页类 / 不可变规则 / 引用要求 / 质量门槛。

AI 不需要读外部 prompt。它已经知道怎么干了。
```

### Tweet 5 — 致敬 Karpathy
```
5/

Karpathy 的原话最准：

"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

这个 pattern 是他的，包装是我的。

MIT 协议，v0.1.1，刚上 PyPI，dogfood 跑过 33 篇真实笔记。issue 反馈欢迎。
```

### Tweet 6 — CTA（双轨）
```
6/

你想第一个把哪个 docs/wiki/ 丢进 Vault？

留言扔过来最乱的一个，我给你跑一遍看 pwiki 输出什么。

懒得发的话点个 ⭐ 也行，等以后你有 vault 时再回来用。

仓库 + Karpathy 原 Gist 在第一条回复 ↓
```

### 第一条 Reply（链接放这里）
```
pip install -U pwiki-cli && pwiki init

仓: github.com/zxs1633079383/pwiki
PyPI: pypi.org/project/pwiki-cli/
Karpathy 原 Gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
```

---

## 📱 即刻（一条长动态，不分 thread）

```
30 天前 Karpathy 发了个 LLM Wiki 的 Gist：把笔记编译成结构化 markdown，让 LLM 在上面"导航"，不是 RAG。

30 天涌现 6 个开源实现，但每一个都让你 clone 仓 + 配置路径 + 读 50 行教程。

我做了 pwiki —— 一行 pip install，5 个命令搞定：
  • sync       wiki 到 Obsidian Vault
  • aliases    自动对齐英文 slug ↔ 中文文件名
  • canvas     多仓知识图谱（JSON Canvas）
  • brief      4 板块每日早报（艾宾浩斯+概念碰撞+商机+4 维自我演进）
  • query      本地语义搜索（fastembed 多语言，离线，零 API key）

我自己仓 33 篇笔记跑出来 130 条 cross-repo wikilink，全自动连边。

Karpathy 原话："Obsidian 是 IDE，LLM 是程序员，wiki 是源代码。"

仓: github.com/zxs1633079383/pwiki
PyPI: pip install -U pwiki-cli
MIT 协议，能跑。

什么场景最受用？我猜两个：
1. 自己有 5+ 个项目想统一知识层但散在各处
2. Substack/公众号长内容创作，需要私人 brain trust 而非通用日报
```

字符数 ~480，即刻舒适区。

---

## 📕 小红书（emoji + 干货向）

**封面文字**：「30 天前 Karpathy 引爆，我做成了 pip 一行」

**配图建议**：从 GitHub 仓首页截 README hero 区（含 Karpathy quote 那段）。小红书不收 GIF，要图片。

**正文**：

```
✨ Karpathy 的 LLM Wiki，30 天后我让它真正自动化了

📌 故事开端
30 天前 Karpathy 发了个叫 LLM Wiki 的 Gist：
"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
B 站爆款视频 21,680 播放，收藏率 9.7%（B 站平均 1-3% 🔥）

⚡️ 痛点：6 个开源实现，没有一个能"AI 自动填"
× 都让你 clone 仓 + 配 Python 依赖
× 都让你**手动**对 AI 一页一页指挥写 wiki
× wiki 内容生成的鸿沟没人填上

🚀 pwiki 0.3.0 改了这件事
pip install -U pwiki-cli + pwiki init 之后，AI 知道：
→ Karpathy 的 3 层架构（Raw / Wiki / Schema）
→ 6 种页类（实体 / 概念 / 操作 / 对比 / 综合 / 概要）
→ 8 步 Bootstrap 协议
→ 5 类 Lint（孤儿 / 过期 / 矛盾 / 断链 / 引用缺失）
→ Quality bar（陌生人 10 分钟内能看懂全貌）

你说一句"帮我填 wiki"，AI 自己读源码 + 写 8 页 + 跑 sync。

📊 真实跑通数据（cses-client，4205 行 ARCHITECTURE.md）
- 8 页 wiki（5 实体 / 1 概念 / 1 操作 / 1 对比）
- 38 条 [[wikilink]] 内部互链
- 每条 claim 都引 src-tauri/... 真实路径
- 60 秒端到端
- 0 行手敲 CLI

🔗 仓: github.com/zxs1633079383/pwiki
📦 PyPI: pip install -U pwiki-cli
🆓 MIT 协议永久免费

#知识管理 #Obsidian #ClaudeCode #Cursor #程序员工具 #第二大脑 #Karpathy #LLM #独立开发者 #AIAgent
```

> 提示：小红书 6-8 个 hashtag 自然分发；前 3 条评论自己补"我自己怎么用"，制造算法启动信号。

---

## 📖 知乎（长文专栏，800–1500 字）

**标题候选**：
- 「Karpathy 的 LLM Wiki 30 天后：开源生态长成什么样了？」
- 「为什么 Notion AI 不是个人知识库的终点 — 一个开发者的 30 天复盘」
- 「我把 Karpathy 的 LLM Wiki 做成了 CLI，一行装，开源」

**正文骨架**：

```markdown
## 1. 一切从 Karpathy 那条 Gist 开始

2026 年 4 月初，Andrej Karpathy 在 GitHub Gist 上扔了一个文件：
《我维护个人知识库的方式》。其中那句被反复引用的话：

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

简单说，他的姿势是：把笔记编译成结构化 markdown，让 LLM
在文件夹上"导航"——不是 RAG，不在查询时检索，而是预先把
知识压进 wiki 结构里，让 LLM 当成代码库来读。

## 2. 30 天里发生的事

到目前已经有 6 个开源实现：
- Ar9av/obsidian-wiki — 偏 ingest 流水线
- AgriciDaniel/claude-obsidian — 加了 autoresearch 命令
- NicholasSpisak/second-brain — 最贴近 Karpathy 原版
- 还有 Medium / Substack 5+ 篇长文教程

但是——每一个都还是要你 clone 仓、配 Python 路径、把 Gist
拷进 Claude Code 项目里。**没有一个是装上就跑的产品**。

B 站杰森效率工坊那期教学视频 21,680 播放、9.7% 收藏率，
说明用户真的想用，但也真的卡在配置环节。

## 3. 我做了什么

pwiki —— 一行 pip install 的 CLI：

`​`​`bash
pip install -U pwiki-cli   # PyPI 上 pwiki 名被占了，发布为 pwiki-cli；CLI 命令仍是 pwiki
pwiki sync ./your-repo/wiki your-repo
pwiki canvas
pwiki brief
`​`​`

5 个子命令：
- sync     — wiki 同步到 Vault/repos/<name>/
- aliases  — 英文 slug ↔ 中文文件名（这点是中文用户的真痛点）
- canvas   — 多仓 JSON Canvas（自动跨仓连边）
- brief    — 4 板块每日早报（艾宾浩斯+四维轮值演进）
- query    — 本地语义搜索（fastembed 多语言 MiniLM，离线零 API key）

每个命令都是 idempotent 的，可独立运行也可组合。

## 4. 真实跑通的数据

我自己仓 GitNexus 33 篇笔记导入：
- 自动加 frontmatter（source_repo / last_synced / ebbinghaus_stage 等）
- 130 条 cross-repo wikilink 自动连边（98% 解析率）
- 中文文件名 + 英文 slug 通过 EN→ZH 词典 100% 对齐
- 235 chunks 本地索引，semantic 查询命中率高

## 5. 与现有方案的差异

不重复别人的工作：每个开源仓都很好，pwiki 只补一件事——
"装上即跑"。原生 multi-repo + 中文友好 + JSON Canvas + 早报 +
艾宾浩斯 + 本地 RAG 一并打包。

## 6. 仓库

GitHub: https://github.com/zxs1633079383/pwiki
PyPI: pip install -U pwiki-cli

MIT 协议。欢迎 PR。

---

下一步规划：
- 0.4 推出 hosted 版（Fly.io 一键部署，省掉 CouchDB 配置苦工，gated on ⭐ ≥ 300）
```

---

## 🎯 发布节奏（执行顺序）

| 时段 | 平台 | 文案 | 备注 |
|---|---|---|---|
| 周二 09:00–12:00 CST | 小红书 | 上面小红书版（emoji+截图） | 中国白天高峰 |
| 周二 09:00–12:00 CST | 即刻 | 上面即刻长动态 | 同上 |
| 周二 22:00 CST | X 中文圈 | 上面 6 条中文 thread | 中国晚高峰 |
| **同一时刻**（= 09:00 EST） | X 英文圈 | 英文 thread A v2（[`launch-tweet.md`](./launch-tweet.md)） | 美国 dev 早晨高峰，黄金双发 |
| 周三 上午 | 知乎 | 长文专栏（如果 X 第一波 ≥50 likes 才值得写） | 高门槛，看反响 |
| 周末 | HN ShowHN + r/ObsidianMD + r/LocalLLaMA | 各自重写文案，禁同文 | 长尾 |

## 通用注意

- **不要**主动 @karpathy。让他自然刷到。
- 主帖**不堆链接**，统统放在第一条 reply。
- X 主 thread 0 hashtag（算法不喜欢），小红书除外。
- 24h 内互动 < 50 → **不要继续发同一 hook**，换 B 或 C 重写发新 thread（[`launch-tweet.md`](./launch-tweet.md) 备选 Hooks 区）。
