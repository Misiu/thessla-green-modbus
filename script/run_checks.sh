#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python}"
"$PYTHON_BIN" -m ruff format --check .
"$PYTHON_BIN" -m ruff check .
"$PYTHON_BIN" -m mypy
"$PYTHON_BIN" -m compileall -q src tests script
"$PYTHON_BIN" -m pytest --cov --cov-report=term-missing
"$PYTHON_BIN" -m build
"$PYTHON_BIN" -m twine check --strict dist/*
