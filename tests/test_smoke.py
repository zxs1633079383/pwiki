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
    for sub in ("sync", "aliases", "canvas", "brief", "evolution"):
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


def test_imports() -> None:
    """Every module imports cleanly without side effects."""
    import pwiki  # noqa: F401
    from pwiki import sync, aliases, canvas, brief, evolution  # noqa: F401

    assert pwiki.__version__
