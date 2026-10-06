"""
patch_login_page.py: give the annotation tool our own login / register page.

Potato has no setting for the look of its login page (templates/home.html inside the
installed package): custom_footer_html and base_css only reach the annotation pages.
So this script copies annotation/potato/login_page.html over that file in the Python
environment this repo runs, keeping Potato's original next to it as home.html.orig.

Our page keeps every field, id and form action Potato's server expects, so the server
code is untouched. It only changes the words and the look.

Run it after every install or upgrade of potato-annotation (pip overwrites the file).
scripts/start_public_tool.sh runs it automatically before starting the public tool.

Usage (from the repo root, with the venv's python):
    python scripts/patch_login_page.py            # install our page (idempotent)
    python scripts/patch_login_page.py --check    # exit 0 if our page is installed, 1 if not
    python scripts/patch_login_page.py --restore  # put Potato's original page back

Annotators who run a zip pack on their own computer get Potato's stock page, which has
the same fields; only the hosted copy at bluecart.khurramshafique.com shows this one.
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OURS = REPO / "annotation" / "potato" / "login_page.html"


def installed_home_html():
    import potato  # the package this interpreter runs; fails loudly if potato is not installed
    return Path(potato.__file__).resolve().parent / "templates" / "home.html"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only report whether our page is installed")
    ap.add_argument("--restore", action="store_true", help="restore Potato's original home.html")
    args = ap.parse_args()

    target = installed_home_html()
    backup = target.with_suffix(".html.orig")
    if not target.exists():
        raise SystemExit(f"Potato's login template was not found at {target}")

    if args.check:
        same = filecmp.cmp(OURS, target, shallow=False)
        print(("our login page is installed" if same else "Potato's stock login page is installed") + f": {target}")
        return 0 if same else 1

    if args.restore:
        if not backup.exists():
            raise SystemExit(f"No backup at {backup}; nothing to restore.")
        shutil.copy(backup, target)
        print(f"restored Potato's original login page: {target}")
        return 0

    if not OURS.exists():
        raise SystemExit(f"{OURS} is missing")
    for must in ('action="{{ url_prefix }}/auth"', 'action="{{ url_prefix }}/register"', 'id="login-email"', 'id="login-pass"',
                 'id="register-email"', 'id="register-pass"', 'name="email"', 'name="pass"', 'value="signup"', 'value="login"'):
        if must not in OURS.read_text(encoding="utf-8"):
            raise SystemExit(f"login_page.html lost something Potato's server needs: {must}")
    if not backup.exists() and not filecmp.cmp(OURS, target, shallow=False):
        shutil.copy(target, backup)                       # keep Potato's original once
        print(f"kept Potato's original as {backup.name}")
    if filecmp.cmp(OURS, target, shallow=False):
        print(f"our login page is already installed: {target}")
    else:
        shutil.copy(OURS, target)
        print(f"installed our login page: {target}")
    print("restart the tool to see it (Flask caches templates).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
