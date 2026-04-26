#!/usr/bin/env python3
"""
obsidian-bridge: sync a repo's wiki/ directory into the Obsidian Vault.

Usage:
    sync.py <source_wiki_dir> <repo_name> [--vault PATH] [--dry-run]

Behavior:
    - Mirrors source_wiki_dir → <vault>/repos/<repo_name>/
    - For each .md, prepends YAML frontmatter if missing; merges if present.
      Adds: source_repo, source_path, last_synced, ebbinghaus_stage(=0),
            last_reviewed(=today), tags(['repo/<name>', dir tag]).
    - Generates <vault>/repos/<repo_name>/_index.md from _templates/repo-index.md.
    - Idempotent: re-running updates last_synced and refreshes _index.md only.
    - Conservative: never overwrites file body, only manages YAML frontmatter.
"""
import argparse
import datetime as dt
import os
import pathlib
import re
import shutil
import sys
from typing import Tuple

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> Tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end():]
    fm: dict = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm, body


def serialize_frontmatter(fm: dict) -> str:
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            inner = ", ".join(str(x) for x in v)
            lines.append(f"{k}: [{inner}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)


def merge(existing: dict, additions: dict) -> dict:
    """Additions don't overwrite human-set fields, except sync metadata."""
    overwrite_keys = {"source_repo", "source_path", "last_synced"}
    out = dict(existing)
    for k, v in additions.items():
        if k in overwrite_keys or k not in out:
            out[k] = v
    return out


def slug_to_dir_tag(rel_dir: str) -> str:
    if not rel_dir or rel_dir == ".":
        return "general"
    return rel_dir.replace("/", "-")


def sync_file(src: pathlib.Path, dst: pathlib.Path,
              repo: str, source_root: pathlib.Path, today: str,
              dry_run: bool) -> str:
    text = src.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    rel = src.relative_to(source_root)
    rel_dir = str(rel.parent)
    additions = {
        "source_repo": repo,
        "source_path": str(rel),
        "last_synced": today,
        "ebbinghaus_stage": fm.get("ebbinghaus_stage", 0),
        "last_reviewed": fm.get("last_reviewed", today),
        "tags": fm.get("tags", f"[repo/{repo}, {slug_to_dir_tag(rel_dir)}]"),
    }
    new_fm = merge(fm, additions)
    new_text = serialize_frontmatter(new_fm) + body.lstrip("\n")
    if dry_run:
        return "DRY"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new_text, encoding="utf-8")
    return "OK"


def gather_categories(repo_dir: pathlib.Path) -> dict:
    """Categorize notes by top-level subdir for the index page."""
    cats: dict = {}
    for md in sorted(repo_dir.rglob("*.md")):
        if md.name.startswith("_"):
            continue
        rel = md.relative_to(repo_dir)
        cat = rel.parts[0] if len(rel.parts) > 1 else "_root"
        link = f"[[{md.stem}]]"
        cats.setdefault(cat, []).append(link)
    return cats


def render_index(repo: str, source_path: str, repo_dir: pathlib.Path,
                 template: pathlib.Path, today: str) -> str:
    cats = gather_categories(repo_dir)
    count = sum(len(v) for v in cats.values())
    if not template.exists():
        body = f"# {repo} 索引\n\nlast_synced: {today}\n笔记数: {count}\n"
        for cat, links in cats.items():
            body += f"\n## {cat}\n\n" + "\n".join(f"- {ln}" for ln in links) + "\n"
        return body
    tmpl = template.read_text(encoding="utf-8")

    def cat_block(name: str) -> str:
        items = cats.get(name, [])
        return "\n".join(f"- {ln}" for ln in items) if items else "_空_"

    full = []
    for cat, links in cats.items():
        full.append(f"### {cat}")
        full.extend(f"- {ln}" for ln in links)
    full_list = "\n".join(full) if full else "_空_"

    out = (
        tmpl.replace("{{repo}}", repo)
            .replace("{{source_path}}", source_path)
            .replace("{{date}}", today)
            .replace("{{count}}", str(count))
            .replace("{{entities_list}}", cat_block("实体"))
            .replace("{{operations_list}}", cat_block("操作"))
            .replace("{{concepts_list}}", cat_block("概念"))
            .replace("{{comparisons_list}}", cat_block("对比"))
            .replace("{{full_list}}", full_list)
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="source wiki directory")
    ap.add_argument("repo", help="repo name (becomes Vault/repos/<repo>/)")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src_root = pathlib.Path(args.source).expanduser().resolve()
    if not src_root.is_dir():
        sys.exit(f"source not found: {src_root}")
    vault = pathlib.Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        sys.exit(f"vault not found: {vault}")
    repo_dir = vault / "repos" / args.repo
    today = dt.date.today().isoformat()

    md_files = sorted(p for p in src_root.rglob("*.md") if p.is_file())
    if not md_files:
        sys.exit(f"no .md files under {src_root}")

    print(f"==> syncing {len(md_files)} files: {src_root} → {repo_dir}")
    counts = {"OK": 0, "DRY": 0}
    for src in md_files:
        rel = src.relative_to(src_root)
        dst = repo_dir / rel
        result = sync_file(src, dst, args.repo, src_root, today, args.dry_run)
        counts[result] += 1
        print(f"   [{result}] {rel}")

    template = vault / "_templates" / "repo-index.md"
    if not args.dry_run:
        index_text = render_index(args.repo, str(src_root), repo_dir, template, today)
        (repo_dir / "_index.md").write_text(index_text, encoding="utf-8")
        print(f"==> wrote {repo_dir / '_index.md'}")

    print(f"==> done: {counts}")


if __name__ == "__main__":
    main()
