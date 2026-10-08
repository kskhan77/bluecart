"""
make_hf_space.py: build the folder that goes on Hugging Face (one hosted tool for everyone).

With packs, every annotator runs the tool on their own computer. With a Hugging Face
"Space", the tool runs once on the internet and annotators only open a link.
This script builds the Space folder from the current dataset:

  deploy/hf_space/
      README.md           settings Hugging Face reads (Docker Space, port 7860)
      Dockerfile          starts Potato from its published image
      config.yaml         the same tool config as the packs, plus the hosted settings below
      welcome.html        the welcome page
      data/items.jsonl    every photo, the shared ones FIRST
      media/              the photos, the guidelines page, the how-it-works page and the demo page (with video)

What is different from a pack (all of it is in the generated config.yaml):
  * accounts with passwords: each annotator registers once on the login page;
  * one photo list for everybody. The first --shared photos go to every annotator
    (the agreement set). After those, each annotator gets the next photos that still
    need a label, up to --per-annotator in total. Every other photo is labeled by
    --labels-per-photo people (1 = pure coverage, 2 = every photo can be checked,
    3 = majority vote everywhere). Potato hands photos out from the top of the
    list, so the shared ones are simply placed first;
  * answers are copied to a private Hugging Face Dataset every few minutes,
    because a Space loses its files every time it restarts.

Usage (from the repo root):
    python scripts/make_hf_space.py --backup-repo <your-hf-name>/blue-cart-check-annotations
    python scripts/make_hf_space.py --shared 30 --per-annotator 200 --annotators 10 --labels-per-photo 2 \
        --backup-repo <your-hf-name>/blue-cart-check-annotations

Then follow docs/HUGGINGFACE_HOSTING.md to push the folder with git.
Nothing is uploaded by this script.

The same folder also works for hosting from this computer through a Cloudflare tunnel
(answers then stay on this disk, so no Hugging Face backup is needed):
    python scripts/make_hf_space.py --out deploy/local_server --no-backup
"""

import argparse
import csv
import importlib.util
import json
import random
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POTATO = REPO / "annotation" / "potato"
DEFAULT_OUT = REPO / "deploy" / "hf_space"

README = """---
title: Blue Cart Check
emoji: ♻️
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Blue Cart Check: annotation tool

ARI 510 Machine Learning, University of Michigan-Flint, Fall 2026, Group 2.
Annotators answer two short questions about photos of everyday items under the
City of Flint recycling rules.

This Space runs [Potato](https://www.potatoannotator.com), an open-source annotation tool.
Answers are copied to a private Dataset repository every few minutes, because a
Space does not keep its files across restarts.
"""

DOCKERFILE = """# Hugging Face Space for the Blue Cart Check annotation tool.
# Starts from Potato's published image and adds only this folder.
FROM ghcr.io/davidjurgens/potato:{version}

USER potato
WORKDIR /app
COPY --chown=potato:potato . /app

# Hugging Face sends visitors to port 7860.
ENV POTATO_CONFIG=config.yaml \\
    PORT=7860 \\
    GUNICORN_WORKERS=1 \\
    GUNICORN_THREADS=8 \\
    POTATO_NONINTERACTIVE=1

EXPOSE 7860
"""

LOCAL_TAIL = """require_password: false

user_config:
  allow_all_users: true
  users: []
"""

HOSTED_TAIL = """# ================= hosted version (made by scripts/make_hf_space.py) =================
# Accounts: each annotator registers once with a password on the login page.
require_password: true
authentication:
  user_config_path: user_config.json      # keeps the accounts while the Space is running
user_config:
  allow_all_users: true
  users: []

# Who gets which photos.
# Every photo is labeled by {labels} annotator(s), except the {shared} shared photos, which go to
# {annotators} annotators. Those {shared} are the FIRST lines of data/items.jsonl, and Potato
# hands photos out from the top, so every annotator gets all of them and then
# the next photos that still need a label, {per} in total.
num_annotators_per_item:
  default: {labels}
  overlap_sample:
    fraction: {fraction}
    count: {annotators}
    seed: {seed}
max_annotations_per_user: {per}
random_seed: {seed}

# A Space loses its files on every restart. Answers are copied to this private
# Dataset every {minutes} minutes. The token comes from the Space secret HF_TOKEN.
huggingface_backup:
  enabled: true
  repo_id: {backup_repo}
  repo_type: dataset
  private: true
  schedule_minutes: {minutes}
"""


def shared_ids(all_ids, n_shared, seed):
    """The photos Potato will give to every annotator.

    This repeats what Potato's own overlap sampler does (sort the ids, shuffle with
    the seed, take the first ones), so we know the shared photos before the tool runs.
    Returns (ids, fraction to write into the config).
    """
    fraction = n_shared / len(all_ids)
    ordered = sorted(all_ids)
    random.Random(seed).shuffle(ordered)
    target = max(1, int(round(len(ordered) * fraction)))
    return ordered[:target], fraction


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shared", type=int, default=30, help="photos that every annotator labels")
    ap.add_argument("--per-annotator", type=int, default=120, help="photos per annotator in total (shared + own)")
    ap.add_argument("--annotators", type=int, default=6, help="how many people will label (external + internal)")
    ap.add_argument("--labels-per-photo", type=int, default=1,
                    help="how many people label each non-shared photo (1 coverage only, 2 checkable, 3 majority vote)")
    ap.add_argument("--backup-repo", default="YOUR-HF-NAME/blue-cart-check-annotations",
                    help="private Hugging Face Dataset that receives the answers, as owner/name")
    ap.add_argument("--backup-minutes", type=int, default=5)
    ap.add_argument("--potato-version", default="latest", help="tag of Potato's published image")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="where to build the folder (default deploy/hf_space)")
    ap.add_argument("--no-backup", action="store_true",
                    help="leave out the Hugging Face backup, for a server that runs on this computer")
    ap.add_argument("--keep-photo-list", action="store_true",
                    help="rebuild a RUNNING server with exactly the photos it already serves (same list, same shared set); "
                         "photos added to the manifest since are left out until the next round")
    ap.add_argument("--fresh", action="store_true",
                    help="allow the shared set to change even though the folder already has one (starts a new round)")
    args = ap.parse_args()
    OUT = Path(args.out)

    with (REPO / "data" / "manifest.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ids = [r["id"] for r in rows]
    path_of = {r["id"]: r["image_path"] for r in rows}
    previous_list = OUT / "data" / "items.jsonl"
    previous_shared = OUT / "shared_ids.json"
    if args.keep_photo_list:
        if not (previous_list.exists() and previous_shared.exists()):
            raise SystemExit(f"--keep-photo-list needs an existing {previous_list} and {previous_shared}.")
        served = [json.loads(l)["id"] for l in previous_list.open(encoding="utf-8")]
        missing = [i for i in served if i not in path_of]
        if missing:
            raise SystemExit(f"{len(missing)} photos the server serves are no longer in the manifest (e.g. {missing[:3]}); cannot keep the list.")
        left_out = len(ids) - len(served)
        ids = served
        print(f"keeping the photo list the server already serves: {len(ids)} photos"
              + (f" ({left_out} newer manifest photos left out until the next round)" if left_out else ""))
    shared, fraction = shared_ids(ids, args.shared, args.seed)
    if previous_shared.exists() and not args.fresh:
        old = json.load(previous_shared.open(encoding="utf-8")).get("shared_ids", [])
        if old and set(old) != set(shared):
            raise SystemExit("REFUSED: this rebuild would change the shared photos that everyone labels "
                             f"({len(set(old) - set(shared))} of the current {len(old)} would drop out), because the photo list changed. "
                             "Potato samples the shared set from the whole list, so people who already labeled the old shared photos "
                             "would no longer share them with new annotators.\n"
                             "  * to update a running server without changing its photos:  add --keep-photo-list\n"
                             "  * to start a new round with the new photos and a new shared set: add --fresh")
    if args.per_annotator <= len(shared):
        raise SystemExit(f"--per-annotator ({args.per_annotator}) must be larger than the shared set ({len(shared)}).")
    if args.labels_per_photo < 1:
        raise SystemExit("--labels-per-photo must be at least 1.")
    # capacity: how many non-shared photos get all their labels when every annotator finishes
    rest_n = len(ids) - len(shared)
    own_labels = args.annotators * (args.per_annotator - len(shared))
    covered = min(rest_n, own_labels // args.labels_per_photo)

    if OUT.exists():
        # git history, session key, ACCOUNTS, admin key and ANSWERS survive a rebuild
        keep = {".git", ".secret_key", "user_config.json", "admin_api_key.txt", "annotation_output"}
        for child in OUT.iterdir():
            if child.name not in keep:
                shutil.rmtree(child) if child.is_dir() else child.unlink()
        if (OUT / "annotation_output").exists():
            print("note: kept the existing accounts (user_config.json) and answers (annotation_output/). "
                  "Accounts made before this rebuild keep their old photo lists.")
    (OUT / "data").mkdir(parents=True, exist_ok=True)
    (OUT / "media").mkdir(exist_ok=True)

    # shared photos first, then the rest in a fixed shuffled order (so one source does not come all at once);
    # with --keep-photo-list the previous order is kept exactly, so running annotators' positions do not move
    if args.keep_photo_list:
        order = ids
    else:
        rest = [i for i in ids if i not in set(shared)]
        random.Random(args.seed + 1).shuffle(rest)
        order = shared + rest
    with (OUT / "data" / "items.jsonl").open("w", encoding="utf-8") as f:
        for image_id in order:
            f.write(json.dumps({"id": image_id, "image": f"/media/{image_id}.jpg"}) + "\n")
            shutil.copy(REPO / "data" / path_of[image_id], OUT / "media" / f"{image_id}.jpg")

    # guidelines page for the "Guidelines" button (same function the packs use)
    spec = importlib.util.spec_from_file_location("packs", REPO / "scripts" / "make_annotation_packs.py")
    packs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(packs)
    guidelines = (REPO / "annotation" / "guidelines.md").read_text(encoding="utf-8")
    (OUT / "media" / "guidelines.html").write_text(packs.guidelines_html(guidelines), encoding="utf-8")
    packs.add_help_pages(OUT / "media", with_video=True)        # pages behind the round help button

    config = (POTATO / "config.yaml").read_text(encoding="utf-8")
    if LOCAL_TAIL not in config:
        raise SystemExit("annotation/potato/config.yaml no longer ends with the expected login block; update LOCAL_TAIL.")
    hosted = HOSTED_TAIL.format(shared=len(shared), annotators=args.annotators, per=args.per_annotator, fraction=repr(fraction),
                                labels=args.labels_per_photo, seed=args.seed, backup_repo=args.backup_repo, minutes=args.backup_minutes)
    if args.no_backup:                              # answers stay on this computer's disk
        hosted = hosted[:hosted.index("# A Space loses its files")] + "# No Hugging Face backup: this server runs on our own computer.\n"
    (OUT / "config.yaml").write_text(config.replace(LOCAL_TAIL, hosted), encoding="utf-8")
    shutil.copy(POTATO / "welcome.html", OUT / "welcome.html")
    (OUT / "README.md").write_text(README, encoding="utf-8")
    (OUT / "Dockerfile").write_text(DOCKERFILE.format(version=args.potato_version), encoding="utf-8")
    # never commit answers, accounts or keys if the folder is also run locally for a test
    (OUT / ".gitignore").write_text("annotation_output/\nuser_config.json\nadmin_api_key.txt\nproject.sqlite*\nlayouts/\n", encoding="utf-8")
    with (OUT / "shared_ids.json").open("w", encoding="utf-8") as f:
        json.dump({"seed": args.seed, "shared_ids": shared, "labels_per_photo": args.labels_per_photo,
                   "per_annotator": args.per_annotator, "annotators": args.annotators}, f, indent=1)

    size_mb = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file() and ".git" not in p.parts) / 1e6
    print(f"Space folder: {OUT}  ({len(ids)} photos, {size_mb:.0f} MB)")
    print(f"  {len(shared)} shared photos for all {args.annotators} annotators, then {args.per_annotator - len(shared)} more each; "
          f"every other photo is labeled by {args.labels_per_photo} annotator(s)")
    print(f"  when all {args.annotators} annotators finish: {len(shared) + covered} of {len(ids)} photos have all their labels"
          + ("" if covered == rest_n else f"; {rest_n - covered} photos stay short (more annotators, or fewer labels per photo)"))
    if covered == rest_n and own_labels > rest_n * args.labels_per_photo:
        print(f"  the last annotators run out of photos before {args.per_annotator}: the list is finished after about "
              f"{(rest_n * args.labels_per_photo) / (args.per_annotator - len(shared)):.1f} annotators")
    print("  answers stay in annotation_output/ on this computer (no backup configured)" if args.no_backup
          else f"  answers are backed up to the Dataset: {args.backup_repo}")
    if "YOUR-HF-NAME" in args.backup_repo and not args.no_backup:
        print("\nWARNING: --backup-repo is still the placeholder. Rebuild with your real Hugging Face name before pushing.")
    if "TEAM TODO" in guidelines:
        print("WARNING: annotation/guidelines.md still has a TEAM TODO box. Finish it before real annotators use the Space.")


if __name__ == "__main__":
    main()
