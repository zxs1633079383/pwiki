#!/usr/bin/env python3
"""
obsidian-bridge follow-up: parse a synced repo's 索引.md / index.md to extract
[[english-slug]] → 中文名 mappings, then add `aliases:` frontmatter to the
matching note files so wikilinks resolve in Obsidian's graph.

Strategy:
  1. Read Vault/repos/<repo>/索引.md (or index.md).
  2. For each line `- [[slug]] — **中文名**: ...` (also handles non-bold form),
     capture (slug, 中文名).
  3. For each (slug, 中文名), find the best file under that repo by:
     a. exact filename stem == 中文名
     b. filename stem contains 中文名 (or 中文名 contains filename stem,
        for cases like "多仓库匹配机制" vs file "多仓库匹配.md")
     c. H1 heading (first `^# ` line after frontmatter) contains 中文名
  4. Merge slug into target file's `aliases:` frontmatter list (idempotent).
  5. Print mapping stats.

Usage:
    add_aliases.py <repo_name> [--vault PATH] [--dry-run]
"""
import argparse
import pathlib
import re
import sys

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
INDEX_LINE_BOLD = re.compile(
    r"^- \[\[([a-z0-9][a-z0-9_\-]*)\]\]\s*[—-]\s*\*\*([^*]+?)\*\*"
)
INDEX_LINE_PLAIN = re.compile(
    r"^- \[\[([a-z0-9][a-z0-9_\-]*)\]\]\s*[—-]\s*([^：:（(\n]+?)(?:\s*[：:（(]|$)"
)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

# Trim common Chinese suffixes that pad concept names but are absent in filenames.
TRIM_SUFFIXES = ["机制", "策略", "方式", "方法", "模型", "流程", "结构",
                 "算法", "顺序与分发", "引擎", "管线", "系统"]

# English-token → Chinese filename-fragment dictionary for Pass-3 fallback.
# When a slug like `mcp-server` has no **bold name** in the index, we still
# want to match it to `MCP服务器.md` by translating tokens.
EN_ZH = {
    "package": "包", "module": "模块", "server": "服务器", "backend": "后端",
    "registry": "注册表", "contract": "契约", "call": "调用",
    "resolution": "解析", "dag": "DAG", "scope": "作用域",
    "pipeline": "流水线", "staleness": "过期", "detection": "检测",
    "cli": "命令行", "web": "网页", "shared": "共享", "mcp": "MCP",
    "local": "本地", "language": "语言", "providers": "提供者",
    "provider": "提供者", "group": "分组", "ladybugdb": "LadybugDB",
    "storage": "存储", "embeddings": "向量嵌入", "embedding": "向量嵌入",
    "wiki": "Wiki", "generator": "生成器", "worker": "工作", "pool": "池",
    "analyze": "分析", "flow": "流程", "tools": "工具", "tool": "工具",
    "reference": "参考", "sync": "同步", "setup": "配置", "oss": "开源",
    "enterprise": "企业版", "vs": "对比", "import": "导入",
    "mro": "方法解析顺序", "dispatch": "分发", "blast": "爆炸",
    "radius": "半径", "knowledge": "知识", "graph": "图谱",
    "hybrid": "混合", "search": "搜索", "config": "配置",
}


def parse_fm(text: str):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text, ""
    fm: dict = {}
    raw = m.group(1)
    for line in raw.splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    body = text[m.end():]
    return fm, body, raw


def serialize_fm(fm: dict) -> str:
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            inner = ", ".join(str(x) for x in v)
            lines.append(f"{k}: [{inner}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)


def parse_aliases_field(raw: str) -> list:
    """Parse `tags: [a, b, c]` style list value into a Python list."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inside = raw[1:-1].strip()
        if not inside:
            return []
        return [x.strip() for x in inside.split(",") if x.strip()]
    return [x for x in raw.split(",") if x.strip()] if raw else []


def find_index_file(repo_dir: pathlib.Path):
    for name in ("索引.md", "index.md", "INDEX.md", "Index.md"):
        p = repo_dir / name
        if p.is_file():
            return p
    return None


def parse_index(index_path: pathlib.Path):
    """Yield (slug, name) pairs."""
    out = []
    seen = set()
    text = index_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = INDEX_LINE_BOLD.match(line) or INDEX_LINE_PLAIN.match(line)
        if not m:
            continue
        slug, name = m.group(1).strip(), m.group(2).strip()
        # de-duplicate (some indexes list a slug under multiple sections)
        if slug in seen:
            continue
        seen.add(slug)
        out.append((slug, name))
    return out


def normalize_candidates(name: str):
    """Return progressively shorter forms of `name` to widen matching."""
    cands = {name}
    for suf in TRIM_SUFFIXES:
        if name.endswith(suf) and len(name) > len(suf):
            cands.add(name[:-len(suf)])
    # also drop bracketed parens / English in title
    cands.add(re.sub(r"[（(].*?[）)]", "", name).strip())
    return [c for c in cands if c]


def first_h1(body: str) -> str:
    m = H1_RE.search(body)
    return m.group(1).strip() if m else ""


def slug_tokens_zh(slug: str) -> list:
    """Translate slug tokens through EN_ZH; tokens not in dict are kept as-is."""
    raw = [t for t in re.split(r"[\-_]", slug.lower()) if t and t not in {"and", "the", "of", "to"}]
    out = []
    for t in raw:
        out.append(EN_ZH.get(t, t))
    return out


def best_match(slug: str, name: str, files: list, body_h1: dict):
    cands = normalize_candidates(name)
    # Pass 1: filename stem exact / contains
    for f in files:
        stem = f.stem
        for c in cands:
            if stem == c or c in stem or stem in c:
                return f
    # Pass 2: H1 contains any candidate
    for f in files:
        h1 = body_h1.get(f, "")
        for c in cands:
            if c and c in h1:
                return f
    # Pass 3: translate slug tokens via EN_ZH and score against filename stems.
    zh_tokens = slug_tokens_zh(slug)
    if not zh_tokens:
        return None
    best, best_score = None, 0
    for f in files:
        stem = f.stem
        score = sum(1 for t in zh_tokens if t and (t in stem or stem in t))
        # need at least 2 matching tokens, OR a single token covering most of the stem
        if score > best_score and (score >= 2 or (score == 1 and len(zh_tokens) == 1)):
            best, best_score = f, score
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    vault = pathlib.Path(args.vault).expanduser().resolve()
    repo_dir = vault / "repos" / args.repo
    if not repo_dir.is_dir():
        sys.exit(f"repo dir not found: {repo_dir}")

    idx = find_index_file(repo_dir)
    if not idx:
        sys.exit(f"no index file (索引.md / index.md) in {repo_dir}")

    pairs = parse_index(idx)
    print(f"==> parsed {len(pairs)} (slug, 中文名) pairs from {idx.name}")

    files = [p for p in repo_dir.rglob("*.md")
             if p.name not in ("_index.md", idx.name)]
    body_h1: dict = {}
    file_state: dict = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        fm, body, _raw = parse_fm(text)
        body_h1[f] = first_h1(body)
        file_state[f] = (fm, body, text)

    matched, unmatched = {}, []
    for slug, name in pairs:
        f = best_match(slug, name, files, body_h1)
        if f:
            matched.setdefault(f, []).append(slug)
        else:
            unmatched.append((slug, name))

    changed = 0
    for f, slugs in matched.items():
        fm, body, original = file_state[f]
        existing = parse_aliases_field(fm.get("aliases", ""))
        merged = list(dict.fromkeys(existing + slugs))  # preserve order, unique
        if merged == existing:
            continue  # already up-to-date
        fm["aliases"] = merged
        new_text = serialize_fm(fm) + body.lstrip("\n")
        if not args.dry_run:
            f.write_text(new_text, encoding="utf-8")
        changed += 1

    print(f"==> matched: {len(matched)} files, total slugs: {sum(len(v) for v in matched.values())}")
    print(f"==> unmatched: {len(unmatched)}")
    for slug, name in unmatched[:20]:
        print(f"     - [[{slug}]] = '{name}'")
    if len(unmatched) > 20:
        print(f"     ... and {len(unmatched) - 20} more")
    print(f"==> {'(dry-run) would update' if args.dry_run else 'updated'}: {changed} file(s)")


if __name__ == "__main__":
    main()
