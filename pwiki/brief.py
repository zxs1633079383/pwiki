#!/usr/bin/env python3
"""
morning-brief: assemble today's daily/<date>.md skeleton with the review queue
filled in and a 'materials' block for the LLM to populate the rest.

The script does NOT call any LLM. It produces a deterministic scaffold; the
caller (Claude in the current session) reads the file and fills sections
② 10 directions, ③ deep opportunity, and ④ self-evolution in place.

Usage:
    build_brief.py [--vault PATH] [--repos-root PATH ...] [--lookback-days N]
"""
import argparse
import datetime as dt
import pathlib
import re
import subprocess
import sys

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"
DEFAULT_REPOS_ROOTS = [pathlib.Path.home() / "workspace"]

# stage → days until next review (Ebbinghaus, see _meta/ebbinghaus.md)
INTERVALS = {0: 1, 1: 3, 2: 7, 3: 15, 4: 30, 5: 60}
INTERVAL_LONG = 120

# weekday() Mon=0..Sun=6 — matches evolution/_quadrants.md
QUADRANT_BY_WEEKDAY = {
    0: "思维", 4: "思维",
    1: "知识宽度", 5: "知识宽度",
    2: "产品视野", 6: "产品视野",
    3: "创业 & 风投",
}
WEEKDAY_ZH = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_fm(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def parse_date(s: str, default: dt.date) -> dt.date:
    try:
        return dt.date.fromisoformat(s.strip())
    except Exception:
        return default


def stage_interval(stage: int) -> int:
    return INTERVALS.get(stage, INTERVAL_LONG)


def is_due(fm: dict, today: dt.date):
    raw_stage = fm.get("ebbinghaus_stage", "0")
    try:
        stage = int(str(raw_stage).split("#")[0].strip())
    except Exception:
        stage = 0
    last = parse_date(fm.get("last_reviewed", ""), today)
    interval = stage_interval(stage)
    return today >= last + dt.timedelta(days=interval), stage, last


def scan_due(vault: pathlib.Path, today: dt.date):
    out = []
    repos = vault / "repos"
    if not repos.is_dir():
        return out
    for md in repos.rglob("*.md"):
        if md.name == "_index.md":
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_fm(text)
        if not fm.get("source_repo"):
            continue
        due, stage, last = is_due(fm, today)
        if due:
            rel = md.relative_to(vault)
            out.append((stage, last.isoformat(), str(rel), md.stem))
    out.sort(key=lambda x: (x[0], x[1]))
    return out


def find_git_repos(roots, max_depth=4):
    """Find directories containing .git, up to max_depth from each root."""
    found = []
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob(".git"):
            if not p.is_dir():
                continue
            depth = len(p.relative_to(root).parts)
            if depth > max_depth:
                continue
            found.append(p.parent)
    # dedupe, prefer shorter paths first
    seen = set()
    uniq = []
    for r in sorted(found, key=lambda x: (len(x.parts), str(x))):
        if r in seen:
            continue
        seen.add(r)
        uniq.append(r)
    return uniq


def git_log_since(repo: pathlib.Path, since_date: str, n: int = 5):
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "log",
             f"--since={since_date}", "--pretty=%h %s", f"-n{n}"],
            capture_output=True, text=True, timeout=8,
        )
        if r.returncode != 0:
            return []
        return [ln for ln in r.stdout.splitlines() if ln.strip()]
    except Exception:
        return []


def gather_signals(repos_roots, lookback_days, max_repos=15):
    since = (dt.date.today() - dt.timedelta(days=lookback_days)).isoformat()
    signals = []
    for repo in find_git_repos(repos_roots):
        lines = git_log_since(repo, since)
        if lines:
            signals.append((repo.name, str(repo), lines))
        if len(signals) >= max_repos:
            break
    return signals


def render(today: dt.date, due_list, signals, template: str,
           weekday_zh: str, quadrant: str) -> str:
    if due_list:
        review_block = "\n".join(
            f"- [stage={s}] [[{name}]] — `{path}` (last: {last})"
            for s, last, path, name in due_list
        )
    else:
        review_block = "_今日无到期笔记。可主动选 1–2 条 stage=0 的笔记巩固。_"

    body = (template
            .replace("{{date}}", today.isoformat())
            .replace("{{weekday}}", weekday_zh)
            .replace("{{quadrant}}", quadrant)
            .replace("{{review_list}}", review_block)
            .replace("{{evolution_block}}",
                     f"_待 LLM 填：今日维度【{quadrant}】，"
                     f"输出 1 条具体可复述的演进点（含数字 / 反例 / 一句话结论）。_"))

    materials = ["", "---", "", "## 素材区（仅供 LLM 填 ②③④，写完可手动删除此节）", ""]
    materials.append("### 跨仓最近活跃（git log 摘要）")
    if signals:
        for name, path, lines in signals:
            materials.append(f"- **{name}** — `{path}`")
            for ln in lines:
                materials.append(f"  - {ln}")
    else:
        materials.append("_最近无活跃仓库（lookback 内 0 commit）_")

    materials += [
        "",
        "### 复习候选汇总（用于挑可碰撞的概念）",
        f"_共 {len(due_list)} 篇到期，见上方板块①_",
        "",
        "### LLM 填表指引",
        "- 板块②（10 方向）：从近期 commit 主题 + 到期复习概念里抓 cross-repo 联想，每条带 [假设/信号/最小验证]。",
        "- 板块③（深度商机）：从②里挑 1 条信号最强的展开；如周末跑得通，写到 `opportunities/`.",
        f"- 板块④（自我演进）：维度=【{quadrant}】，按 `evolution/_quadrants.md` 的产出标准。",
    ]

    return body.rstrip() + "\n" + "\n".join(materials) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--repos-root", action="append", default=None,
                    help="repeatable; defaults to ~/workspace")
    ap.add_argument("--lookback-days", type=int, default=7)
    args = ap.parse_args()

    vault = pathlib.Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        sys.exit(f"vault not found: {vault}")
    roots = [pathlib.Path(p).expanduser().resolve()
             for p in (args.repos_root or DEFAULT_REPOS_ROOTS)]

    today = dt.date.today()
    weekday_idx = today.weekday()
    weekday_zh = WEEKDAY_ZH[weekday_idx]
    quadrant = QUADRANT_BY_WEEKDAY[weekday_idx]

    tpl_path = vault / "_templates" / "daily.md"
    if not tpl_path.is_file():
        sys.exit(f"missing template: {tpl_path}")
    template = tpl_path.read_text(encoding="utf-8")

    due_list = scan_due(vault, today)
    signals = gather_signals(roots, args.lookback_days)

    daily_path = vault / "daily" / f"{today.isoformat()}.md"
    daily_path.parent.mkdir(parents=True, exist_ok=True)
    if daily_path.exists():
        bak = daily_path.with_suffix(".md.bak")
        bak.write_text(daily_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"==> existing daily backed up to {bak.name}", file=sys.stderr)

    out = render(today, due_list, signals, template, weekday_zh, quadrant)
    daily_path.write_text(out, encoding="utf-8")

    print(f"==> wrote {daily_path}")
    print(f"   weekday={weekday_zh}, quadrant={quadrant}")
    print(f"   due notes={len(due_list)}, active repos={len(signals)}")


if __name__ == "__main__":
    main()
