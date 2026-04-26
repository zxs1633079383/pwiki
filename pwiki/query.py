"""pwiki query — simple grep-based search over Vault/repos with frontmatter filters.

This is the v0.2-B baseline: deterministic, zero deps, instant. The v0.2-C
upgrade replaces the scoring core with sentence-transformer embeddings while
keeping this CLI surface identical.

Usage:
    pwiki query "blast radius"
    pwiki query "ebbinghaus" --tag concept
    pwiki query "scope" --repo GitNexus
    pwiki query "wiki" --top 20 --vault /custom/path
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
from collections import OrderedDict
from typing import Iterable

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_fm(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def parse_list_field(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        return [x.strip() for x in raw[1:-1].split(",") if x.strip()]
    return [x.strip() for x in raw.split(",") if x.strip()]


def safe_int(s: str, default: int = 0) -> int:
    try:
        return int(str(s).split("#")[0].strip())
    except Exception:
        return default


def safe_date(s: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(s.strip())
    except Exception:
        return None


def iter_repo_files(vault: pathlib.Path, repo_filter: str | None) -> Iterable[pathlib.Path]:
    repos_dir = vault / "repos"
    if not repos_dir.is_dir():
        return
    for repo_dir in sorted(p for p in repos_dir.iterdir() if p.is_dir()):
        if repo_filter and repo_dir.name != repo_filter:
            continue
        for md in sorted(repo_dir.rglob("*.md")):
            if md.name == "_index.md":
                continue
            yield md


def context_lines(text: str, query: str, n: int = 2, max_len: int = 200) -> list[str]:
    """Return up to n lines around the first query hit."""
    lines = text.splitlines()
    q_lower = query.lower()
    out = []
    for i, line in enumerate(lines):
        if q_lower in line.lower():
            for j in range(max(0, i - 0), min(len(lines), i + n)):
                snippet = lines[j].strip()
                if snippet and snippet not in out:
                    out.append(snippet[:max_len])
            if len(out) >= n:
                break
    return out


def score_hit(fm: dict, body: str, query: str) -> float:
    """Composite ranking signal:
        - count of query occurrences in body (case-insensitive)
        - +0.5 if query appears in H1
        - +0.3 if query appears in tags or aliases
        - +ebbinghaus_stage * 0.05 (mature concepts rank slightly higher)
        - +recency boost: +0.2 if last_synced within 30 days
    """
    q_lower = query.lower()
    body_lower = body.lower()
    occurrences = body_lower.count(q_lower)
    if occurrences == 0:
        return 0.0

    score = float(occurrences)

    h1 = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    if h1 and q_lower in h1.group(1).lower():
        score += 0.5

    for field in ("tags", "aliases"):
        items = parse_list_field(fm.get(field, ""))
        if any(q_lower in x.lower() for x in items):
            score += 0.3

    score += safe_int(fm.get("ebbinghaus_stage", "0")) * 0.05

    last = safe_date(fm.get("last_synced", ""))
    if last and (dt.date.today() - last).days <= 30:
        score += 0.2

    return score


def search(vault: pathlib.Path, query: str, *,
           repo_filter: str | None = None,
           tag_filter: str | None = None,
           top: int = 10) -> list[tuple[float, pathlib.Path, dict, list[str]]]:
    results = []
    for f in iter_repo_files(vault, repo_filter):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        fm, body = parse_fm(text)

        if tag_filter:
            tags = parse_list_field(fm.get("tags", ""))
            if not any(tag_filter in t for t in tags):
                continue

        s = score_hit(fm, body, query)
        if s <= 0:
            continue
        ctx = context_lines(body, query, n=2)
        results.append((s, f, fm, ctx))

    results.sort(key=lambda x: -x[0])
    # de-duplicate by path (rglob can yield same path through symlinks; defensive)
    seen = OrderedDict()
    for tup in results:
        seen.setdefault(str(tup[1]), tup)
    return list(seen.values())[:top]


def render(hits, vault: pathlib.Path, query: str) -> str:
    if not hits:
        return f"==> 0 hits for {query!r}\n"
    lines = [f"==> {len(hits)} hit(s) for {query!r}\n"]
    for i, (score, path, fm, ctx) in enumerate(hits, 1):
        rel = path.relative_to(vault).as_posix()
        repo = fm.get("source_repo", "?")
        stage = fm.get("ebbinghaus_stage", "?")
        lines.append(f"  [{i}] score={score:.2f}  {repo} · stage={stage}")
        lines.append(f"      {rel}")
        for c in ctx[:2]:
            lines.append(f"        > {c}")
        lines.append("")
    return "\n".join(lines)


def render_rag(hits, query: str) -> str:
    if not hits:
        return f"==> 0 RAG hits for {query!r}\n"
    lines = [f"==> {len(hits)} RAG hit(s) for {query!r} (cosine similarity)\n"]
    for i, (score, meta) in enumerate(hits, 1):
        repo = meta.get("source_repo") or "?"
        lines.append(f"  [{i}] sim={score:.3f}  {repo}")
        lines.append(f"      {meta.get('file', '?')}")
        if meta.get("heading"):
            lines.append(f"        # {meta['heading']}")
        snippet = (meta.get("text", "") or "").splitlines()
        for s in snippet[:3]:
            s = s.strip()
            if s:
                lines.append(f"        > {s[:200]}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Search the Vault for notes matching a query."
    )
    ap.add_argument("query", help="search string (case-insensitive for grep mode)")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--repo", default=None, help="restrict to a single repo")
    ap.add_argument("--tag", default=None,
                    help="restrict to notes whose tag contains this substring")
    ap.add_argument("--top", type=int, default=10, help="max results to show")
    ap.add_argument("--rag", action="store_true",
                    help="semantic search via local embeddings "
                         "(requires `pip install 'pwiki[rag]'`)")
    ap.add_argument("--rebuild", action="store_true",
                    help="(re)build the RAG index before searching")
    args = ap.parse_args()

    vault = pathlib.Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        sys.exit(f"vault not found: {vault}")

    if args.rag or args.rebuild:
        from pwiki import index_embed
        if args.rebuild:
            index_embed.build_index(vault)
        rag_hits = index_embed.search(vault, args.query, top=args.top)
        sys.stdout.write(render_rag(rag_hits, args.query))
        return 0 if rag_hits else 1

    hits = search(vault, args.query,
                  repo_filter=args.repo, tag_filter=args.tag, top=args.top)
    sys.stdout.write(render(hits, vault, args.query))
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
