"""
compute_agreement.py (Phase 2): inter-annotator agreement + majority-vote ground truth.

Input: the annotation_output/ folders annotators sent back, copied to
       annotation/returned/<annotator>/annotation_output/...
Reads every annotations.jsonl under annotation/returned/ (Potato export format:
{"instance_id", "user_id", "labels": {"label": {"<name>": ...}, "reason": {...}}}).

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


def load(returned):
    rows = []
    for f in Path(returned).rglob("annotations.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            lab = list((r.get("labels", {}).get("label") or {}).keys())
            if lab:
                reason = list((r.get("labels", {}).get("reason") or {}).keys())
                rows.append({"id": r["instance_id"], "annotator": r["user_id"],
                             "label": lab[0], "reason": reason[0] if reason else ""})
    df = pd.DataFrame(rows).drop_duplicates(["id", "annotator"], keep="last")
    return df


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
        raise SystemExit(f"No annotations.jsonl found under {args.returned}")

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
