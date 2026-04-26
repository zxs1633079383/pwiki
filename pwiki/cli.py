"""pwiki CLI dispatcher — thin shim over the five module mains."""
from __future__ import annotations

import argparse
import sys
from importlib import import_module

from . import __version__

SUBCOMMANDS = {
    "sync": ("pwiki.sync", "ingest a generated wiki/ dir into your Obsidian Vault"),
    "aliases": ("pwiki.aliases", "add YAML aliases from index.md so wikilinks resolve"),
    "canvas": ("pwiki.canvas", "render the Vault as a multi-repo JSON Canvas"),
    "brief": ("pwiki.brief", "build today's morning-brief skeleton"),
    "evolution": ("pwiki.evolution", "roll up the past week's self-evolution entries"),
    "query": ("pwiki.query", "search Vault notes by query string"),
}


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pwiki",
        description=(
            "pwiki - Karpathy's LLM Wiki, brew-install ready.\n"
            "Run `pwiki <subcommand> --help` for per-command flags."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--version", action="version", version=f"pwiki {__version__}")
    sub = p.add_subparsers(dest="cmd", metavar="<subcommand>")
    for name, (_, help_text) in SUBCOMMANDS.items():
        sub.add_parser(name, help=help_text, add_help=False)
    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        _build_parser().print_help()
        return 0
    if argv[0] in {"-V", "--version"}:
        print(f"pwiki {__version__}")
        return 0
    cmd = argv[0]
    if cmd not in SUBCOMMANDS:
        _build_parser().print_help()
        print(f"\nerror: unknown subcommand '{cmd}'", file=sys.stderr)
        return 2
    module_name, _ = SUBCOMMANDS[cmd]
    module = import_module(module_name)
    sys.argv = [f"pwiki {cmd}"] + argv[1:]
    rc = module.main()
    return int(rc or 0)


if __name__ == "__main__":
    raise SystemExit(main())
