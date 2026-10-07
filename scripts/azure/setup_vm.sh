#!/usr/bin/env bash
# setup_vm.sh: prepare a fresh Ubuntu 24.04 Azure virtual machine to run the Blue Cart Check annotation tool.
#
# Run ON THE VM, as the admin user you chose in the Azure portal:
#     bash setup_vm.sh
#
# What it does:
#   * installs Python, a virtual environment and the same Potato version we use (2.9.4)
#   * installs cloudflared, the Cloudflare tunnel program (the public address keeps working without opening ports)
#   * creates a systemd service "bluecart" that starts the tool on port 8010 at every boot and restarts it if it crashes
# The server folder itself (photos, config, accounts, answers) is copied later by scripts/azure/migrate.sh from the laptop.
set -euo pipefail

echo "== packages"
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip rsync curl

echo "== Potato 2.9.4 in /opt/bluecart/venv"
sudo mkdir -p /opt/bluecart
sudo chown "$USER":"$USER" /opt/bluecart
[ -d /opt/bluecart/venv ] || python3 -m venv /opt/bluecart/venv
/opt/bluecart/venv/bin/pip install --quiet --upgrade pip
/opt/bluecart/venv/bin/pip install --quiet "potato-annotation==2.9.4"
mkdir -p /opt/bluecart/server

echo "== cloudflared"
if ! command -v cloudflared >/dev/null 2>&1; then
  curl -fsSL -o /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
  sudo dpkg -i /tmp/cloudflared.deb
fi
cloudflared --version

echo "== systemd service for the tool"
sudo tee /etc/systemd/system/bluecart.service >/dev/null <<EOF
[Unit]
Description=Blue Cart Check annotation tool (Potato)
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=/opt/bluecart/server
# the session key lives in .secret_key inside the server folder (copied from the laptop), so logins survive restarts
ExecStart=/bin/bash -c 'POTATO_SECRET_KEY=\$(cat /opt/bluecart/server/.secret_key) POTATO_PROXY_FIX_X_PROTO=1 POTATO_PROXY_FIX_X_FOR=1 POTATO_PROXY_FIX_X_HOST=1 exec /opt/bluecart/venv/bin/potato start config.yaml -p 8010 --host 127.0.0.1'
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable bluecart >/dev/null

echo
echo "VM is ready. Next steps (see docs/AZURE_HOSTING.md):"
echo "  1. on this VM:      cloudflared tunnel login      (open the printed link on your PC, choose khurramshafique.com)"
echo "  2. on the laptop:   bash scripts/azure/migrate.sh $USER@<this VM's public IP>"
echo "  3. on this VM:      bash /opt/bluecart/tunnel_vm.sh"
