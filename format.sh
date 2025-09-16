#!/usr/bin/env bash
set -euo pipefail

echo "Running ruff lint..."
ruff check .
echo "Running ruff format..."
ruff format .
echo "Done."
