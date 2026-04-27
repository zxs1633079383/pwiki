#!/usr/bin/env bash
# Set up a Vault with the minimal scaffolding pwiki needs.
# Templates here mirror the production Vault layout (Chinese 4-section daily,
# bilingual repo-index) so demo output matches what README and launch-tweet promise.
#
# Usage:  bash examples/setup-demo.sh [VAULT_PATH]   # default: /tmp/demo-vault
set -euo pipefail

VAULT="${1:-/tmp/demo-vault}"
echo "==> setting up demo Vault at $VAULT"
rm -rf "$VAULT"
mkdir -p "$VAULT/repos" "$VAULT/daily" "$VAULT/canvas" "$VAULT/opportunities" \
         "$VAULT/evolution" "$VAULT/_meta" "$VAULT/_templates" "$VAULT/.obsidian"

# Ebbinghaus spaced-repetition rules (read by `pwiki brief`)
cat > "$VAULT/_meta/ebbinghaus.md" <<'EOF'
---
type: meta
purpose: 艾宾浩斯遗忘曲线复习规则
---

# Ebbinghaus 复习曲线

每篇笔记的 frontmatter 维护：
- `ebbinghaus_stage` （0..6）
- `last_reviewed`   （ISO 日期）

| stage | 下次间隔 | 含义 |
|-------|---------|------|
| 0 | +1d   | 刚学，明天必复 |
| 1 | +3d   | 短期巩固 |
| 2 | +7d   | 一周回顾 |
| 3 | +15d  | 半月校验 |
| 4 | +30d  | 月度回访 |
| 5 | +60d  | 已掌握，季度抽查 |
| 6+| +120d | 长期记忆 |

复习成功 → `stage += 1`；复习失败 → `stage = max(0, stage - 1)`；都更新 `last_reviewed = today`。
EOF

# Repo-index template (used by `pwiki sync` to render Vault/repos/<repo>/_index.md)
cat > "$VAULT/_templates/repo-index.md" <<'EOF'
---
type: repo-index
repo: {{repo}}
source_path: {{source_path}}
last_synced: {{date}}
note_count: {{count}}
tags: [repo, index]
---

# {{repo}} · 索引

## 仓库简介

> 由 pwiki sync 生成；可手工编辑此段加详细描述。

- **路径：** `{{source_path}}`
- **最后同步：** {{date}}
- **笔记数：** {{count}}

## 概念聚类

> 由 LLM 在导入时初步聚类；可手工调整。

### 实体（Entities）
{{entities_list}}

### 操作（Operations）
{{operations_list}}

### 概念（Concepts）
{{concepts_list}}

### 对比（Comparisons）
{{comparisons_list}}

## 全部笔记

{{full_list}}
EOF

# Daily-brief template (used by `pwiki brief`) — 4 sections matching README
cat > "$VAULT/_templates/daily.md" <<'EOF'
---
type: daily-brief
date: {{date}}
weekday: {{weekday}}
quadrant: {{quadrant}}
generated_by: pwiki-brief
---

# {{date}} 早报

## ① 今日复习（艾宾浩斯到期）

{{review_list}}

> 复习方法：每条 30 秒回忆要点 → 看完原文 → 在末尾用一句话写下"今天再读的新感受"，
> 然后让 brief 在第二天的早报里更新该篇的 `ebbinghaus_stage`。

## ② 10 个前沿方向

> 来源：跨仓 git log + Vault 概念碰撞 + 当周创业/技术热点。
> 标准：每条必须包含 [假设] [信号] [最小验证]，禁止鸡汤。

1. ...
2. ...
3. ...
4. ...
5. ...
6. ...
7. ...
8. ...
9. ...
10. ...

## ③ 今日深度商机（1 个）

**主题：** ...

- **一句话假设：**
- **用户痛点（看到了什么信号）：**
- **现有方案 & 差距：**
- **最小可验证产品（周末跑通）：**
- **死亡条件（看到什么我们停手）：**
- **关联仓库 / 笔记：** [[...]]

> 如果这条值得继续推，移到 `opportunities/` 展开。

## ④ 自我演进 — {{quadrant}}

{{evolution_block}}

---

## 反馈给明天

- 今天哪条复习卡住了？→ stage 该降的降。
- 哪条方向有信号？→ 升级到 opportunities/ 跟踪。
- 哪条自我演进值得明天反复看？→ 加 #revisit 标签。
EOF

# Opportunity template (referenced from daily §③)
cat > "$VAULT/_templates/opportunity.md" <<'EOF'
---
type: opportunity
status: 探索
created: {{date}}
related_repos: []
tags: []
---

# {{title}}

## 一句话假设

> 如果 _____ 给 _____ 提供 _____，那么 _____ 会愿意 _____。

## 信号（为什么现在）

- 信号 1（数据/事件/用户言论 + 来源）：
- 信号 2：

## 解法草图

- 核心机制：
- 与现有方案的不可被复制差异：

## MVP（周末能跑通的边界）

- 输入：
- 输出：

## 死亡条件

> 满足任何一条立刻丢弃，不要养。

- [ ] ...

## 时间盒

- 第 1 周：
- 第 2 周：
- 第 4 周（必决断）：继续 / 转向 / 丢弃

## 进展日志

- {{date}} — 创建。
EOF

# Minimal Obsidian config so the folder is recognized as a Vault
cat > "$VAULT/.obsidian/app.json" <<'EOF'
{}
EOF

echo "==> ready: $VAULT"
ls -la "$VAULT"
