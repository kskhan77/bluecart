#!/usr/bin/env bash
# Start (or restart) the public copy of the annotation tool that classmates reach at
#   https://bluecart.khurramshafique.com
#
# How it works:
#   * Potato runs on this computer on port 8010, from deploy/local_server/ (passwords on,
#     30 shared photos first, answers saved in deploy/local_server/annotation_output/).
#   * The Cloudflare tunnel in ~/.cloudflared/config.yml forwards the hostname to port 8010.
#     The tunnel is the same one that serves starboard.khurramshafique.com.
#
# Usage, from the repo root:   bash scripts/start_public_tool.sh
# To rebuild the folder first (our live settings, see README section 6):
#   python scripts/make_hf_space.py --out deploy/local_server --no-backup --shared 30 --per-annotator 200 --annotators 10 --labels-per-photo 2
#   (a rebuild keeps accounts and answers but replaces the photo list and config:
#    run it only when nobody is labeling, and copy deploy/local_server/annotation_output
#    somewhere safe first)
set -euo pipefail
cd "$(dirname "$0")/.."
SERVER=deploy/local_server
PORT=8010

[ -f "$SERVER/config.yaml" ] || { echo "No $SERVER/config.yaml. Build it first:"; echo "  python scripts/make_hf_space.py --out $SERVER --no-backup"; exit 1; }
[ -f "$SERVER/.secret_key" ] || python3 -c "import secrets; print(secrets.token_urlsafe(32))" > "$SERVER/.secret_key"

# our login / register page (Potato has no setting for it; pip reinstalls would bring the stock page back)
.venv/bin/python scripts/patch_login_page.py
chmod 600 "$SERVER/.secret_key"

# stop an older copy of this server, if any
pkill -f "potato start config.yaml -p $PORT" 2>/dev/null && sleep 1 || true

cd "$SERVER"
POTATO_SECRET_KEY="$(cat .secret_key)" POTATO_PROXY_FIX_X_PROTO=1 POTATO_PROXY_FIX_X_FOR=1 POTATO_PROXY_FIX_X_HOST=1 \
  nohup setsid ../../.venv/bin/potato start config.yaml -p "$PORT" --host 127.0.0.1 > potato.log 2>&1 &
for i in $(seq 1 30); do
  if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$PORT/" | grep -q 200; then echo "Tool is running on port $PORT"; break; fi
  sleep 1
done
cd - > /dev/null

# the tunnel: start it only if it is not already running
if pgrep -f "cloudflared --no-autoupdate tunnel --config" > /dev/null; then
  echo "Cloudflare tunnel already running"
else
  nohup setsid /usr/local/bin/cloudflared --no-autoupdate tunnel --config "$HOME/.cloudflared/config.yml" run > "$HOME/.cloudflared/cloudflared.log" 2>&1 &
  sleep 5; echo "Cloudflare tunnel started"
fi
echo "Open: https://bluecart.khurramshafique.com"
echo "Answers: $SERVER/annotation_output/   Admin key: $SERVER/admin_api_key.txt (made on first visit to /admin)"
