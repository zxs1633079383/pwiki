# pwiki 发布手册

完整版本发布的 3 个动作：① GitHub push（已完成）② PyPI 上传 ③ Twitter / 多平台文案。

## ✅ ① GitHub（已完成）

仓库：https://github.com/zxs1633079383/pwiki
状态：public · main 分支 · 36+ tracked file · MIT · GitHub Actions 已配置

> **包名说明**：PyPI 上 `pwiki` 已被一个 MediaWiki 客户端库占用（Fastily/pwiki, v1.3.1），所以本项目在 PyPI 发布为 **`pwiki-cli`**。
> 影响范围（**不变**）：
> - GitHub 仓库名仍是 `pwiki`
> - CLI 命令仍是 `pwiki <subcommand>`
> - Python import 仍是 `import pwiki`
> - 所有 docs / launch-tweet / commit message 中的项目名仍是 pwiki
> 影响范围（**变化**）：
> - 安装命令：`pip install pwiki-cli`

```bash
# 后续推送变更
cd ~/workspace/ai-workspace/pwiki
git add . && git commit -m "..."
git push
```

---

## 🟡 ② PyPI 上传（等你给 token）

让 `pip install pwiki` 真的从 PyPI 装上。**前置一次性配置**：

### Step 1 — 申请 PyPI API token

1. 注册 / 登录 https://pypi.org（如果没账号）
2. 打开 https://pypi.org/manage/account/token/
3. 点 **"Add API token"** → name 填 `pwiki-release` → scope 选 **"Entire account"**（首次发布必须；之后可改为 project-scoped）
4. **复制 token**（以 `pypi-AgE...` 开头），它只显示一次

### Step 2 — 配置 ~/.pypirc

```bash
cat > ~/.pypirc <<'EOF'
[pypi]
username = __token__
password = pypi-AgE...你的token...
EOF
chmod 600 ~/.pypirc
```

### Step 3 — 一键发布

```bash
cd ~/workspace/ai-workspace/pwiki
bash scripts/release.sh
```

`scripts/release.sh` 会：
1. 装 build / twine（如未装）
2. `python3 -m build` 生成 dist/*.tar.gz dist/*.whl
3. `python3 -m twine check dist/*` 验证元数据
4. `python3 -m twine upload dist/*` 上传

### 验证发布成功

```bash
pip install pwiki-cli   # 注意：PyPI 包名 `pwiki` 已被占用，本仓发布为 `pwiki-cli`
pwiki --version         # CLI 命令仍是 pwiki，import 路径仍是 import pwiki
```

PyPI 主页：https://pypi.org/project/pwiki-cli/

### 后续版本更新

修 `pyproject.toml` 里的 version → `bash scripts/release.sh` 一行搞定。
**注意 PyPI 不允许相同版本号重传**——bug fix 至少要 0.1.1。

---

## ✅ ③ Twitter / 多平台文案

| 文件 | 平台 |
|---|---|
| [`docs/launch-tweet.md`](docs/launch-tweet.md) | X 英文圈（主 thread + 2 备选 hook） |
| [`docs/launch-tweet-zh.md`](docs/launch-tweet-zh.md) | X 中文圈 / 即刻 / 小红书 / 知乎 |

发布节奏建议见 `docs/launch-tweet-zh.md` 末尾。

发布前 checklist：

- [x] demo.gif 已 commit 进 repo（README 已引用）
- [x] GitHub repo public
- [x] README 卖货级 + Karpathy quote
- [x] LICENSE = MIT
- [ ] PyPI 已上线（待 ② 完成）
- [ ] Twitter pin 主 thread

---

## 后续 4 周节奏

跟着 Vault 里的 [`opportunities/pwiki.md`](file:///Users/mac28/Documents/Obsidian%20Vault/opportunities/pwiki.md) 4 周时间盒走。

死亡条件 / 决策矩阵都已写明，到时按指标拍。
