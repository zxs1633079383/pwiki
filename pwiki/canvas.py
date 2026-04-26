#!/usr/bin/env python3
"""
vault-canvas: render Vault/canvas/all-repos.canvas (JSON Canvas v1.0)
showing every repo as a group of file nodes, with edges from wikilinks
that resolve to other notes inside the Vault.

Spec: https://jsoncanvas.org/

Usage:
    generate_canvas.py [--vault PATH] [--out FILENAME] [--no-edges]
"""
import argparse
import json
import math
import pathlib
import re
import uuid

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"
WIKILINK_RE = re.compile(r"\[\[([^\[\]\|#]+?)(?:#[^\[\]\|]*)?(?:\|[^\[\]]*)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
ALIASES_RE = re.compile(r"^aliases:\s*\[([^\]]*)\]\s*$", re.MULTILINE)

# layout constants (px)
NODE_W, NODE_H = 220, 70
COL_GAP, ROW_GAP = 60, 30
GROUP_PAD = 40
GROUP_GAP_X = 200
GROUP_GAP_Y = 200


def gen_id() -> str:
    return uuid.uuid4().hex[:16]


def collect_notes(vault: pathlib.Path):
    """Return {repo_name: [(rel_path, stem), ...]} sorted by category/name."""
    repos = {}
    base = vault / "repos"
    if not base.is_dir():
        return repos
    for repo_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        notes = []
        for md in sorted(repo_dir.rglob("*.md")):
            if md.name == "_index.md":
                continue
            rel = md.relative_to(vault)
            notes.append((str(rel), md.stem))
        if notes:
            repos[repo_dir.name] = notes
    return repos


def build_stem_index(vault: pathlib.Path, repos: dict):
    """Map note stem AND each frontmatter alias → vault-relative path.
    First seen wins (intra-repo, top-down)."""
    idx = {}
    for _repo, notes in repos.items():
        for rel, stem in notes:
            idx.setdefault(stem, rel)
            try:
                text = (vault / rel).read_text(encoding="utf-8")
            except Exception:
                continue
            fm = FRONTMATTER_RE.match(text)
            if not fm:
                continue
            am = ALIASES_RE.search(fm.group(1))
            if not am:
                continue
            for raw in am.group(1).split(","):
                alias = raw.strip()
                if alias:
                    idx.setdefault(alias, rel)
    return idx


def extract_links(vault: pathlib.Path, rel_path: str) -> list:
    try:
        text = (vault / rel_path).read_text(encoding="utf-8")
    except Exception:
        return []
    return list({m.group(1).strip() for m in WIKILINK_RE.finditer(text)})


def layout_repo(repo_index: int, notes):
    """Grid-layout a repo's notes. Returns (group_x, group_y, group_w, group_h, file_node_positions)."""
    n = len(notes)
    cols = max(1, int(math.ceil(math.sqrt(n))))
    rows = int(math.ceil(n / cols))
    inner_w = cols * NODE_W + (cols - 1) * COL_GAP
    inner_h = rows * NODE_H + (rows - 1) * ROW_GAP
    group_w = inner_w + 2 * GROUP_PAD
    group_h = inner_h + 2 * GROUP_PAD + 30  # extra for label

    repos_per_row = 3
    col = repo_index % repos_per_row
    row = repo_index // repos_per_row
    group_x = col * (group_w + GROUP_GAP_X)
    group_y = row * (group_h + GROUP_GAP_Y)

    file_positions = []
    for i, (rel, stem) in enumerate(notes):
        c = i % cols
        r = i // cols
        x = group_x + GROUP_PAD + c * (NODE_W + COL_GAP)
        y = group_y + GROUP_PAD + 30 + r * (NODE_H + ROW_GAP)
        file_positions.append((rel, stem, x, y))
    return group_x, group_y, group_w, group_h, file_positions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--out", default="all-repos.canvas",
                    help="filename inside Vault/canvas/")
    ap.add_argument("--no-edges", action="store_true",
                    help="skip wikilink edge resolution")
    args = ap.parse_args()

    vault = pathlib.Path(args.vault).expanduser().resolve()
    repos = collect_notes(vault)
    if not repos:
        print(f"==> no repos found under {vault / 'repos'}; nothing to render")
        return

    nodes, edges = [], []
    file_node_id_by_rel: dict = {}

    for ri, (repo, notes) in enumerate(repos.items()):
        gx, gy, gw, gh, positions = layout_repo(ri, notes)
        nodes.append({
            "id": gen_id(),
            "type": "group",
            "x": gx, "y": gy, "width": gw, "height": gh,
            "label": f"{repo} ({len(notes)})",
        })
        for rel, stem, x, y in positions:
            nid = gen_id()
            nodes.append({
                "id": nid,
                "type": "file",
                "file": rel,
                "x": x, "y": y,
                "width": NODE_W, "height": NODE_H,
            })
            file_node_id_by_rel[rel] = nid

    if not args.no_edges:
        stem_index = build_stem_index(vault, repos)
        seen = set()
        for rel, src_id in file_node_id_by_rel.items():
            for link in extract_links(vault, rel):
                target_rel = stem_index.get(link)
                if not target_rel or target_rel == rel:
                    continue
                tgt_id = file_node_id_by_rel.get(target_rel)
                if not tgt_id:
                    continue
                key = (src_id, tgt_id)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "id": gen_id(),
                    "fromNode": src_id,
                    "fromSide": "right",
                    "toNode": tgt_id,
                    "toSide": "left",
                })

    out_path = vault / "canvas" / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"==> wrote {out_path}")
    print(f"   repos={len(repos)}, file nodes={sum(len(v) for v in repos.values())}, "
          f"edges={len(edges)}")
    if not args.no_edges:
        unresolved = sum(
            1 for rel in file_node_id_by_rel
            for link in extract_links(vault, rel)
            if not build_stem_index(vault, repos).get(link)
        )
        if unresolved:
            print(f"   note: {unresolved} wikilink(s) unresolved "
                  f"(likely English slugs in Chinese-named files; aliases TODO)")


if __name__ == "__main__":
    main()
