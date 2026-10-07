#!/usr/bin/env bash
# tunnel_vm.sh: give the Azure VM its own Cloudflare tunnel and point bluecart.khurramshafique.com at it.
#
# Run ON THE VM after `cloudflared tunnel login` (one-time browser step):
#     bash /opt/bluecart/tunnel_vm.sh
#
# From then on https://bluecart.khurramshafique.com reaches the VM, not the laptop. The laptop's tunnel keeps
# serving its other sites; its bluecart rule simply stops receiving traffic.
# Rollback (from the laptop): cloudflared tunnel route dns --overwrite-dns <laptop tunnel name or id> bluecart.khurramshafique.com
set -euo pipefail
NAME=bluecart-azure
HOST=bluecart.khurramshafique.com

if [ ! -f "$HOME/.cloudflared/cert.pem" ]; then
  echo "Not logged in to Cloudflare yet. Run:   cloudflared tunnel login"
  echo "then open the printed link on your PC, sign in, choose khurramshafique.com, and run this script again."
  exit 1
fi

if ! cloudflared tunnel list -o json | python3 -c "import json,sys; sys.exit(0 if any(t['name']=='$NAME' for t in json.load(sys.stdin)) else 1)"; then
  cloudflared tunnel create "$NAME"
fi
ID=$(cloudflared tunnel list -o json | python3 -c "import json,sys; print([t['id'] for t in json.load(sys.stdin) if t['name']=='$NAME'][0])")
echo "tunnel $NAME = $ID"

mkdir -p "$HOME/.cloudflared"
cat > "$HOME/.cloudflared/config.yml" <<EOF
tunnel: $ID
credentials-file: $HOME/.cloudflared/$ID.json
ingress:
  - hostname: $HOST
    service: http://localhost:8010
  - service: http_status:404
EOF

echo "== DNS: $HOST -> this tunnel (replaces the laptop's record)"
cloudflared tunnel route dns --overwrite-dns "$NAME" "$HOST"

echo "== run the tunnel as a service"
if ! systemctl list-unit-files | grep -q '^cloudflared.service'; then
  sudo cloudflared --config "$HOME/.cloudflared/config.yml" service install
fi
sudo systemctl enable cloudflared >/dev/null
sudo systemctl restart cloudflared
sleep 6
echo "https://$HOST answers: $(curl -s -o /dev/null -w '%{http_code}' "https://$HOST/")"
echo "tool on this VM answers:  $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8010/)"
