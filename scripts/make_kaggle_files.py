"""Phase 2a, step 5: the group-safe, stratified split and the four files a Kaggle community competition expects.

Labels come from annotation/returned/gold_labels.csv (after merge_adjudication.py). Until that file exists the script
runs in PREVIEW mode on majority_labels.csv, with the ties as their own stratum, so the files can be checked early;
the real run happens once the team has adjudicated (then pass --write-repo as well).

Writes deploy/kaggle/ (gitignored):
  public/train.csv               id, image, split (train / val), label        -> upload to Kaggle as data
  public/test.csv                id, image                                    -> upload as data
  public/sample_submission.csv   id, label (every row "accepted" = the majority baseline)  -> upload as sample submission
  public/images/<id>.jpg         every photo of the three splits               -> upload as data (also zipped)
  public/README.txt              the file description for the Data page
  private/solution.csv           id, label, Usage (Public / Private)          -> upload ONLY as the answer key
  private/splits.csv             id, item_group_id, split, usage              -> keep private
  blue_cart_check_kaggle_data.zip  the public folder, ready to upload
With --write-repo it also writes data/splits.csv (id, item_group_id, split) and data/labels_trainval.csv (train and
validation labels only), which may be committed: test labels never leave the private folder.

Split: StratifiedGroupKFold keeps every item_group_id (the same object photographed in several states) on one side,
and keeps the label shares equal across train / val / test. The test set is then halved into Public and Private
rows, again stratified, so both leaderboards see every class. Once private/splits.csv exists the same split is
reused on every later run (so the baselines stay comparable between the preview and the final labels); pass
--resplit to draw a new one.

    python scripts/make_kaggle_files.py                       # preview or final, depending on gold_labels.csv
    python scripts/make_kaggle_files.py --test 0.25 --val 0.1 --seed 42 --write-repo
"""
import argparse
import collections
import csv
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

REPO = Path(__file__).resolve().parents[1]
LABELS = ["accepted", "accepted_after_prep", "not_accepted", "cannot_determine"]
MAJORITY = "accepted"

README = """Blue Cart Check: does this item go in Flint's blue recycling cart?

One photo of one everyday item -> one of four labels:
  accepted             accepted material, ready as it is (clean, empty, loose)
  accepted_after_prep  accepted material that needs a rinse, emptying, flattening or un-bagging first
  not_accepted         never the blue cart (bags, cups, styrofoam, greasy paper, electronics, ...) or ruined material
  cannot_determine     the photo does not show enough to decide

Files
  train.csv              id, image, split, label   ({n_train} train + {n_val} val photos; use our val split or make your own)
  test.csv               id, image                 ({n_test} photos, no labels)
  sample_submission.csv  id, label                 the format to upload; as it stands it is the majority baseline
  images/                every photo, JPEG, long side 512 px, named <id>.jpg; the image column holds this path

Labels were given by 15 human annotators (3 to 6 per photo) with a written guideline, then disagreements were
settled by the project team. Metric: macro-F1 over the four labels. Data: CC BY-NC-SA 4.0, for use in
ARI 410/510 (UM-Flint, Fall 2026) only; per-photo credits in attribution.csv on
https://github.com/kskhan77/bluecart (which holds the photos but no labels).
"""


def load_labels(returned):
    """Return (DataFrame id,label,stratum ; mode). Final mode needs gold_labels.csv with every photo decided."""
    gold = returned / "gold_labels.csv"
    if gold.exists():
        g = pd.read_csv(gold, dtype=str).fillna("")
        unresolved = g[g.source == "unresolved"]
        if len(unresolved):
            sys.exit(f"{len(unresolved)} photos are still unresolved in {gold}; finish the adjudication first "
                     f"(or delete the file to run the preview on the majority vote)")
        g = g[g.label != "exclude_photo"]
        return pd.DataFrame({"id": g.photo_id, "label": g.label, "stratum": g.label}), "final"
    m = pd.read_csv(returned / "majority_labels.csv", dtype=str).fillna("")
    lab = m.majority_label.where(m.majority_label != "", "undecided")
    return pd.DataFrame({"id": m.photo_id, "label": lab, "stratum": lab}), "preview"


def group_split(df, frac, seed):
    """Take about `frac` of df as the second part, never splitting an item group, label shares kept."""
    k = max(2, round(1 / frac))
    folds = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed)
    keep, take = next(folds.split(df, df.stratum, df.item_group_id))
    return df.iloc[keep].reset_index(drop=True), df.iloc[take].reset_index(drop=True)


def public_private(test, seed):
    """Half of the test rows Public, half Private, stratified where every class has at least two rows."""
    counts = test.stratum.value_counts()
    strat = test.stratum if counts.min() >= 2 else None
    pub, priv = train_test_split(test.index, test_size=0.5, random_state=seed, stratify=strat)
    usage = pd.Series("Public", index=test.index); usage[priv] = "Private"
    return usage


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"))
    ap.add_argument("--images", default=str(REPO / "data" / "images"))
    ap.add_argument("--manifest", default=str(REPO / "data" / "manifest.csv"))
    ap.add_argument("--out", default=str(REPO / "deploy" / "kaggle"))
    ap.add_argument("--test", type=float, default=0.25, help="share of photos in the hidden test set")
    ap.add_argument("--val", type=float, default=0.10, help="share of photos in the validation split")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--write-repo", action="store_true", help="also write data/splits.csv and data/labels_trainval.csv")
    ap.add_argument("--no-images", action="store_true", help="skip copying and zipping the photos (tests)")
    ap.add_argument("--resplit", action="store_true", help="draw a new split even though <out>/private/splits.csv exists")
    args = ap.parse_args()

    labels, mode = load_labels(Path(args.returned))
    manifest = pd.read_csv(args.manifest, dtype=str)[["id", "item_group_id"]]
    df = labels.merge(manifest, on="id", how="left")
    if df.item_group_id.isna().any():
        sys.exit("labeled photos missing from the manifest: " + ", ".join(df[df.item_group_id.isna()].id))
    df = df.sort_values("id").reset_index(drop=True)

    out = Path(args.out); pub, priv = out / "public", out / "private"
    for d in (pub, priv):
        d.mkdir(parents=True, exist_ok=True)
    previous = priv / "splits.csv"
    if previous.exists() and not args.resplit:
        # keep the split that baselines were already run on: only the labels change between preview and final
        old = pd.read_csv(previous, dtype=str).fillna("")[["id", "split", "usage"]]
        allrows = df.merge(old, on="id", how="left")
        if allrows.split.isna().any():
            sys.exit(f"photos not in the previous split {previous}: " + ", ".join(allrows[allrows.split.isna()].id) + " (pass --resplit)")
        train, val, test = (allrows[allrows.split == s].reset_index(drop=True) for s in ("train", "val", "test"))
        split_note = f"split reused from {previous}"
    else:
        rest, test = group_split(df, args.test, args.seed)
        train, val = group_split(rest, args.val / (1 - args.test), args.seed)
        test = test.assign(usage=public_private(test, args.seed).values)
        train, val = train.assign(split="train", usage=""), val.assign(split="val", usage="")
        test = test.assign(split="test")
        allrows = pd.concat([train, val, test], ignore_index=True).sort_values("id").reset_index(drop=True)
        split_note = f"new split, seed {args.seed}"
    image = "images/" + allrows.id + ".jpg"
    tv = allrows[allrows.split != "test"]
    tv.assign(image=image[tv.index])[["id", "image", "split", "label"]].to_csv(pub / "train.csv", index=False)
    te = allrows[allrows.split == "test"]
    te.assign(image=image[te.index])[["id", "image"]].to_csv(pub / "test.csv", index=False)
    te.assign(label=MAJORITY)[["id", "label"]].to_csv(pub / "sample_submission.csv", index=False)
    te.rename(columns={"usage": "Usage"})[["id", "label", "Usage"]].to_csv(priv / "solution.csv", index=False)
    allrows[["id", "item_group_id", "split", "usage"]].to_csv(priv / "splits.csv", index=False)
    (pub / "README.txt").write_text(README.format(n_train=len(train), n_val=len(val), n_test=len(test)), encoding="utf-8")
    if not args.no_images:
        img_dir = pub / "images"; img_dir.mkdir(exist_ok=True)
        for pid in allrows.id:
            shutil.copy(Path(args.images) / f"{pid}.jpg", img_dir / f"{pid}.jpg")
        with zipfile.ZipFile(out / "blue_cart_check_kaggle_data.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(pub.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(pub))
    if args.write_repo:
        if mode != "final":
            sys.exit("--write-repo only with the adjudicated gold labels, not in preview mode")
        allrows[["id", "item_group_id", "split"]].to_csv(REPO / "data" / "splits.csv", index=False)
        tv[["id", "label"]].to_csv(REPO / "data" / "labels_trainval.csv", index=False)

    print(f"{mode.upper()}: {len(allrows)} photos -> train {len(train)}, val {len(val)}, test {len(test)} "
          f"(Public {int((test.usage == 'Public').sum())}, Private {int((test.usage == 'Private').sum())}); {split_note}; written to {out}")
    table = pd.crosstab(allrows.split, allrows.stratum).reindex(["train", "val", "test"])
    table.loc["test (Public)"] = test[test.usage == "Public"].stratum.value_counts()
    table.loc["test (Private)"] = test[test.usage == "Private"].stratum.value_counts()
    print(table.fillna(0).astype(int).to_string())
    groups = allrows.groupby("item_group_id").split.nunique()
    print(f"item groups split across sets: {int((groups > 1).sum())} (must be 0)")
    if mode == "preview":
        print("preview on the majority vote: the undecided photos will take their adjudicated label; rerun after merge_adjudication.py")


if __name__ == "__main__":
    main()
