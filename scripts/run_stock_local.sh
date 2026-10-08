#!/usr/bin/env bash
# Run the annotation tool on this computer with Potato's own look.
#
#   bash scripts/run_stock_local.sh            # http://localhost:8000
#   bash scripts/run_stock_local.sh 8001       # another port
#
# What it does:
#   1. makes sure the venv's Potato uses its own login page (restores templates/home.html from home.html.orig if present),
#   2. builds deploy/stock_local/ from annotation/potato/config.yaml (the plain config on this branch),
#   3. starts Potato there. Answers stay in deploy/stock_local/annotation_output/ (gitignored).
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${1:-8000}"
source .venv/bin/activate

TPL="$(python -c 'import potato, pathlib; print(pathlib.Path(potato.__file__).parent / "templates")')"
if [ -f "$TPL/home.html.orig" ]; then
  cp "$TPL/home.html.orig" "$TPL/home.html"
  echo "Potato's original login page restored in the venv"
fi

python scripts/make_hf_space.py --out deploy/stock_local --no-backup --shared 30 --per-annotator 200 --annotators 10 --labels-per-photo 2 --fresh
cd deploy/stock_local
echo "Stock Potato on http://localhost:$PORT  (Ctrl+C stops it)"
exec potato start config.yaml -p "$PORT"
