"""
make_splits.py: train / validation / test split that never separates an item group
(the same physical object photographed clean/dirty, bagged/loose, ...).

Lecture 2: test data must be unseen and representative. If "cup07 clean" is in
train and "cup07 dirty" is in test, the test score is inflated (leakage).

If data/labels_majority.csv exists (after Phase 2), the split is also
stratified by label (StratifiedGroupKFold); otherwise it uses groups only.

Writes data/splits.csv: id, item_group_id, split

Usage:
  python scripts/make_splits.py --test 0.2 --val 0.1 --seed 42
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold

REPO = Path(__file__).resolve().parents[1]


def group_split(df, frac, seed, strat=None):
    if strat is not None:
        k = max(2, round(1 / frac))
        sgkf = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed)
        a, b = next(sgkf.split(df, strat, df.item_group_id))
    else:
        gss = GroupShuffleSplit(n_splits=1, test_size=frac, random_state=seed)
        a, b = next(gss.split(df, groups=df.item_group_id))
    return df.iloc[a], df.iloc[b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", type=float, default=0.2)
    ap.add_argument("--val", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-labels-ok", action="store_true", help="allow splitting before labels exist")
    args = ap.parse_args()

    df = pd.read_csv(REPO / "data" / "manifest.csv")
    lab_path = REPO / "data" / "labels_majority.csv"
    strat = None
    if lab_path.exists():
        lab = pd.read_csv(lab_path)[["id", "label"]]
        df = df.merge(lab, on="id", how="inner")
        strat = df.label.values
    elif not args.no_labels_ok:
        raise SystemExit("No data/labels_majority.csv yet. Run compute_agreement.py first, or pass --no-labels-ok.")
    df = df.reset_index(drop=True)

    rest, test = group_split(df, args.test, args.seed, strat)
    rest = rest.reset_index(drop=True)
    strat_rest = rest.label.values if strat is not None else None
    train, val = group_split(rest, args.val / (1 - args.test), args.seed, strat_rest)

    out = pd.concat([train.assign(split="train"), val.assign(split="val"), test.assign(split="test")], ignore_index=True)
    out[["id", "item_group_id", "split"]].sort_values("id").to_csv(REPO / "data" / "splits.csv", index=False)
    print(out.split.value_counts().to_string())
    if strat is not None:
        print(pd.crosstab(out.split, out.label, normalize="index").round(2).to_string())


if __name__ == "__main__":
    main()
