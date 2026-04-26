#!/usr/bin/env bash
# scripts/release.sh — one-shot PyPI release
# Prereq:  ~/.pypirc with [pypi] username=__token__ password=pypi-AgE...
# Usage:   bash scripts/release.sh
set -euo pipefail

PROJ_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJ_ROOT"

if [ ! -f ~/.pypirc ]; then
  echo "ERROR: ~/.pypirc missing. See RELEASE.md Step 2." >&2
  exit 1
fi

echo "==> ensuring build / twine installed"
python3 -m pip install --upgrade pip build twine >/dev/null

echo "==> cleaning old dist/"
rm -rf dist build *.egg-info

echo "==> building wheel + sdist"
python3 -m build

echo "==> verifying package metadata"
python3 -m twine check dist/*

echo "==> dist/ contents:"
ls -lh dist/

echo "==> uploading to PyPI"
python3 -m twine upload dist/*

VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
echo
echo "✅ released pwiki v${VERSION}"
echo "   PyPI: https://pypi.org/project/pwiki/${VERSION}/"
echo
echo "verify with:"
echo "   pip install pwiki==${VERSION}"
echo "   pwiki --version"
