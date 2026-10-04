"""
prepare_images.py — Blue Cart Check (ARI 510, Group 2)

Takes a folder of raw phone photos and, for each one:
  1. fixes rotation (phones store rotation in EXIF),
  2. strips ALL metadata (EXIF, GPS, camera info),
  3. downsizes so the long edge is 512 px,
  4. renames to the next free ID (bcc_00001.jpg, bcc_00002.jpg, ...),
  5. appends one row to data/manifest.csv.

Duplicate photos (same file content) are skipped automatically.

ITEM GROUPS (important for honest train/test splits later):
  When you photograph the SAME physical object in several states (clean/dirty,
  bagged/loose, flat/unflattened), name the raw files with a shared prefix
  before the first "__" (double underscore), e.g.
      cup07__clean.jpg   cup07__lid_off.jpg   cup07__coffee_stain.jpg
  All three get item_group_id = "<initials>-cup07" and will always be kept in
  the same split. Files without "__" get their own group.

Usage (run from the repo root):
  pip install pillow
  python scripts/prepare_images.py --input data/raw/khurram \
      --photographer "Khurram Shafique" --category-set disposables \
      --setting bin_station --capture-date 2026-10-04

For openly licensed images, use one call per image or per batch with the same
source/license, and fill in source_url / attribution:
  python scripts/prepare_images.py --input data/raw/wikimedia_batch1 \
      --source wikimedia --license CC0-1.0 --attribution "See attribution.csv" \
      --category-set containers --setting other
"""

import argparse
import csv
import hashlib
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "data" / "manifest.csv"
OUT_DIR = REPO / "data" / "images"

FIELDS = [
    "id", "image_path", "width", "height", "source", "source_url", "license",
    "attribution", "capture_date", "setting", "category_set", "item_count",
    "item_group_id", "sha1", "notes",
]
SOURCES = ["team", "wikimedia", "openverse", "openimages"]
SETTINGS = ["kitchen", "office", "bin_station", "outdoor", "dining", "other"]
CATEGORY_SETS = ["containers", "paper", "disposables", "hard"]
EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
LONG_EDGE = 512


def load_manifest():
    if not MANIFEST.exists():
        return []
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def next_id(rows):
    nums = [int(r["id"].split("_")[1]) for r in rows if r.get("id", "").startswith("bcc_")]
    return (max(nums) + 1) if nums else 1


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="folder of raw photos")
    ap.add_argument("--photographer", default="", help="name, for team photos")
    ap.add_argument("--source", default="team", choices=SOURCES)
    ap.add_argument("--source-url", default="")
    ap.add_argument("--license", default="CC-BY-4.0")
    ap.add_argument("--attribution", default="")
    ap.add_argument("--setting", required=True, choices=SETTINGS)
    ap.add_argument("--category-set", required=True, choices=CATEGORY_SETS)
    ap.add_argument("--capture-date", default=date.today().isoformat())
    ap.add_argument("--item-count", type=int, default=1)
    ap.add_argument("--notes", default="")
    ap.add_argument("--initials", default="",
                    help="prefix for item_group_id, e.g. KS (default: from photographer/source)")
    args = ap.parse_args()

    src = Path(args.input)
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"No images found in {src}")

    if any(p.suffix.lower() == ".heic" for p in files):
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            sys.exit("HEIC photos found: run `pip install pillow-heif` first "
                     "(or set your iPhone camera to 'Most Compatible' / JPEG).")

    initials = args.initials or "".join(w[0] for w in args.photographer.split()).upper() or args.source[:3].upper()
    rows = load_manifest()
    seen = {r["sha1"] for r in rows if r.get("sha1")}
    n = next_id(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    new_rows, skipped = [], 0

    for p in files:
        digest = sha1_of(p)
        if digest in seen:
            skipped += 1
            continue
        img = Image.open(p)
        img = ImageOps.exif_transpose(img)          # apply rotation before metadata is dropped
        img = img.convert("RGB")
        img.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
        clean = Image.new("RGB", img.size)           # brand-new image => no metadata carried over
        clean.paste(img)
        img_id = f"bcc_{n:05d}"
        stem = p.stem
        group = f"{initials}-{stem.split('__')[0]}" if "__" in stem else f"{initials}-{img_id}"
        out = OUT_DIR / f"{img_id}.jpg"
        clean.save(out, "JPEG", quality=90)
        attribution = args.attribution or args.photographer
        new_rows.append({
            "id": img_id,
            "image_path": f"images/{img_id}.jpg",
            "width": clean.width, "height": clean.height,
            "source": args.source, "source_url": args.source_url,
            "license": args.license, "attribution": attribution,
            "capture_date": args.capture_date, "setting": args.setting,
            "category_set": args.category_set, "item_count": args.item_count,
            "item_group_id": group,
            "sha1": digest, "notes": args.notes,
        })
        seen.add(digest)
        n += 1

    write_header = not MANIFEST.exists() or MANIFEST.stat().st_size == 0
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        w.writerows(new_rows)

    print(f"Added {len(new_rows)} images ({skipped} duplicates skipped). "
          f"Manifest now has {len(rows) + len(new_rows)} rows.")


if __name__ == "__main__":
    main()
