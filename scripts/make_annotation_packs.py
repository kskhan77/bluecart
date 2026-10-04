"""
make_annotation_packs.py — split the dataset into annotator packs.

Design (handout Section 3.3):
  * AGREEMENT SET: N images that EVERY annotator (external + internal) labels.
    -> used in Phase 2 for inter-annotator agreement + majority-vote ground truth.
  * COVERAGE BATCHES: the remaining images, split into non-overlapping batches,
    one per annotator, so as much of the dataset as possible gets labeled.

Each annotator gets a self-contained folder (zip it and send it):
  packs/annotator_XX/
      config.yaml          Potato config (same for everyone)
      data/items.jsonl     agreement set + this annotator's batch, shuffled
      media/               only the images this annotator needs
      guidelines.md        the annotation guidelines
      HOW_TO_ANNOTATE.md   setup steps

Usage (from repo root):
  python scripts/make_annotation_packs.py --agreement 100 --batch 150 \
      --external 5 --internal 1 --seed 42
"""

import argparse
import csv
import json
import random
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POTATO = REPO / "annotation" / "potato"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agreement", type=int, default=100, help="images every annotator labels")
    ap.add_argument("--batch", type=int, default=150, help="extra non-overlapping images per annotator")
    ap.add_argument("--external", type=int, default=5)
    ap.add_argument("--internal", type=int, default=1)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    with (REPO / "data" / "manifest.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rng = random.Random(args.seed)
    rng.shuffle(rows)

    agreement = rows[:args.agreement]
    rest = rows[args.agreement:]
    names = [f"external_{i + 1:02d}" for i in range(args.external)] + \
            [f"internal_{i + 1:02d}" for i in range(args.internal)]

    out_root = REPO / "annotation" / "packs"
    if out_root.exists():
        shutil.rmtree(out_root)

    plan = {"seed": args.seed, "agreement_ids": [r["id"] for r in agreement], "batches": {}}
    for k, name in enumerate(names):
        batch = rest[k * args.batch:(k + 1) * args.batch]
        items = agreement + batch
        rng.shuffle(items)  # agreement items are mixed in, not shown first
        plan["batches"][name] = [r["id"] for r in batch]

        pack = out_root / name
        (pack / "data").mkdir(parents=True)
        (pack / "media").mkdir()
        with (pack / "data" / "items.jsonl").open("w", encoding="utf-8") as f:
            for r in items:
                f.write(json.dumps({"id": r["id"], "image": f"/media/{r['id']}.jpg"}) + "\n")
                shutil.copy(REPO / "data" / r["image_path"], pack / "media" / f"{r['id']}.jpg")
        shutil.copy(POTATO / "config.yaml", pack / "config.yaml")
        shutil.copy(REPO / "annotation" / "guidelines.md", pack / "guidelines.md")
        shutil.copy(REPO / "annotation" / "HOW_TO_ANNOTATE.md", pack / "HOW_TO_ANNOTATE.md")
        shutil.make_archive(str(out_root / f"bluecartcheck_{name}"), "zip", pack)

    with (REPO / "annotation" / "assignment_plan.json").open("w") as f:
        json.dump(plan, f, indent=1)

    used = len(agreement) + sum(len(v) for v in plan["batches"].values())
    print(f"Agreement set: {len(agreement)} images x {len(names)} annotators")
    print(f"Coverage: {used - len(agreement)} more images across {len(names)} batches")
    print(f"Images that get at least one label: {used} of {len(rows)}")
    if used < len(rows):
        print(f"  ({len(rows) - used} unassigned; increase --batch or team annotation to cover them)")
    print(f"Zips written to {out_root}/")


if __name__ == "__main__":
    main()
