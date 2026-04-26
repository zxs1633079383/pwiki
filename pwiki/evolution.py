#!/usr/bin/env python3
"""
evolution-tracker: roll up the past week's daily/<date>.md self-evolution
sections (§④) into a single weekly digest at evolution/<YYYY>-W<WW>.md,
grouped by quadrant.

Usage:
    build_weekly.py [--vault PATH] [--week-of YYYY-MM-DD]

Designed to run on Sunday after the morning brief, but works any day —
defaults to the ISO week of `today`.
"""
import argparse
import datetime as dt
import pathlib
import re
import sys

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"

QUADRANT_BY_WEEKDAY = {
    0: "思维", 4: "思维",
    1: "知识宽度", 5: "知识宽度",
    2: "产品视野", 6: "产品视野",
    3: "创业 & 风投",
}
QUADRANTS_ORDER = ["思维", "知识宽度", "产品视野", "创业 & 风投"]

# Capture the §④ block in a daily file. We rely on the daily template's
# heading prefix "## ④ 自我演进".
SECTION_RE = re.compile(
    r"^##\s*④\s*自我演进[^\n]*\n(.*?)(?=^##\s|\Z)",
    re.DOTALL | re.MULTILINE,
)


def iso_week(d: dt.date) -> tuple:
    iso_year, iso_week, _ = d.isocalendar()
    return iso_year, iso_week


def week_dates(d: dt.date):
    """Mon..Sun of the ISO week containing d."""
    monday = d - dt.timedelta(days=d.weekday())
    return [monday + dt.timedelta(days=i) for i in range(7)]


def extract_section(daily_text: str) -> str:
    m = SECTION_RE.search(daily_text)
    if not m:
        return ""
    body = m.group(1).strip()
    # strip the auto-scaffold placeholder if user never filled it
    if body.startswith("_待 LLM 填") or not body or body.startswith("_LLM"):
        return ""
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--week-of", default=None,
                    help="any date inside the target ISO week, default=today")
    args = ap.parse_args()

    vault = pathlib.Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        sys.exit(f"vault not found: {vault}")

    today = (dt.date.fromisoformat(args.week_of)
             if args.week_of else dt.date.today())
    iso_year, iso_w = iso_week(today)
    days = week_dates(today)

    sections_by_quadrant = {q: [] for q in QUADRANTS_ORDER}
    found_count = 0
    for d in days:
        daily = vault / "daily" / f"{d.isoformat()}.md"
        if not daily.is_file():
            continue
        text = daily.read_text(encoding="utf-8")
        body = extract_section(text)
        if not body:
            continue
        quadrant = QUADRANT_BY_WEEKDAY[d.weekday()]
        sections_by_quadrant[quadrant].append((d.isoformat(), body))
        found_count += 1

    out_path = vault / "evolution" / f"{iso_year}-W{iso_w:02d}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"---",
        f"type: evolution-weekly",
        f"iso_year: {iso_year}",
        f"iso_week: {iso_w}",
        f"week_start: {days[0].isoformat()}",
        f"week_end: {days[-1].isoformat()}",
        f"entries_found: {found_count}",
        f"tags: [evolution, weekly]",
        f"---",
        "",
        f"# 自我演进 · {iso_year}-W{iso_w:02d}",
        "",
        f"> 周期 {days[0].isoformat()} → {days[-1].isoformat()}，"
        f"共抽出 {found_count} 条 §④ 条目。",
        "",
    ]
    for q in QUADRANTS_ORDER:
        lines.append(f"## {q}")
        items = sections_by_quadrant[q]
        if not items:
            lines.append("_本周该维度无记录_")
        for date_iso, body in items:
            lines.append(f"### {date_iso}")
            lines.append(body)
        lines.append("")

    lines += [
        "## 周回看",
        "- 哪条本周写了但下周想不起来？→ 加 #revisit，下周一早报顶到 §①。",
        "- 哪条已经在工作中真正用到？→ 转成正式笔记进 `repos/<repo>/` 或 `_meta/`。",
        "- 哪个维度本周空了？→ 下周固定一天专门补这个 quadrant。",
        "",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"==> wrote {out_path}")
    print(f"   week={iso_year}-W{iso_w:02d}, entries={found_count}")


if __name__ == "__main__":
    main()
