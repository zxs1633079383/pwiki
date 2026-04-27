"""Smoke tests — every subcommand wired up correctly and minimally functional.

These do NOT exercise the full Vault flow (that requires a fixture Vault).
They verify imports, CLI dispatch, and `--help` output for each subcommand.
"""
from __future__ import annotations

import subprocess
import sys


def _run_pwiki(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pwiki.cli", *args],
        capture_output=True,
        text=True,
    )


def test_version() -> None:
    r = _run_pwiki("--version")
    assert r.returncode == 0
    assert r.stdout.startswith("pwiki ")


def test_help_lists_all_subcommands() -> None:
    r = _run_pwiki("--help")
    assert r.returncode == 0
    for sub in ("init", "sync", "aliases", "canvas", "brief", "evolution", "query", "serve"):
        assert sub in r.stdout, f"{sub} missing from --help output"


def test_unknown_subcommand_errors() -> None:
    r = _run_pwiki("nope")
    assert r.returncode != 0
    assert "unknown subcommand" in r.stderr.lower()


def test_sync_help() -> None:
    r = _run_pwiki("sync", "--help")
    assert r.returncode == 0
    assert "source" in r.stdout
    assert "repo" in r.stdout


def test_canvas_help() -> None:
    r = _run_pwiki("canvas", "--help")
    assert r.returncode == 0
    assert "vault" in r.stdout.lower() or "canvas" in r.stdout.lower()


def test_brief_help() -> None:
    r = _run_pwiki("brief", "--help")
    assert r.returncode == 0


def test_evolution_help() -> None:
    r = _run_pwiki("evolution", "--help")
    assert r.returncode == 0


def test_aliases_help() -> None:
    r = _run_pwiki("aliases", "--help")
    assert r.returncode == 0
    assert "repo" in r.stdout.lower()


def test_query_help() -> None:
    r = _run_pwiki("query", "--help")
    assert r.returncode == 0
    assert "query" in r.stdout.lower()


def test_init_help() -> None:
    r = _run_pwiki("init", "--help")
    assert r.returncode == 0
    assert "init" in r.stdout.lower() or "setup" in r.stdout.lower()


def test_imports() -> None:
    """Every module imports cleanly without side effects."""
    import pwiki  # noqa: F401
    from pwiki import init, sync, aliases, canvas, brief, evolution, query  # noqa: F401

    assert pwiki.__version__


def test_brief_help_advertises_force_flag() -> None:
    """Regression: 0.3.4 added --force to override the filled-detection refuse."""
    r = _run_pwiki("brief", "--help")
    assert r.returncode == 0
    assert "--force" in r.stdout


def test_looks_like_scaffold_detects_placeholders() -> None:
    """A fresh scaffold has at least one of the SCAFFOLD_MARKERS sentinels."""
    from pwiki.brief import looks_like_scaffold

    fresh = "## §②\n1. ...\n2. ...\n3. ...\n## §④\n_待 LLM 填..._\n"
    assert looks_like_scaffold(fresh)

    filled = "## §②\n1. **PR Review Bot 商业化**\n2. **pwiki Hosted**\n## §④\nInversion 优先...\n"
    assert not looks_like_scaffold(filled)


def test_rotate_backup_creates_timestamped_copy(tmp_path) -> None:
    """rotate_backup must NOT clobber an existing .bak (the 0.3.3 regression)."""
    from pwiki.brief import rotate_backup

    daily = tmp_path / "2026-04-27.md"
    daily.write_text("filled content", encoding="utf-8")
    bak = rotate_backup(daily)
    assert bak.exists()
    assert bak.read_text(encoding="utf-8") == "filled content"
    assert ".bak." in bak.name  # timestamped, not bare .bak

    # A second call within the same second must still produce a unique file.
    bak2 = rotate_backup(daily)
    assert bak2.exists()
    assert bak2 != bak
