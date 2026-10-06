"""
compute_agreement.py (Phase 2): inter-annotator agreement + majority-vote ground truth.

Input: the annotation_output/ folders annotators sent back, copied to
       annotation/returned/<annotator>/annotation_output/...
The annotation tool asks two questions per photo (Step 1 "cart": what kind of item,
Step 2 "condition": what state it is in). derive_label() below turns the two answers
into one of our four labels, and everything else in this script works on that label.

Reads, under annotation/returned/:
  * every <username>/user_state.json  (Potato's own save file, written on every click)
  * every exports/jsonl/annotations.jsonl  (Potato export format:
    {"instance_id", "user_id", "labels": {"label": {"<name>": ...}, "reason": {...}}})
The export can lag behind the save file, so when both have a label for the same
(item, annotator) the save file wins.

Reports (Lecture 6/7):
  * Fleiss' kappa on items labeled by ALL annotators (the agreement set)
  * Krippendorff's alpha (nominal) on everything (handles missing labels)
  * Cohen's kappa for every annotator pair (pairwise heat table)
  * internal-vs-external agreement (annotator ids starting with "internal")
Writes data/labels_majority.csv: id, label (majority vote), n_labels, agreement share, tie flag.

Usage: python scripts/compute_agreement.py [--returned annotation/returned]
"""

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LABELS = ["accepted", "accepted_after_prep", "not_accepted", "cannot_determine"]


def derive_label(cart, condition):
    """Turn the two answers from the annotation tool into one of the four final labels.

    Step 1 (cart):       blue_cart | not_blue_cart | cannot_tell
    Step 2 (condition):  ready | needs_prep | ruined | cannot_tell   (only asked for blue_cart)
    """
    if cart == "not_blue_cart":
        return "not_accepted"
    if cart == "cannot_tell":
        return "cannot_determine"
    if cart == "blue_cart":
        return {"ready": "accepted",
                "needs_prep": "accepted_after_prep",
                "ruined": "not_accepted",              # e.g. a greasy pizza box
                "cannot_tell": "cannot_determine"}.get(condition, "")
    return ""   # Step 1 not answered, or Step 2 still missing: not a finished label


def to_row(item, annotator, picked):
    """picked = {question name: chosen option}. Returns one table row, or None if unfinished."""
    cart = picked.get("cart", "")
    # Step 2 only counts for blue cart items. The tool can keep an old Step 2 answer
    # after the annotator changes Step 1, so we ignore it in every other case.
    condition = picked.get("condition", "") if cart == "blue_cart" else ""
    # packs made before the two-step design stored the label directly under "label"
    label = derive_label(cart, condition) if cart else picked.get("label", "")
    if label not in LABELS:
        return None
    return {"id": item, "annotator": annotator, "label": label,
            "reason": picked.get("reason", ""), "cart": cart, "condition": condition}


def load(returned):
    """One row per (item, annotator): id, annotator, label, reason, cart, condition."""
    rows = []
    # 1) the export file (may be missing an annotator's most recent labels)
    for f in sorted(Path(returned).rglob("annotations.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            picked = {q: next(iter(opts)) for q, opts in (r.get("labels") or {}).items() if opts}
            row = to_row(r["instance_id"], r["user_id"], picked)
            if row:
                rows.append(row)
    # 2) Potato's save file (always complete). Added last, so it wins below.
    for f in sorted(Path(returned).rglob("user_state.json")):
        state = json.loads(f.read_text(encoding="utf-8"))
        for item, pairs in (state.get("instance_id_to_label_to_value") or {}).items():
            picked = {}                      # question name -> chosen option
            for key, value in pairs:         # key = {"schema": "cart", "name": "blue_cart"}
                # Potato stores a CLEARED option as a "not selected" marker (value false or ""),
                # and media data under names starting with "_": neither is an answer.
                if value in (None, False, "") or str(key.get("name", "")).startswith("_"):
                    continue
                picked[key["schema"]] = key["name"]
            row = to_row(item, state.get("user_id", f.parent.name), picked)
            if row:
                rows.append(row)
    df = pd.DataFrame(rows, columns=["id", "annotator", "label", "reason", "cart", "condition"])
    return df.drop_duplicates(["id", "annotator"], keep="last")


def fleiss_kappa(counts):
    """counts: items x categories matrix, every row sums to the same n."""
    n = counts.sum(axis=1)[0]
    p_j = counts.sum(axis=0) / counts.sum()
    P_i = (np.square(counts).sum(axis=1) - n) / (n * (n - 1))
    P_bar, P_e = P_i.mean(), np.square(p_j).sum()
    return (P_bar - P_e) / (1 - P_e)


def krippendorff_nominal(df):
    """Nominal alpha from the coincidence matrix; items with < 2 labels are ignored."""
    idx = {c: i for i, c in enumerate(LABELS)}
    o = np.zeros((len(LABELS), len(LABELS)))
    for _, g in df.groupby("id"):
        vals = [idx[v] for v in g.label]
        m = len(vals)
        if m < 2:
            continue
        for a, b in itertools.permutations(range(m), 2):
            o[vals[a], vals[b]] += 1 / (m - 1)
    n_c = o.sum(axis=1); n = n_c.sum()
    if n == 0:
        return float("nan")
    D_o = (n - np.trace(o)) / n
    D_e = (n * n - np.square(n_c).sum()) / (n * (n - 1))
    return 1 - D_o / D_e


def cohen(a, b):
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(a, b, labels=LABELS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"))
    args = ap.parse_args()
    df = load(args.returned)
    if df.empty:
        raise SystemExit(f"No annotations (user_state.json / annotations.jsonl) found under {args.returned}")

    annots = sorted(df.annotator.unique())
    per_item = df.groupby("id").annotator.nunique()
    full = per_item[per_item == len(annots)].index
    print(f"{len(df)} labels | {df.id.nunique()} items | {len(annots)} annotators | "
          f"{len(full)} items labeled by everyone | {(per_item >= 2).sum()} items with 2+ labels")

    if len(full) > 0 and len(annots) > 1:
        sub = df[df.id.isin(full)]
        counts = pd.crosstab(sub.id, sub.label).reindex(columns=LABELS, fill_value=0).values
        print(f"Fleiss' kappa (agreement set): {fleiss_kappa(counts):.3f}")
    print(f"Krippendorff's alpha (all items, nominal): {krippendorff_nominal(df):.3f}")

    wide = df.pivot(index="id", columns="annotator", values="label")
    print("\nPairwise Cohen's kappa:")
    for a, b in itertools.combinations(annots, 2):
        both = wide[[a, b]].dropna()
        if len(both) >= 10:
            print(f"  {a:>14} vs {b:<14} n={len(both):>4}  kappa={cohen(both[a], both[b]):.3f}")

    out = []
    for item, g in df.groupby("id"):
        c = Counter(g.label).most_common()
        tie = len(c) > 1 and c[0][1] == c[1][1]
        out.append({"id": item, "label": c[0][0], "n_labels": len(g),
                    "agreement": round(c[0][1] / len(g), 3), "tie": tie})
    res = pd.DataFrame(out)
    res.to_csv(REPO / "data" / "labels_majority.csv", index=False)
    print(f"\nMajority labels -> data/labels_majority.csv  (ties: {res.tie.sum()})")
    print(res.label.value_counts().to_string())


if __name__ == "__main__":
    main()
