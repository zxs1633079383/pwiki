"""Local semantic index for `pwiki query --rag`.

Backend: fastembed (qdrant), ONNX runtime — small footprint vs sentence-transformers.
Default model: intfloat/multilingual-e5-small (works for both English and Chinese).
Storage:  <vault>/.pwiki/embeddings.npy   (N, D float32, L2-normalized)
          <vault>/.pwiki/meta.jsonl        (N lines: {file, heading, text, fm})
          <vault>/.pwiki/index.json        (model name, dim, built_at, n_chunks)

No faiss. Pure numpy cosine similarity — fine up to ~50k chunks (~30MB index).

Install:  pip install 'pwiki[rag]'   (adds fastembed + numpy)
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys

INDEX_DIRNAME = ".pwiki"
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_CHARS = 1000
MIN_CHUNK_CHARS = 40

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING_RE = re.compile(r"(?m)^(#{1,3}\s+.*)$")


def _import_deps():
    """Lazy import: keep pwiki itself dep-free unless --rag is used."""
    import warnings as _w
    # fastembed 0.8 emits a one-time UserWarning about mean pooling vs CLS for the
    # multilingual MiniLM model. It's informational only and pollutes every CLI
    # run. Silence it; the embeddings remain functionally identical for our use.
    _w.filterwarnings(
        "ignore",
        message=".*mean pooling.*",
        category=UserWarning,
    )
    _w.filterwarnings(
        "ignore",
        message=".*pinning fastembed.*",
        category=UserWarning,
    )
    try:
        from fastembed import TextEmbedding  # type: ignore
        import numpy as np  # type: ignore
    except ImportError:
        sys.exit(
            "pwiki query --rag requires the [rag] extra.\n"
            "Install:  pip install 'pwiki-cli[rag]'\n"
            "(adds fastembed + numpy; first use downloads ~120MB ONNX model)"
        )
    return TextEmbedding, np


def parse_fm(text: str):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def chunk_doc(rel_path: str, fm: dict, body: str):
    """Split body at H1/H2/H3 boundaries, then size-cap each chunk."""
    parts = HEADING_RE.split(body)
    cur_heading = ""
    cur_buf: list[str] = []

    def flush():
        text = "".join(cur_buf).strip()
        if len(text) < MIN_CHUNK_CHARS:
            return []
        out = []
        for i in range(0, len(text), CHUNK_CHARS):
            piece = text[i:i + CHUNK_CHARS].strip()
            if piece:
                out.append({
                    "file": rel_path,
                    "heading": cur_heading.strip(),
                    "text": piece,
                    "source_repo": fm.get("source_repo", ""),
                })
        return out

    chunks = []
    for p in parts:
        if not p:
            continue
        if HEADING_RE.match(p):
            chunks.extend(flush())
            cur_buf = []
            cur_heading = p
        else:
            cur_buf.append(p)
    chunks.extend(flush())
    return chunks


def iter_vault_chunks(vault: pathlib.Path):
    repos = vault / "repos"
    if not repos.is_dir():
        return
    for md in sorted(repos.rglob("*.md")):
        if md.name == "_index.md":
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue
        fm, body = parse_fm(text)
        rel = md.relative_to(vault).as_posix()
        yield from chunk_doc(rel, fm, body)


def build_index(vault: pathlib.Path, model_name: str = DEFAULT_MODEL,
                quiet: bool = False) -> dict:
    TextEmbedding, np = _import_deps()
    chunks = list(iter_vault_chunks(vault))
    if not chunks:
        sys.exit(f"nothing to index under {vault}/repos")
    if not quiet:
        print(f"==> chunked {len(chunks)} segments from Vault/repos")

    if not quiet:
        print(f"==> loading embedding model: {model_name}")
    model = TextEmbedding(model_name=model_name)

    docs = [f"{c['heading']}\n{c['text']}".strip() for c in chunks]
    if not quiet:
        print(f"==> embedding {len(docs)} chunks…")
    emb = np.array(list(model.embed(docs)), dtype="float32")
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    emb = emb / norms

    idx_dir = vault / INDEX_DIRNAME
    idx_dir.mkdir(exist_ok=True)
    np.save(idx_dir / "embeddings.npy", emb)
    with (idx_dir / "meta.jsonl").open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    info = {
        "model": model_name,
        "dim": int(emb.shape[1]),
        "n_chunks": int(emb.shape[0]),
        "built_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    (idx_dir / "index.json").write_text(json.dumps(info, indent=2))
    if not quiet:
        print(f"==> wrote {idx_dir} ({emb.shape}, {emb.nbytes/1024:.1f} KB)")
    return info


def load_index(vault: pathlib.Path):
    TextEmbedding, np = _import_deps()
    idx_dir = vault / INDEX_DIRNAME
    emb_path = idx_dir / "embeddings.npy"
    meta_path = idx_dir / "meta.jsonl"
    info_path = idx_dir / "index.json"
    if not emb_path.is_file() or not meta_path.is_file():
        sys.exit(
            "RAG index not found. Build it first:\n"
            "  pwiki query --rag --rebuild '<any query>'"
        )
    emb = np.load(emb_path)
    info = json.loads(info_path.read_text()) if info_path.is_file() else {}
    with meta_path.open(encoding="utf-8") as f:
        meta = [json.loads(line) for line in f if line.strip()]
    return emb, meta, info


def search(vault: pathlib.Path, query: str, top: int = 10):
    TextEmbedding, np = _import_deps()
    emb, meta, info = load_index(vault)
    model = TextEmbedding(model_name=info.get("model", DEFAULT_MODEL))
    q_vec = list(model.embed([query]))[0].astype("float32")
    n = np.linalg.norm(q_vec)
    if n > 0:
        q_vec = q_vec / n
    sims = emb @ q_vec  # cosine (both already L2-normalized)
    top_idx = np.argsort(-sims)[:top]
    return [(float(sims[i]), meta[i]) for i in top_idx]
