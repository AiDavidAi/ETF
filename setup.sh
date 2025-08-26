#!/usr/bin/env bash
# Setup script for the ETF repository

set -euo pipefail

# Locate repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creating virtual environment..."
python3 -m venv "$REPO_ROOT/.venv"
source "$REPO_ROOT/.venv/bin/activate"

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
python -m pip install -r "$REPO_ROOT/requirements.txt"

# Make project modules importable without packaging
export PYTHONPATH="$REPO_ROOT/src:${PYTHONPATH:-}"

echo "Running test suite..."
pytest -q

echo "Setup complete."
