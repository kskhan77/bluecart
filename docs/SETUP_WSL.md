# Setup: WSL Ubuntu + Claude Code (Khurram's machine)

Target folder: `\\wsl.localhost\Ubuntu\home\kshafique\workspace-school\blue-cart-check`
(inside Ubuntu that's `~/workspace-school/blue-cart-check`)

> Work **inside** the Linux filesystem (`~/...`), not under `/mnt/c/...`. It's much faster for Python and git, and file watching works.

---

## 0. One-time Windows check (PowerShell)
```powershell
wsl --list --verbose        # Ubuntu should show VERSION 2
wsl --update
```
If it shows VERSION 1: `wsl --set-version Ubuntu 2`.

## 1. Ubuntu packages (Ubuntu terminal)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl unzip make build-essential python3 python3-venv python3-pip python3-dev libgl1
python3 --version    # 3.10+ works, 3.11+ preferred
```

## 2. Get the project into WSL
The project zip was saved to your Windows folder `C:\Fall-2026\project\`.
```bash
mkdir -p ~/workspace-school
cd ~/workspace-school
unzip /mnt/c/Fall-2026/project/blue-cart-check-claude.zip
cd blue-cart-check
bash setup_wsl.sh          # creates .venv, installs deps, runs tests, git init
```

## 3. Install Claude Code (inside Ubuntu, not PowerShell)
Official native installer (Linux/WSL):
```bash
curl -fsSL https://claude.ai/install.sh | bash
# open a NEW Ubuntu terminal, then:
claude --version
claude doctor            # optional health check
```
- Needs a Pro, Max, Team, Enterprise or Console account (the free plan doesn't include Claude Code).
- First run of `claude` opens a browser to log in. In WSL it prints a URL if the browser doesn't open, so copy it into Windows Chrome.
- If `claude: command not found`: add `export PATH="$HOME/.local/bin:$PATH"` to `~/.bashrc`, then `source ~/.bashrc`.
- Alternative: `npm install -g @anthropic-ai/claude-code` (needs Node 22+; never use `sudo npm`).
- Docs: https://code.claude.com/docs/en/setup

## 4. Start working
```bash
cd ~/workspace-school/blue-cart-check
source .venv/bin/activate
claude
```
Claude Code automatically reads `CLAUDE.md` (project memory) and `.claude/settings.json` (permissions).
Project skills you can call by name:
| type in Claude Code | what it does |
|---|---|
| `/phase1-check` | audits the repo against the Phase 1 requirements, gives a ✅/⚠️/❌ table |
| `/add-photos` | ingests a teammate's raw photos safely + checks |
| `/presentation-stats` | numbers + figures for the Oct 6 slides |
| `/explain-lecture` | plain-language lecture explainer tied to the project |

Good first prompts:
1. `Read CLAUDE.md and docs/REQUIREMENTS_PHASE1.md, then run /phase1-check`
2. `I copied my photos to data/raw/khurram_bin. Use /add-photos (photographer Khurram Shafique, disposables, bin_station)`
3. `Fill README sections 2, 5 and 6 from the current stats; ask me for the pilot timing`

## 5. GitHub (one repo for the team)
```bash
git config --global user.name  "Khurram Shafique"
git config --global user.email "kshafiqu@umich.edu"
# create an EMPTY repo on github.com (e.g. blue-cart-check), then:
git remote add origin https://github.com/<you>/blue-cart-check.git
git branch -M main
git push -u origin main
```
Optional GitHub CLI: `sudo apt install gh && gh auth login`. Then Claude Code can open PRs/issues for you.
Add Daud, Hina and Ian as collaborators (repo → Settings → Collaborators).

## 6. VS Code (optional but recommended)
Install VS Code on Windows + the **WSL** extension, then from Ubuntu: `code .`
Install the **Claude Code** extension in the WSL window if you prefer the IDE panel.

## 7. Copying photos from Windows / phone into WSL
Phone → Google Drive / USB → Windows folder → into WSL:
```bash
mkdir -p data/raw/khurram_bin
cp /mnt/c/Users/<WindowsUser>/Downloads/bin_photos/* data/raw/khurram_bin/
```
Then `/add-photos` in Claude Code (or run `prepare_images.py` yourself).

## 8. Running the annotation tool from WSL
```bash
cd annotation/packs/internal_01 && potato start config.yaml -p 8000
```
Open http://localhost:8000 in Windows Chrome (WSL2 forwards localhost automatically).

## Troubleshooting
| problem | fix |
|---|---|
| `python3 -m venv` fails | `sudo apt install python3-venv` |
| `ImportError: libGL.so.1` | `sudo apt install libgl1` |
| HEIC photos from iPhone | `pip install pillow-heif` (in requirements) or set iPhone Camera → Formats → Most Compatible |
| very slow git/pip | you're under `/mnt/c`; move the project to `~/workspace-school` |
| localhost:8000 not opening | `potato start config.yaml -p 8000 --host 0.0.0.0`, then use the WSL IP from `hostname -I` |
