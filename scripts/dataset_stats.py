"""
dataset_stats.py — descriptive statistics for the README and the Oct 6 slides.

Reads data/manifest.csv and prints:
  - total images
  - breakdown by source (team vs. sourced), category set, setting, photographer
  - image size summary
and saves two simple bar charts to docs/stats_*.png for the slides.

Usage (from repo root):
  pip install pandas matplotlib
  python scripts/dataset_stats.py
"""

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
df = pd.read_csv(REPO / "data" / "manifest.csv")

print(f"Total images: {len(df)}\n")
for col in ["source", "category_set", "setting", "attribution", "license"]:
    if col in df:
        counts = df[col].fillna("(blank)").value_counts()
        print(f"--- {col} ---")
        for k, v in counts.items():
            print(f"  {k:<28} {v:>5}  ({v / len(df):.0%})")
        print()

print("--- image size (px) ---")
print(df[["width", "height"]].describe().loc[["min", "mean", "max"]].round(0).to_string())
print("\n--- capture dates ---")
print(f"  {df['capture_date'].min()}  to  {df['capture_date'].max()}")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = REPO / "docs"
    out.mkdir(exist_ok=True)
    for col, title in [("category_set", "Images per category set"),
                       ("source", "Images per source")]:
        counts = df[col].value_counts()
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.barh(counts.index[::-1], counts.values[::-1], color="#2b6cb0")
        for i, v in enumerate(counts.values[::-1]):
            ax.text(v, i, f" {v}", va="center", fontsize=9)
        ax.set_title(title, loc="left", fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xlabel("images")
        fig.tight_layout()
        fig.savefig(out / f"stats_{col}.png", dpi=200)
        plt.close(fig)
    print(f"\nCharts saved to {out}/stats_category_set.png and stats_source.png")
except ImportError:
    print("\n(matplotlib not installed: skipped charts)")
