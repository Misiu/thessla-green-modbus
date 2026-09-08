#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-python}"
"$PYTHON_BIN" -m ruff check --fix .
"$PYTHON_BIN" -m ruff format .
