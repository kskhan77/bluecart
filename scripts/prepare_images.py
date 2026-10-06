"""
prepare_images.py — Blue Cart Check (ARI 510, Group 2)

Takes a folder of raw phone photos and, for each one:
  1. fixes rotation (phones store rotation in EXIF),
  2. strips ALL metadata (EXIF, GPS, camera info),
  3. downsizes so the long edge is 512 px,
  4. renames to the next free ID (bcc_00001.jpg, bcc_00002.jpg, ...),
  5. appends one row to data/manifest.csv.

Duplicate photos (same file content) are skipped automatically.

CAPTURE DATE: if you do not pass --capture-date, each team photo gets the
"date taken" stored by the phone (EXIF). Photos without one (and sourced
images, where capture_date means the download date) use the file's
modification date, and that fallback is written into the notes column.

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
      --setting bin_station

IMAGES WE DID NOT TAKE OURSELVES (any --source other than "team"):
  Use one call per batch that shares the same source, author and license.
  --attribution must be the ORIGINAL author, never a team member. The script
  also adds one credit row per image to data/attribution.csv (source, URL,
  original file name, author, license), which the license requires.
  --sample N takes a random N files from the folder (same --seed = same files),
  so we can use part of a big dataset and still describe exactly how we chose.
  If a team member is responsible for the batch, say so in --notes.
  python scripts/prepare_images.py --input data/raw/RealWaste/Cardboard \
      --source realwaste --source-url https://github.com/sam-single/realwaste \
      --license CC-BY-NC-SA-4.0 --license-url https://creativecommons.org/licenses/by-nc-sa/4.0/ \
      --attribution "Sam Single et al. (RealWaste)" --sample 70 --seed 42 \
      --category-set paper --setting other --notes "assigned to Hina Kramer's set"
"""

import argparse
import csv
import hashlib
import random
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "data" / "manifest.csv"
ATTRIBUTION = REPO / "data" / "attribution.csv"
OUT_DIR = REPO / "data" / "images"

FIELDS = [
    "id", "image_path", "width", "height", "source", "source_url", "license",
    "attribution", "capture_date", "setting", "category_set", "item_count",
    "item_group_id", "sha1", "notes",
]
ATTRIBUTION_FIELDS = ["id", "source", "source_url", "title", "author", "license", "license_url", "downloaded_on"]
SOURCES = ["team", "wikimedia", "openverse", "openimages", "realwaste", "kaggle_drinking_waste"]
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


def exif_date_taken(img):
    """Return the phone's 'date taken' as YYYY-MM-DD, or "" if the photo has none."""
    try:
        exif = img.getexif()
        raw = exif.get_ifd(0x8769).get(0x9003) or exif.get(0x0132)   # DateTimeOriginal, else DateTime
        return datetime.strptime(str(raw)[:10], "%Y:%m:%d").date().isoformat() if raw else ""
    except (ValueError, TypeError, AttributeError, KeyError, OSError):
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="folder of raw photos")
    ap.add_argument("--photographer", default="", help="name, for team photos")
    ap.add_argument("--source", default="team", choices=SOURCES)
    ap.add_argument("--source-url", default="")
    ap.add_argument("--license", default="CC-BY-4.0")
    ap.add_argument("--license-url", default="", help="link to the license text (sourced images)")
    ap.add_argument("--attribution", default="", help="ORIGINAL author of sourced images (never a team member)")
    ap.add_argument("--sample", type=int, default=0, help="use only a random N files from the folder (0 = all)")
    ap.add_argument("--seed", type=int, default=42, help="random seed for --sample")
    ap.add_argument("--setting", required=True, choices=SETTINGS)
    ap.add_argument("--category-set", required=True, choices=CATEGORY_SETS)
    ap.add_argument("--capture-date", default="",
                    help="YYYY-MM-DD for the whole batch (default: per photo, from EXIF or the file date)")
    ap.add_argument("--item-count", type=int, default=1)
    ap.add_argument("--notes", default="")
    ap.add_argument("--initials", default="",
                    help="prefix for item_group_id, e.g. KS (default: from photographer/source)")
    args = ap.parse_args()

    src = Path(args.input)
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"No images found in {src}")
    if args.source != "team" and not args.attribution:
        sys.exit("Sourced images need --attribution with the ORIGINAL author's name.")
    found = len(files)
    if args.sample and args.sample < found:          # reproducible random sample of a larger folder
        files = sorted(random.Random(args.seed).sample(files, args.sample))

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
    new_rows, credit_rows, skipped = [], [], 0

    for p in files:
        digest = sha1_of(p)
        if digest in seen:
            skipped += 1
            continue
        img = Image.open(p)
        notes = args.notes
        capture_date = args.capture_date or (exif_date_taken(img) if args.source == "team" else "")
        if not capture_date:                         # no EXIF date: fall back to the file's date
            capture_date = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
            notes = "; ".join(x for x in [notes, "capture_date from file timestamp (no EXIF date)"] if x)
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
            "capture_date": capture_date, "setting": args.setting,
            "category_set": args.category_set, "item_count": args.item_count,
            "item_group_id": group,
            "sha1": digest, "notes": notes,
        })
        if args.source != "team":                    # one credit row per image we did not take ourselves
            credit_rows.append({
                "id": img_id, "source": args.source, "source_url": args.source_url,
                "title": p.name,                         # original file name, so the image can be traced back
                "author": args.attribution, "license": args.license,
                "license_url": args.license_url, "downloaded_on": capture_date,
            })
        seen.add(digest)
        n += 1

    write_header = not MANIFEST.exists() or MANIFEST.stat().st_size == 0
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        w.writerows(new_rows)

    if credit_rows:
        write_header = not ATTRIBUTION.exists() or ATTRIBUTION.stat().st_size == 0
        with ATTRIBUTION.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=ATTRIBUTION_FIELDS)
            if write_header:
                w.writeheader()
            w.writerows(credit_rows)

    picked = f" (random {len(files)} of {found} files, seed {args.seed})" if len(files) < found else ""
    print(f"Added {len(new_rows)} images{picked} ({skipped} duplicates skipped). "
          f"Manifest now has {len(rows) + len(new_rows)} rows."
          + (f" {len(credit_rows)} credit rows added to attribution.csv." if credit_rows else ""))


if __name__ == "__main__":
    main()
