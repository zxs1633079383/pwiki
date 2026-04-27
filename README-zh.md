# pwiki

[English](README.md) | **中文**

> **Karpathy 的 LLM Wiki，一行 `pip install` 就能跑。**
> 把任何文件夹变成"AI 真能看懂、自己写得出深度文档"的知识库——
> 写出来的每页都是高级工程师水准，不是糊弄事的 stub。

[![PyPI version](https://img.shields.io/pypi/v/pwiki-cli.svg)](https://pypi.org/project/pwiki-cli/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Karpathy LLM Wiki](https://img.shields.io/badge/pattern-Karpathy_LLM_Wiki-purple.svg)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

![pwiki demo](docs/demo.gif)

> *"Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase."*
> —— Andrej Karpathy，[LLM Wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)，2026 年 4 月

---

## 这是什么

pwiki 把 Karpathy 的 [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
模式打包成 CLI——把你的源码 + 笔记编译成"LLM 能像读代码库一样导航"的结构化 markdown，
不是 RAG 临阵检索、而是预先按 schema 写好。

它是 **(你的代码)** 和 **(你的第二大脑)** 之间的中间件。

## 安装

```bash
pip install -U pwiki-cli     # PyPI 上 pwiki 名被占了，发布为 pwiki-cli；CLI 命令仍是 pwiki
# 或者从源码：
git clone https://github.com/zxs1633079383/pwiki && cd pwiki && pip install -e .
```

要求 Python 3.10+ 和一个文件夹做 Obsidian Vault（默认 `~/Documents/Obsidian Vault`）。

> **Python 3.14 用户注意**：`[rag]` 这个 extra 依赖 `onnxruntime`，目前只有 3.10–3.13 的 wheel。
> 如果你用 3.14，请用 3.13 venv 跑：
> ```bash
> python3.13 -m venv ~/.pwiki-venv
> ~/.pwiki-venv/bin/pip install 'pwiki-cli[rag]'
> ```

## 60 秒上手（一行命令 + 一句话）

```bash
cd ~/your-project
pip install -U "pwiki-cli[rag,serve]"
pwiki init                  # 1. 数项目 LOC，按规模推荐页数
                            # 2. 检测 5 种 AI 工具配置文件
                            # 3. 把 Karpathy 完整 LLM Wiki 协议注入到每一个里
                            # 4. 创建 docs/wiki/ 骨架
```

你会看到（50K 行的项目示例输出）：

```
🐦 pwiki init  (v0.3.1)
  project root: /Users/you/your-project
  language    : javascript  (git: yes)
  scale       : 52,431 LOC across 14 modules → recommend 35-50 wiki pages
  arch docs   : ARCHITECTURE.md, docs/CONVENTIONS.md
✓ AI instructions written:
   updated  CLAUDE.md   (Claude Code)
   updated  AGENTS.md   (Codex CLI)
   updated  GEMINI.md   (Gemini CLI)
✅ pwiki init complete
```

然后打开你的 AI 工具（Cursor / Claude Code / Codex / Gemini CLI），**对它说**：

> "帮我填 wiki" / "扫一下源码写 wiki" / "fill the wiki"

你的 AI 已经在加载的 instruction 里拿到了 **0.3.1 完整协议**：

- **页数按规模缩放** —— LOC 决定推荐页数（<2K → 5-8 / 2K-10K → 10-15 / 10K-50K → 20-30 / 50K+ → 35-50）
- **6 种页类型** —— 实体 / 概念 / 操作 / 对比 / 综合 / 概要
- **强制每页 6 段结构** —— `TL;DR` + ≥2 内容章节 + `源码锚点表`（≥3 行带行号）+ ≥2 对 `常见问题/边缘情况` + ≥2 条 `wikilink` 跨页关联
- **引用密度目标** —— 每页 ≥3 条源码路径引用，必须带行号（`src/foo.ts:123`）
- **质量门槛** —— 每页 400-800 字；stub 页（200 字、复述 README）会被判作不合格、要求重写

AI 自己读你的 README + 源码树 → 写出每一页 → 跑 `pwiki sync` + `pwiki aliases` + `pwiki canvas` →
回报。整个过程**你不用敲任何 pwiki 命令**。

## 手动模式（如果你想自己开车）

```bash
# 1. 把一个 wiki/ 目录同步进 Vault 的 repos/<name>/
pwiki sync ./my-project/docs/wiki my-project

# 2. 把 [[english-slug]] wikilink 解析到中文文件名
#    （处理"wiki 用 slug、文件名是中文短语"这个常见 pattern）
pwiki aliases my-project

# 3. 把每个同步过的仓渲染成 JSON Canvas 图谱（在 Obsidian 里打开）
pwiki canvas

# 4. 生成今天的早报（艾宾浩斯到期复习 + 跨仓概念碰撞）
pwiki brief

# 5. （周日）把本周的自我演进条目按四象限滚总
pwiki evolution

# 6. 在 Vault 里搜笔记 —— grep 模式（零依赖）
pwiki query "blast radius"

# 7. 语义搜索 —— RAG 模式（多语言，全本地）
pip install 'pwiki-cli[rag]'         # 加 fastembed（首次会下载 ~120MB ONNX 模型）
pwiki query --rag --rebuild "warmup"      # 一次性建索引
pwiki query --rag "怎么判断改一个接口会炸到下游哪些服务"   # 中英混合也行

# 8. 在本地 web UI 里浏览 Vault（含 D3 Canvas 图）
pip install 'pwiki-cli[serve]'
pwiki serve --port 8080 --open
# → http://127.0.0.1:8080/
```

每个命令都是 idempotent 的——同样的输入重跑只会更新 frontmatter 时间戳和索引，
**永远不会破坏内容**。

## 你最终会得到什么

- **`repos/<name>/`** —— 你 wiki 的镜像，带托管的 YAML frontmatter（`source_repo` / `last_synced` / `ebbinghaus_stage` / `last_reviewed` / `tags`）
- **`canvas/all-repos.canvas`** —— [JSON Canvas](https://jsoncanvas.org) 知识图：每个仓一个分组、每篇笔记一个节点、`[[wikilink]]` 解析为边（跨仓也连）
- **`daily/<日期>.md`** —— 4 板块早报：① 艾宾浩斯到期复习 ② 10 个前沿方向（跨仓概念碰撞）③ 1 个深度商机 ④ 自我演进（4 象限按工作日轮值）
- **`evolution/<YYYY>-W<WW>.md`** —— ④ 板块按象限分组的周度滚动
- **`opportunities/`** —— ② 板块发现值得深挖的方向时，你自己 promote 过来的目录

整个 Vault 都是纯 markdown：用 Obsidian 打开 / 手动改 / git 版本化 / 用
[Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync) 多端同步——
pwiki 不锁定你。

## 跟其他实现的差异

Karpathy Gist 发布 30 天内出现了 6 个开源实现：

| 项目 | 重点 | pwiki 多做的 |
|---|---|---|
| [`Ar9av/obsidian-wiki`](https://github.com/Ar9av/obsidian-wiki) | 基于 Skill 的框架 / ingest 流水线 | 一行装 / 多仓 Vault / JSON Canvas |
| [`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian) | `/wiki /save /autoresearch` 斜杠命令 | 跨仓概念碰撞 + 艾宾浩斯复习 |
| [`NicholasSpisak/second-brain`](https://github.com/NicholasSpisak/second-brain) | 个人 vault skills | 早报 + 周度演进 |
| Karpathy [原 Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | pattern 本身 | brew-install ready 的 CLI + 每个命令的 help |

详细对比见 [`docs/COMPARISON.md`](docs/COMPARISON.md)。

诚实定位：现有 6 个实现都还要让你 clone 仓 / 配 Python 路径 / 读 50 行教程 /
**手动**对 AI 一页一页指挥写 wiki。pwiki 是一行 pip + 五个子命令 + AI 自动按
GitNexus 标准的协议生成深度页。差异就是这点。

## 路线图

- ✅ **0.1**：5 命令 CLI + JSON Canvas + 艾宾浩斯 + 周度演进
- ✅ **0.2**：alias Pass 4 支持英文文件名 + `pwiki query`（grep / RAG via fastembed 多语言 MiniLM）
- ✅ **0.3.0**：`pwiki init` —— 把 Karpathy 完整 LLM Wiki pattern（3 层架构 / 3 操作 / 6 页类 / 8 步引导 / 7 步 ingest / 5 类 lint）注入到每个 AI 工具的 instruction 文件。AI 自己读源码写 wiki，你说一句话。
- ✅ **0.3**（同时）：`pwiki serve` —— 本地 web UI，含 D3 Canvas 图 + inline grep/RAG 搜索。
- ✅ **0.3.1**：**不写 stub 了。** 项目规模感知（按 LOC 推荐 5-8 / 10-15 / 20-30 / 35-50 页）+ 强制每页 6 段结构（TL;DR + 源码锚点表带行号 + 边缘 Q&A + 跨页关联）+ 引用密度目标 ≥3/页。0.3.0 在 50K 行真实仓上 dogfood 时翻车——AI 写出 8 个 stub 而本应写 25-30 篇深度页。0.3.1 修这个翻车，让 AI 默认走深而不是浅。
- 🟡 **0.4**（hosted，未开工）：一键托管 LiveSync——这样多端同步不再是 CouchDB 苦工。规格：[`docs/0.4-hosted-spec.md`](docs/0.4-hosted-spec.md)。实现 gated on ⭐ ≥ 300（没流量先做 SaaS 是已知反模式）。

## 价格（Freemium）

| 档位 | 价格 | 你拿到什么 |
|---|---|---|
| **OSS（CLI + serve）** | 永久免费 | 0.1 → 0.3 全部 —— 5 命令 CLI、Canvas、艾宾浩斯、演进、本地 RAG（自带 OpenAI key 也能跑）、`pwiki serve` 本地 web UI |
| **Hosted Pro** | $9/月 | 0.4 hosted LiveSync（不用自己运维 CouchDB）+ hosted RAG（embedding 缓存）+ `pwiki.dev/yourname` 公开 URL |
| **Team Pro** | $29/座位/月 | 共享团队 vault + 权限 + 团队聚合早报 + SSO |

## 新手常见踩坑

**Q：`pwiki init` 跑完，AI 不写 wiki？**
A：检查 `<!-- pwiki:begin --> ... <!-- pwiki:end -->` 这一段是不是真的注入到了你的
CLAUDE.md / AGENTS.md / .cursor/rules/pwiki.md 里。然后**重启 AI 工具**让它重新加载
instruction。最后说"帮我填 wiki"。

**Q：AI 写的页太薄，又是 stub？**
A：你装的可能是 0.3.0 之前的版本。`pip install -U pwiki-cli` 升到 0.3.1，然后
`pwiki init -y` 重跑（会原地更新 marker 之间的内容，不动你已有内容）。

**Q：`pwiki query --rag` 报 onnxruntime 错？**
A：你在 Python 3.14。用 3.13 venv 重装，见上面"Python 3.14 用户注意"。

**Q：不想用 Obsidian，能不能只用 pwiki？**
A：可以。Vault 就是普通文件夹，`pwiki sync` 输出纯 markdown。不用 Obsidian 的话，
`pwiki serve` 给你一个本地 web UI 看 Canvas + 搜索。

**Q：我项目里已经有 CLAUDE.md，会被覆盖吗？**
A：不会。pwiki 用 `<!-- pwiki:begin --> ... <!-- pwiki:end -->` 标记包裹自己注入的段，
你的现有内容**完全不动**，重跑 init 也只在 marker 之间原地更新。

## 贡献

欢迎 issue 和 PR。跑测试：

```bash
pip install -e ".[dev]"
pytest
```

如果你在 pwiki 上做了什么——自定义象限、新子命令、不同的 Canvas 布局——
开个 PR 或贴链接给我，我会在这里挂出来。

## 协议

[MIT](LICENSE) —— 商用也行。

## 致谢

- Andrej Karpathy [那个 Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 在 2026 年 4 月开了所有这些后续。
- [Obsidian](https://obsidian.md) 团队和 [kepano](https://github.com/kepano) 维护 [obsidian-skills](https://github.com/kepano/obsidian-skills) 集合。
- [vrtmrz](https://github.com/vrtmrz) 写的 [Self-hosted LiveSync](https://github.com/vrtmrz/obsidian-livesync) —— pwiki 推荐的多端同步层。
- [@karpathy](https://x.com/karpathy) 把一个 markdown 文件夹叫做"编程环境"的那个框架。
