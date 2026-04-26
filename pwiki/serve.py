"""pwiki serve — local web UI for browsing the Vault.

Routes:
    GET  /                          home: repos list + recent dailies + recent ops
    GET  /repo/{name}/              per-repo index (notes by category)
    GET  /note/{path:path}          render single note (markdown → HTML)
    GET  /daily/{date}              render a daily brief
    GET  /canvas/                   Canvas viewer (D3 force layout, SVG)
    GET  /api/canvas.json           raw .canvas JSON (for the viewer JS)
    GET  /api/query?q=...&rag=1     query as JSON (rag=1 → semantic, default grep)

Install: pip install 'pwiki[serve]'
Run:     pwiki serve [--vault PATH] [--port 8080] [--host 127.0.0.1] [--open]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import webbrowser
from typing import Any

DEFAULT_VAULT = pathlib.Path.home() / "Documents" / "Obsidian Vault"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _import_deps():
    try:
        from fastapi import FastAPI, HTTPException, Query  # type: ignore
        from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse  # type: ignore
        from markdown_it import MarkdownIt  # type: ignore
        import uvicorn  # type: ignore
    except ImportError:
        sys.exit(
            "pwiki serve requires the [serve] extra:\n"
            "  pip install 'pwiki[serve]'\n"
            "(adds fastapi + uvicorn + markdown-it-py)"
        )
    return FastAPI, HTTPException, Query, HTMLResponse, JSONResponse, PlainTextResponse, MarkdownIt, uvicorn


def parse_fm(text: str):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


# --------------------------------------------------------------------- HTML

CSS = """
:root {
  --bg: #0f172a; --bg2: #1e293b; --fg: #e2e8f0; --muted: #94a3b8;
  --accent: #a78bfa; --link: #60a5fa; --border: #334155;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
             font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
header { padding: 12px 24px; background: var(--bg2); border-bottom: 1px solid var(--border);
         display: flex; align-items: center; gap: 24px; }
header a { color: var(--fg); text-decoration: none; }
header strong { color: var(--accent); }
header form { margin-left: auto; }
header input { padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border);
               background: var(--bg); color: var(--fg); width: 280px; }
header label { color: var(--muted); margin: 0 8px; }
main { max-width: 1080px; margin: 0 auto; padding: 24px; }
h1 { color: var(--accent); margin-top: 0; }
h1, h2, h3 { color: var(--fg); }
h2 { border-bottom: 1px solid var(--border); padding-bottom: 6px; margin-top: 28px; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border-bottom: 1px solid var(--border); padding: 6px 10px; text-align: left; }
th { color: var(--muted); font-weight: 500; }
.hit { background: var(--bg2); border-left: 3px solid var(--accent);
       padding: 10px 14px; margin: 8px 0; border-radius: 4px; }
.hit small { color: var(--muted); }
.hit .ctx { color: var(--muted); margin-top: 4px; font-size: 13px; }
pre { background: #020617; padding: 12px; border-radius: 6px; overflow-x: auto;
      border: 1px solid var(--border); }
code { background: #1e293b; padding: 1px 5px; border-radius: 3px; font-size: 13px; }
pre code { background: transparent; padding: 0; }
blockquote { border-left: 3px solid var(--accent); padding-left: 12px; color: var(--muted); margin: 8px 0; }
.frontmatter { background: var(--bg2); padding: 8px 12px; border-radius: 4px;
               font-family: monospace; font-size: 13px; color: var(--muted); margin-bottom: 16px; }
.tag { display: inline-block; background: var(--bg2); color: var(--accent);
       padding: 2px 8px; border-radius: 10px; font-size: 12px; margin: 2px; }
"""

HEADER = """<!doctype html>
<html><head><meta charset="utf-8"><title>{title} — pwiki</title>
<style>{css}</style></head><body>
<header>
  <a href="/"><strong>pwiki</strong></a>
  <a href="/canvas/">Canvas</a>
  <form action="/" method="get">
    <input name="q" placeholder="search the vault…" value="{q}" autofocus>
    <label><input type="checkbox" name="rag" value="1" {rag_checked}> RAG</label>
  </form>
</header>
<main>
"""

FOOTER = "</main></body></html>"


def render_html(title: str, body: str, q: str = "", rag: bool = False) -> str:
    head = HEADER.format(title=title, css=CSS, q=q,
                         rag_checked="checked" if rag else "")
    return head + body + FOOTER


# --------------------------------------------------------------------- pages

def page_home(vault: pathlib.Path, q: str, rag: bool) -> str:
    body = []
    if q:
        # delegate to /api/query path-style so we share rendering logic
        from pwiki import query as gq
        if rag:
            try:
                from pwiki import index_embed
                hits = index_embed.search(vault, q, top=20)
                body.append(f"<h1>RAG results for {q!r}</h1>")
                if not hits:
                    body.append("<p><em>No matches.</em></p>")
                for sim, meta in hits:
                    file = meta.get("file", "?")
                    repo = meta.get("source_repo") or "?"
                    head = meta.get("heading", "").strip()
                    text = (meta.get("text") or "")[:300]
                    body.append(
                        f'<div class="hit"><small>sim={sim:.3f} · {repo}</small>'
                        f'<div><a href="/note/{file}">{file}</a></div>'
                        f'{("<small>"+head+"</small>") if head else ""}'
                        f'<div class="ctx">{text}</div></div>'
                    )
            except SystemExit as e:
                body.append(f"<p><em>RAG unavailable: {e}</em></p>")
        else:
            hits = gq.search(vault, q, top=20)
            body.append(f"<h1>Search results for {q!r}</h1>")
            if not hits:
                body.append("<p><em>No matches.</em></p>")
            for score, path, fm, ctx in hits:
                rel = path.relative_to(vault).as_posix()
                repo = fm.get("source_repo", "?")
                stage = fm.get("ebbinghaus_stage", "?")
                ctx_html = "<br>".join(c for c in ctx[:2])
                body.append(
                    f'<div class="hit"><small>score={score:.2f} · {repo} · stage={stage}</small>'
                    f'<div><a href="/note/{rel}">{rel}</a></div>'
                    f'<div class="ctx">{ctx_html}</div></div>'
                )
        return render_html(f"search: {q}", "\n".join(body), q=q, rag=rag)

    # default home
    body.append("<h1>pwiki vault</h1>")
    body.append(f"<p style='color:var(--muted)'>{vault}</p>")
    body.append("<h2>Repos</h2><ul>")
    repos_dir = vault / "repos"
    if repos_dir.is_dir():
        for d in sorted(p for p in repos_dir.iterdir() if p.is_dir()):
            n = sum(1 for _ in d.rglob("*.md")) - 1  # minus _index.md
            body.append(f'<li><a href="/repo/{d.name}/">{d.name}</a> '
                        f'<small style="color:var(--muted)">({n} notes)</small></li>')
    body.append("</ul>")

    body.append("<h2>Recent dailies</h2><ul>")
    daily_dir = vault / "daily"
    if daily_dir.is_dir():
        for d in sorted(daily_dir.glob("*.md"), reverse=True)[:7]:
            body.append(f'<li><a href="/daily/{d.stem}">{d.stem}</a></li>')
    body.append("</ul>")

    body.append("<h2>Active opportunities</h2><ul>")
    op_dir = vault / "opportunities"
    if op_dir.is_dir():
        for d in sorted(op_dir.glob("*.md")):
            body.append(f'<li><a href="/note/opportunities/{d.name}">{d.stem}</a></li>')
    body.append("</ul>")
    return render_html("home", "\n".join(body))


def page_repo(vault: pathlib.Path, repo_name: str) -> str:
    repo_dir = vault / "repos" / repo_name
    if not repo_dir.is_dir():
        return render_html("404", f"<h1>Not found</h1><p>repo {repo_name!r} missing</p>")
    body = [f"<h1>{repo_name}</h1>"]
    by_cat: dict[str, list] = {}
    for md in sorted(repo_dir.rglob("*.md")):
        if md.name == "_index.md":
            continue
        rel = md.relative_to(vault).as_posix()
        rel_in_repo = md.relative_to(repo_dir)
        cat = rel_in_repo.parts[0] if len(rel_in_repo.parts) > 1 else "_root"
        by_cat.setdefault(cat, []).append((md.stem, rel))
    for cat, items in by_cat.items():
        body.append(f"<h2>{cat}</h2><ul>")
        for stem, rel in items:
            body.append(f'<li><a href="/note/{rel}">{stem}</a></li>')
        body.append("</ul>")
    return render_html(f"repo: {repo_name}", "\n".join(body))


def page_note(vault: pathlib.Path, rel_path: str, md_renderer) -> str:
    p = vault / rel_path
    if not p.is_file() or not str(p).startswith(str(vault)):
        return render_html("404", f"<h1>Not found</h1><p>{rel_path}</p>")
    text = p.read_text(encoding="utf-8")
    fm, body = parse_fm(text)
    fm_html = ""
    if fm:
        items = " · ".join(f"<b>{k}:</b> {v}" for k, v in fm.items())
        fm_html = f'<div class="frontmatter">{items}</div>'
    # rewrite [[wikilink]] → /note/<resolved> (best effort: stem match)
    def _wikilink(m):
        target = m.group(1).strip()
        return f'<a href="/wikilink/{target}">[[{target}]]</a>'
    body_with_links = re.sub(r"\[\[([^\[\]\|#]+?)(?:\|([^\[\]]+))?\]\]", _wikilink, body)
    body_html = md_renderer.render(body_with_links)
    page = f"<h1>{p.stem}</h1>{fm_html}{body_html}"
    return render_html(p.stem, page)


def resolve_wikilink(vault: pathlib.Path, link: str) -> str | None:
    """Return relative path of file that matches a [[link]] by stem or alias."""
    repos = vault / "repos"
    if not repos.is_dir():
        return None
    target_lower = link.lower()
    for md in repos.rglob("*.md"):
        if md.name == "_index.md":
            continue
        if md.stem.lower() == target_lower:
            return md.relative_to(vault).as_posix()
        try:
            text = md.read_text(encoding="utf-8")
            fm, _ = parse_fm(text)
            aliases_raw = fm.get("aliases", "").strip()
            if aliases_raw.startswith("[") and aliases_raw.endswith("]"):
                aliases = [a.strip().lower() for a in aliases_raw[1:-1].split(",")]
                if target_lower in aliases:
                    return md.relative_to(vault).as_posix()
        except Exception:
            continue
    return None


def page_daily(vault: pathlib.Path, date: str, md_renderer) -> str:
    p = vault / "daily" / f"{date}.md"
    if not p.is_file():
        return render_html("404", f"<h1>No daily for {date}</h1>")
    text = p.read_text(encoding="utf-8")
    _fm, body = parse_fm(text)
    return render_html(f"daily {date}", f"<h1>{date}</h1>" + md_renderer.render(body))


CANVAS_HTML = """<h1>Canvas</h1>
<svg id="canvas" width="100%" height="800" style="background:#0a0e1a;border:1px solid var(--border);border-radius:6px"></svg>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>
fetch('/api/canvas.json').then(r => r.json()).then(data => {
  const svg = d3.select('#canvas');
  const W = svg.node().clientWidth, H = 800;
  // pre-position file nodes from canvas coords; group nodes ignored for force layout
  const fileNodes = data.nodes.filter(n => n.type === 'file');
  const groups = data.nodes.filter(n => n.type === 'group');
  const nodeIndex = new Map(fileNodes.map((n,i) => [n.id, i]));
  const links = (data.edges||[]).filter(e => nodeIndex.has(e.fromNode) && nodeIndex.has(e.toNode))
    .map(e => ({ source: nodeIndex.get(e.fromNode), target: nodeIndex.get(e.toNode) }));
  const sim = d3.forceSimulation(fileNodes)
    .force('link', d3.forceLink(links).distance(80).strength(0.4))
    .force('charge', d3.forceManyBody().strength(-180))
    .force('center', d3.forceCenter(W/2, H/2));
  const link = svg.append('g').selectAll('line').data(links).enter().append('line')
    .attr('stroke', '#475569').attr('stroke-opacity', 0.5);
  const node = svg.append('g').selectAll('g').data(fileNodes).enter().append('g')
    .call(d3.drag()
      .on('start', (e,d) => { if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on('drag',  (e,d) => { d.fx=e.x; d.fy=e.y; })
      .on('end',   (e,d) => { if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }));
  node.append('circle').attr('r', 6).attr('fill', '#a78bfa');
  node.append('text').text(d => (d.file||'').split('/').pop().replace(/\\.md$/,''))
    .attr('dx', 8).attr('dy', 4).attr('fill', '#cbd5e1').attr('font-size', 11);
  node.append('title').text(d => d.file);
  node.style('cursor', 'pointer').on('click', (e,d) => { window.location.href = '/note/' + d.file; });
  sim.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
  });
  d3.select('#meta').text(fileNodes.length + ' nodes · ' + links.length + ' edges · ' + groups.length + ' repos');
});
</script>
<p id="meta" style="color:var(--muted);margin-top:12px"></p>
<p style="color:var(--muted);font-size:13px">drag nodes · click to open</p>
"""


def page_canvas() -> str:
    return render_html("canvas", CANVAS_HTML)


# --------------------------------------------------------------------- app

def make_app(vault: pathlib.Path):
    (FastAPI, HTTPException, Query, HTMLResponse, JSONResponse,
     PlainTextResponse, MarkdownIt, _uvicorn) = _import_deps()

    md = MarkdownIt("commonmark", {"html": False, "linkify": True, "typographer": True})
    md.enable("table").enable("strikethrough")

    app = FastAPI(title="pwiki", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    def home(q: str = Query(default=""), rag: int = Query(default=0)):
        return page_home(vault, q, bool(rag))

    @app.get("/repo/{name}/", response_class=HTMLResponse)
    @app.get("/repo/{name}", response_class=HTMLResponse)
    def repo(name: str):
        return page_repo(vault, name)

    @app.get("/note/{rel_path:path}", response_class=HTMLResponse)
    def note(rel_path: str):
        return page_note(vault, rel_path, md)

    @app.get("/wikilink/{link}", response_class=HTMLResponse)
    def wikilink(link: str):
        target = resolve_wikilink(vault, link)
        if not target:
            return render_html("404", f"<h1>[[{link}]] unresolved</h1>"
                                      f"<p>No file with stem or alias {link!r}.</p>")
        return page_note(vault, target, md)

    @app.get("/daily/{date}", response_class=HTMLResponse)
    def daily(date: str):
        return page_daily(vault, date, md)

    @app.get("/canvas/", response_class=HTMLResponse)
    @app.get("/canvas", response_class=HTMLResponse)
    def canvas_page():
        return page_canvas()

    @app.get("/api/canvas.json", response_class=JSONResponse)
    def canvas_json():
        p = vault / "canvas" / "all-repos.canvas"
        if not p.is_file():
            return {"nodes": [], "edges": []}
        return json.loads(p.read_text(encoding="utf-8"))

    @app.get("/api/query", response_class=JSONResponse)
    def api_query(q: str, rag: int = 0, top: int = 10,
                  repo: str | None = None, tag: str | None = None):
        if not q:
            return {"hits": []}
        if rag:
            try:
                from pwiki import index_embed
                hits = index_embed.search(vault, q, top=top)
                return {"mode": "rag",
                        "hits": [{"score": s, **m} for s, m in hits]}
            except SystemExit as e:
                return {"error": str(e)}
        from pwiki import query as gq
        hits = gq.search(vault, q, repo_filter=repo, tag_filter=tag, top=top)
        return {"mode": "grep",
                "hits": [{"score": s, "path": str(p.relative_to(vault)),
                          "fm": fm, "context": ctx}
                         for s, p, fm, ctx in hits]}

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "vault": str(vault), "ts": dt.datetime.now().isoformat()}

    return app


def main() -> int:
    *_, uvicorn = _import_deps()
    ap = argparse.ArgumentParser(description="Local web UI for the pwiki Vault.")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--open", dest="open_browser", action="store_true",
                    help="open the URL in your browser after start")
    ap.add_argument("--reload", action="store_true",
                    help="auto-reload on code changes (dev mode)")
    args = ap.parse_args()

    vault = pathlib.Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        sys.exit(f"vault not found: {vault}")

    print(f"==> serving {vault}")
    print(f"==> http://{args.host}:{args.port}/")
    if args.open_browser:
        webbrowser.open(f"http://{args.host}:{args.port}/")

    if args.reload:
        # uvicorn reload requires an import string
        import os
        os.environ["PWIKI_VAULT"] = str(vault)
        uvicorn.run("pwiki.serve:_reload_app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run(make_app(vault), host=args.host, port=args.port, log_level="info")
    return 0


def _reload_app():  # used only with --reload
    import os
    return make_app(pathlib.Path(os.environ.get("PWIKI_VAULT", str(DEFAULT_VAULT))))


if __name__ == "__main__":
    raise SystemExit(main())
