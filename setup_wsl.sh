#!/usr/bin/env bash
# One-shot setup for Blue Cart Check on WSL Ubuntu.
# Usage: cd ~/workspace-school/blue-cart-check && bash setup_wsl.sh [--ml]
#   --ml  also installs torch/torchvision (CPU) for ResNet features + later baselines (~1 GB)
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Checking system packages"
missing=()
for pkg in python3 git make unzip; do command -v "$pkg" >/dev/null || missing+=("$pkg"); done
python3 -c "import venv" 2>/dev/null || missing+=("python3-venv")
if [ ${#missing[@]} -gt 0 ]; then
  echo "Installing: ${missing[*]} (sudo)"
  sudo apt update && sudo apt install -y "${missing[@]}" python3-venv python3-pip libgl1
fi

echo "==> Python virtual environment (.venv)"
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip wheel >/dev/null
pip install -r requirements.txt
if [[ "${1:-}" == "--ml" ]]; then
  pip install -r requirements-ml.txt --extra-index-url https://download.pytorch.org/whl/cpu
fi

echo "==> Folders"
mkdir -p data/images data/raw annotation/packs annotation/returned docs/figures results models

echo "==> Tests"
pytest -q

echo "==> Git"
if [ ! -d .git ]; then
  git init -q
  git add -A
  git commit -qm "chore: initial Blue Cart Check scaffold" || true
  echo "Git repo initialised (add a GitHub remote: see docs/SETUP_WSL.md step 5)"
fi

cat <<'EOF'

Setup complete.
Next:
  source .venv/bin/activate
  claude                      # start Claude Code here (install: curl -fsSL https://claude.ai/install.sh | bash)
  then type:  /phase1-check
EOF
