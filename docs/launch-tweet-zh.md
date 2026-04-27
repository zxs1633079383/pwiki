# pwiki 中文发布文案（多平台）

> 仿英文版结构，按"可信度锚点 + 数字 + 反差 + 价值"公式写。
> 对应英文版：[`launch-tweet.md`](./launch-tweet.md)。
> 用户：zxs1633079383，仓 URL：https://github.com/zxs1633079383/pwiki

---

## 🐦 推特中文圈 / X（thread 6 条 + 1 reply）

### Tweet 1（主 Hook）

```
1/

Karpathy 30 天前发了"LLM Wiki" Gist。

之后涌现 6 个开源实现。

每一个都需要你 clone 仓、配置路径、读 50 行教程。

我做了 pwiki，让你 pip install 就能用。

🧵
```

字符数 ~120（比英文版短，符合中文密度）

### Tweet 2 — 它做什么

```
2/

5 个子命令，就是全部 API：

  pwiki sync       wiki/ 目录 → Vault/repos/<name>/
  pwiki aliases    [[英文 slug]] ↔ 中文文件名 自动对齐
  pwiki canvas     多仓 JSON Canvas（自动连边）
  pwiki brief      四板块每日早报（艾宾浩斯+四维轮值）
  pwiki evolution  周日聚合本周演进

每个都是幂等的，可以任意顺序组合。
```

### Tweet 3 — Demo GIF

```
3/

60 秒演示（GIF）：

[demo.gif]

任何 docs/wiki/ 都能丢进去：
• Vault/repos/<name>/ 自动加 frontmatter
• 跨仓 JSON Canvas（我自己仓里 130 条 wikilink 自动连边）
• 早报：到期复习 + 跨仓概念碰撞 + 1 条深度商机 + 自我演进
```

### Tweet 4 — 为啥不用现有的

```
4/

有人会问：6 个开源实现都不错，为啥再做？

诚实答：它们都需要 clone、配路径、把 Gist 拷进 Claude Code。

pwiki 只需 pip install + 5 个正交命令。

差异就这一点，没多余的。
```

### Tweet 5 — 致敬 Karpathy

```
5/

Karpathy 的原话最准：

"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

这个 pattern 是他的，包装是我的。

MIT 协议，能跑，就这样。
```

### Tweet 6 — CTA

```
6/

你想第一个把哪个 docs/wiki/ 丢进 Vault？

留言扔过来最乱的一个，我给你跑一遍看 pwiki 输出什么。

仓库 + Karpathy 原 Gist 在第一条回复 ↓
```

### 第一条 Reply（链接放这里，主 thread 算法友好）

```
仓: github.com/zxs1633079383/pwiki
Karpathy 原 Gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

pip install pwiki-cli  # 注意 PyPI 名是 pwiki-cli（pwiki 被占用了），CLI 命令仍是 pwiki
```

---

## 📱 即刻（一条长动态，不分 thread）

```
30 天前 Karpathy 发了个 LLM Wiki 的 Gist：把笔记编译成结构化 markdown，让 LLM 在上面"导航"，不是 RAG。

30 天涌现 6 个开源实现，但每一个都让你 clone 仓 + 配置路径 + 读 50 行教程。

我做了 pwiki — 一行 pip install，5 个命令搞定：
  • sync wiki 到 Obsidian Vault
  • 自动对齐英文 slug ↔ 中文文件名
  • 多仓知识图谱（JSON Canvas）
  • 4 板块每日早报（艾宾浩斯到期 + 概念碰撞 + 商机 + 4 维自我演进）
  • 周日聚合一周演进

我自己仓 33 篇笔记跑出来 130 条 cross-repo wikilink，全自动连边。

Karpathy 原话："Obsidian 是 IDE，LLM 是程序员，wiki 是源代码。"

仓: github.com/zxs1633079383/pwiki
MIT 协议，能跑。

什么场景最受用？我猜两个：
1. 自己有 5+ 个项目想统一知识层但散在各处
2. Substack/公众号长内容创作，需要私人 brain trust 而非通用日报
```

字符数 ~480，即刻舒适区。

---

## 📕 小红书（emoji 多 + 干货向 + 钩子标题）

**封面文字**：「30 天前 Karpathy 引爆，我把它做成了 pip 一行」

**正文**：

```
✨ 帮 Obsidian 重度用户搭一个能跟 Claude Code 对话的"第二大脑"

📌 故事开端
30 天前 Karpathy 发了个叫 LLM Wiki 的 Gist：
"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."
B 站杰森效率工坊那条视频 21,680 播放，收藏率 9.7%（B站平均才 1-3% 🔥）

⚡️ 痛点
30 天涌现 6 个开源实现，但每个都要：
× clone 仓
× 配置一堆 Python 依赖
× 读 50 行教程
× 把 Gist 拷进 Claude Code

🚀 我做了什么
pwiki —— pip install 一行 + 5 个正交命令：
1️⃣ pwiki sync     把 wiki/ 同步进 Obsidian Vault
2️⃣ pwiki aliases  自动对齐 [[英文 slug]] ↔ 中文文件名（关键！）
3️⃣ pwiki canvas   多仓知识图谱
4️⃣ pwiki brief    每日 4 板块早报
5️⃣ pwiki evolution 周末演进档案

📊 我自己测试数据
- 33 篇笔记 → 130 条跨仓 wikilink 自动连边
- LiveSync 实时双向同步 5 秒级
- 安装到能跑 demo 不超过 60 秒

🔗 仓: github.com/zxs1633079383/pwiki
🆓 MIT 协议永久免费

#知识管理 #Obsidian #ClaudeCode #程序员工具 #第二大脑 #Karpathy #LLM #独立开发者
```

> 提示：小红书加 6-8 个 hashtag 自然分发；前 3 条评论可以补"我自己怎么用"，制造算法启动信号。

---

## 📖 知乎（长答 / 技术深度向）

**问题切入**：可以写一篇专栏，标题候选：

- 「Karpathy 的 LLM Wiki 30 天后：开源生态长成什么样了？」
- 「为什么 Notion AI 不是个人知识库的终点 — 一个开发者的 30 天复盘」
- 「我把 Karpathy 的 LLM Wiki 做成了 CLI，一行装，开源」

**正文结构**（800-1500 字最佳）：

```markdown
## 1. 一切从 Karpathy 那条 Gist 开始

2026 年 4 月初，Andrej Karpathy 在 GitHub Gist 上扔了一个文件：
《我维护个人知识库的方式》。其中那句被反复引用的话：

> "Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."

简单说，他的姿势是：把笔记编译成结构化 markdown，让 LLM
在文件夹上"导航"——不是 RAG，不查询时检索，而是预先把
知识压进 wiki 结构里，让 LLM 当成代码库来读。

## 2. 30 天里发生的事

我数了下，到目前已经有 6 个开源实现：
- Ar9av/obsidian-wiki — 偏 ingest 流水线
- AgriciDaniel/claude-obsidian — 加了 autoresearch 命令
- NicholasSpisak/second-brain — 最贴近 Karpathy 原版
- 还有 Medium / Substack 5+ 篇长文教程

但是——每一个都需要你 clone 仓、配 Python 路径、把 Gist
拷进 Claude Code 项目里。**没有一个是装上就跑的产品**。

B 站杰森效率工坊那期教学视频 21,680 播放、9.7% 收藏率，
说明用户真的想用，但也真的卡在配置环节。

## 3. 我做了什么

pwiki —— 一行 pip install 一行的 CLI：

```bash
pip install -e ~/workspace/ai-workspace/pwiki  # PyPI 发布中
pwiki sync ./your-repo/wiki your-repo
pwiki canvas
pwiki brief
```

5 个子命令：
- sync     — wiki 同步到 Vault/repos/<name>/
- aliases  — 英文 slug ↔ 中文文件名（这点是中文用户的真痛点）
- canvas   — 多仓 JSON Canvas（自动跨仓连边）
- brief    — 4 板块每日早报（艾宾浩斯+周轮值演进）
- evolution — 周日聚合一周演进

每个命令都是 idempotent 的，可以独立运行也可以组合。

## 4. 真实跑通的数据

我自己仓 GitNexus 33 篇笔记导入：
- 自动加 frontmatter（source_repo / last_synced / ebbinghaus_stage 等）
- 130 条 cross-repo wikilink 自动连边（98% 解析率）
- 中文文件名 + 英文 slug 通过 EN→ZH 词典 100% 对齐
- LiveSync 实时双向同步 5 秒级

## 5. 与现有方案的差异

不重复别人的工作：每个开源仓都很好，pwiki 只补一件事——
"装上即跑"。原生 multi-repo + 中文友好 + JSON Canvas + 早报 +
艾宾浩斯一并打包。

## 6. 仓库

GitHub: https://github.com/zxs1633079383/pwiki

MIT 协议。欢迎 PR。

---

下一步规划：
- 0.2 加 query 子命令（真正的 RAG hybrid）
- 0.3 加 web UI 看 Canvas
- 0.4 推出 hosted 版（Fly.io 一键部署，省掉 CouchDB 配置苦工）
```

---

## 🎯 发布节奏（建议执行顺序）

| 时段 | 平台 | 文案 | 备注 |
|---|---|---|---|
| 周二 09:00–11:00 EST | X / 推特英文圈 | 英文 thread（A hook） | 主战场 |
| 同日 22:00 CST | X 中文圈 | 上面 6 条中文 thread | |
| 周二 23:00 CST | 即刻 | 即刻长动态 | |
| 周三 上午 | 知乎 | 长文专栏 | |
| 周三 晚上 | 小红书 | 笔记 + 8 个 tag | |
| 周四 上午 | HN ShowHN | 自己写 ShowHN 文案（不照搬 Twitter） | 高权重平台 |
| 周四 晚上 | r/ObsidianMD + r/LocalLLaMA | 各自重写文案，禁同文 | |

## 通用注意

- @karpathy（让原作者看到，他可能 quote-RT 放大）
- 不要在主帖里堆链接，统统放在第一条评论 / 回复
- 主 thread 0 hashtag（X 算法不喜欢），小红书除外
- 如果第一波数据 < 期望（24h 互动 < 50），改 hook 重发，别死磕原文
