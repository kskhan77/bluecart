#!/usr/bin/env bash
# migrate.sh: move the running annotation tool from this laptop to the Azure VM, keeping accounts and answers.
#
# Run ON THE LAPTOP, from the repo root, after setup_vm.sh has run on the VM:
#     bash scripts/azure/migrate.sh azureuser@<vm public IP>          (add  -i ~/.ssh/<key>.pem  through SSH config if needed)
#
# Order matters:
#   1. the laptop copy is STOPPED first, so no answer is saved on the laptop after the copy
#   2. deploy/local_server is copied to the VM (photos, config, login page, accounts, answers, session key)
#   3. our login page is installed into the VM's Potato and the service is started
# Then run tunnel_vm.sh ON THE VM to point the public address at it. Until that step classmates see an error page
# (the laptop copy is stopped), so do the three steps in one sitting, ideally when nobody is labeling
# (admin page, Annotators tab, "Last Activity").
# To push later updates (new config, pages or photos): rebuild deploy/local_server on the laptop, then run this again.
set -euo pipefail
cd "$(dirname "$0")/../.."
VM="${1:?usage: bash scripts/azure/migrate.sh user@host}"
SERVER=deploy/local_server
[ -f "$SERVER/config.yaml" ] || { echo "No $SERVER/config.yaml; build it first (see start_public_tool.sh)"; exit 1; }

echo "== 1. stopping the laptop copy"
pkill -f "potato start config.yaml -p 8010" 2>/dev/null && sleep 2 || true

echo "== 2. copying $SERVER to $VM:/opt/bluecart/server  (accounts, answers, photos; $(du -sh "$SERVER" | cut -f1))"
rsync -az --delete --exclude potato.log --exclude 'project.sqlite*' --exclude layouts "$SERVER"/ "$VM":/opt/bluecart/server/
scp -q scripts/azure/tunnel_vm.sh "$VM":/opt/bluecart/tunnel_vm.sh

echo "== 3. installing our login page in the VM's Potato and (re)starting the service"
ssh "$VM" 'bash -s' <<'EOF'
set -e
/opt/bluecart/venv/bin/python - <<'PY'
import potato, pathlib, shutil
target = pathlib.Path(potato.__file__).parent / "templates" / "home.html"
backup = target.with_suffix(".html.orig")
if not backup.exists():
    shutil.copy(target, backup)
shutil.copy("/opt/bluecart/server/login_page.html", target)
print("login page installed")
PY
chmod 600 /opt/bluecart/server/.secret_key
sudo systemctl restart bluecart
sleep 5
echo "tool on the VM answers: $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8010/)"
echo "accounts on the VM: $(grep -c username /opt/bluecart/server/user_config.json 2>/dev/null || echo 0)"
EOF

echo
echo "== 4. now point the address at the VM. On the VM run:"
echo "       bash /opt/bluecart/tunnel_vm.sh"
echo "   (first time only, before that:  cloudflared tunnel login)"
