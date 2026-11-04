"""Phase 2a, step 4: how many photos carry each label, as a chart for the slides and a few numbers for the talk.

Reads annotation/returned/gold_labels.csv (the adjudicated labels from merge_adjudication.py) when it exists,
otherwise majority_labels.csv (a preview: ties show as an "undecided" bar). Writes docs/figures/label_distribution.png
(a class count reveals nothing about any single photo, so the figure may be committed) and prints the counts, the
shares, the imbalance ratio and what the majority baseline would score, which is the argument for macro-F1.

    python scripts/label_distribution.py                      # gold labels if present, else majority preview
    python scripts/label_distribution.py --source majority    # force the preview
"""
import argparse
import collections
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[1]
LABELS = ["accepted", "accepted_after_prep", "not_accepted", "cannot_determine"]
NICE = {"accepted": "accepted", "accepted_after_prep": "accepted after prep", "not_accepted": "not accepted",
        "cannot_determine": "cannot determine", "undecided": "undecided (tie)"}
BLUE, GRAY, INK, MUTED = "#2a78d6", "#b8b7b2", "#0b0b0b", "#52514e"


def load(folder, source):
    """Return (Counter of labels incl. 'undecided', number excluded, description of the source)."""
    gold = folder / "gold_labels.csv"
    if source == "gold" or (source == "auto" and gold.exists()):
        rows = list(csv.DictReader(gold.open(encoding="utf-8")))
        labels = [r["label"] or "undecided" for r in rows]
        what = "adjudicated labels" if "undecided" not in labels else "adjudicated labels, some still open"
    else:
        rows = list(csv.DictReader((folder / "majority_labels.csv").open(encoding="utf-8")))
        labels = [r["majority_label"] or "undecided" for r in rows]
        what = "majority vote, ties still open"
    excluded = labels.count("exclude_photo")
    return collections.Counter(l for l in labels if l != "exclude_photo"), excluded, what


def chart(counts, what, out):
    order = LABELS + (["undecided"] if counts["undecided"] else [])
    total = sum(counts[k] for k in order)
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=200)
    fig.patch.set_facecolor("white")
    ys = range(len(order))[::-1]
    for y, k in zip(ys, order):
        ax.barh(y, counts[k], height=0.52, color=GRAY if k == "undecided" else BLUE, hatch="///" if k == "undecided" else None,
                edgecolor="white", linewidth=0)
        ax.text(counts[k] + total * 0.012, y, f"{counts[k]}  ({100 * counts[k] / total:.0f}%)", va="center", ha="left", fontsize=10, color=INK)
    ax.set_yticks(list(ys)); ax.set_yticklabels([NICE[k] for k in order], fontsize=11, color=INK)
    ax.set_xlim(0, max(counts[k] for k in order) * 1.22)
    ax.xaxis.set_visible(False)
    for side in ("top", "right", "bottom"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#d9d8d3")
    ax.tick_params(axis="y", length=0)
    ax.set_title(f"Blue Cart Check: label per photo ({total} photos, {what})", fontsize=11, color=MUTED, loc="left", pad=12)
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"))
    ap.add_argument("--source", choices=["auto", "gold", "majority"], default="auto")
    ap.add_argument("--out", default=str(REPO / "docs" / "figures" / "label_distribution.png"))
    args = ap.parse_args()
    counts, excluded, what = load(Path(args.returned), args.source)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    chart(counts, what, out)

    decided = sum(counts[k] for k in LABELS); total = decided + counts["undecided"]
    print(f"{out.name}: {total} photos ({what})" + (f", {excluded} excluded" if excluded else ""))
    print("| label | photos | share of decided |\n|---|---|---|")
    for k in LABELS:
        print(f"| {k} | {counts[k]} | {100 * counts[k] / decided:.1f}% |")
    if counts["undecided"]:
        print(f"| undecided (tie) | {counts['undecided']} | |")
    big, small = max(LABELS, key=lambda k: counts[k]), min(LABELS, key=lambda k: counts[k])   # counts[k] is 0 for an absent class
    share = counts[big] / decided; f1_big = 2 * share / (1 + share)
    print(f"\nImbalance: {big} has {counts[big]} photos, {small} has {counts[small]}: {counts[big] / max(counts[small], 1):.0f} to 1. "
          f"Classes under 10%: {', '.join(k for k in LABELS if counts[k] / decided < 0.10) or 'none'}.")
    print(f"A model that always says '{big}' scores accuracy {100 * share:.0f}% but macro-F1 {f1_big / 4:.2f} "
          f"(F1 {f1_big:.2f} on that class, 0 on the other three). Macro-F1 is the metric; recall on not_accepted is the safety gate.")


if __name__ == "__main__":
    main()
