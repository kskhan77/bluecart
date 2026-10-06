"""
show_labels.py: look at the labels people have given so far.

Reads the annotation_output folders under --returned (the same files that
compute_agreement.py reads) and gives you three views:

  1. In the terminal: how many labels each annotator gave, how often each
     label was used, and one row per photo with every annotator's label.
     Photos where annotators disagree are marked with "<-- disagree".
  2. <returned>/labels_table.csv   the same table, for Excel / pandas.
  3. <returned>/labels_review.html one page with a small copy of every labeled
     photo next to the labels it got. Open it in a browser. Tick "only
     disagreements" to see the photos the team should discuss.

Usage (from the repo root):
    python scripts/show_labels.py                                   # annotation/returned/
    python scripts/show_labels.py --returned annotation/packs/internal_01

The outputs contain annotator names, so they stay in the (git-ignored)
--returned folder. This script only reads labels; it never changes them.
"""

import argparse
import base64
import html
import importlib.util
import io
from collections import Counter
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
COLORS = {"accepted": "#1f7a3d", "accepted_after_prep": "#a86a00",
          "not_accepted": "#b3261e", "cannot_determine": "#5b6472"}


def load_labels(returned):
    """Reuse the loader from compute_agreement.py so both scripts read labels the same way."""
    spec = importlib.util.spec_from_file_location("compute_agreement", REPO / "scripts" / "compute_agreement.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load(returned)


def thumbnail(image_id, size=220):
    """Small copy of data/images/<id>.jpg as text, so the HTML page is one self-contained file."""
    path = REPO / "data" / "images" / f"{image_id}.jpg"
    if not path.exists():
        return ""
    img = Image.open(path).convert("RGB")
    img.thumbnail((size, size))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def write_html(wide, notes, annotators, out_path):
    cards = []
    for image_id, row in wide.iterrows():
        given = [(a, row[a]) for a in annotators if isinstance(row[a], str)]
        disagree = len({label for _, label in given}) > 1
        lines = "".join(
            f"<div><span class='who'>{html.escape(a)}</span> "
            f"<b style='color:{COLORS.get(label, '#333')}'>{html.escape(label)}</b>"
            f"<span class='why'>{html.escape(notes.get((image_id, a), ''))}</span></div>"
            for a, label in given)
        cards.append(
            f"<div class='card{' disagree' if disagree else ''}'>"
            f"<img src='{thumbnail(image_id)}' alt='{image_id}'>"
            f"<div class='id'>{image_id}{' &nbsp;&#9888; disagree' if disagree else ''}</div>{lines}</div>")
    n_dis = sum("card disagree" in c for c in cards)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Blue Cart Check: labels so far</title>
<style>
 body {{ font-family: system-ui, "Segoe UI", sans-serif; margin: 20px; background: #f5f6f8; color: #1f2430; }}
 .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px; }}
 .card {{ background: #fff; border: 1px solid #d9dee8; border-radius: 10px; padding: 10px; font-size: 0.9rem; }}
 .card.disagree {{ border: 2px solid #b3261e; }}
 .card img {{ display: block; margin: 0 auto 8px; max-width: 100%; border-radius: 6px; }}
 .id {{ font-weight: 600; margin-bottom: 4px; }} .who {{ color: #5b6472; }} .why {{ color: #5b6472; margin-left: 6px; font-size: 0.85em; }}
 body.only .card:not(.disagree) {{ display: none; }}
</style></head><body>
<h2>Blue Cart Check: labels so far</h2>
<p>{len(cards)} labeled photos, {len(annotators)} annotator(s), {n_dis} photo(s) with a disagreement.
 <label><input type="checkbox" onchange="document.body.classList.toggle('only', this.checked)"> only disagreements</label></p>
<div class="grid">{''.join(cards)}</div></body></html>"""
    out_path.write_text(page, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"),
                    help="folder that contains the annotators' annotation_output folders")
    args = ap.parse_args()
    returned = Path(args.returned)

    df = load_labels(returned)
    if df.empty:
        raise SystemExit(f"No labels found under {returned}")

    annotators = sorted(df.annotator.unique())
    print(f"{len(df)} labels on {df.id.nunique()} photos by {len(annotators)} annotator(s)\n")
    print("--- labels per annotator ---")
    for a, n in df.annotator.value_counts().items():
        print(f"  {a:<24} {n:>4}")
    print("\n--- how often each label was used ---")
    for label, n in df.label.value_counts().items():
        print(f"  {label:<24} {n:>4}  ({n / len(df):.0%})")

    # one row per photo, one column per annotator
    wide = df.pivot(index="id", columns="annotator", values="label").sort_index()
    print("\n--- one row per photo ---")
    print(f"  {'photo':<11}" + "".join(f"{a[:20]:<22}" for a in annotators))
    n_disagree = 0
    for image_id, row in wide.iterrows():
        given = [row[a] for a in annotators if isinstance(row[a], str)]
        disagree = len(set(given)) > 1
        n_disagree += disagree
        cells = "".join(f"{(row[a] if isinstance(row[a], str) else '-'):<22}" for a in annotators)
        print(f"  {image_id:<11}{cells}{'<-- disagree' if disagree else ''}")
    both = int((wide.notna().sum(axis=1) >= 2).sum())
    print(f"\n{both} photo(s) have 2+ labels; annotators disagree on {n_disagree} of them.")

    wide.to_csv(returned / "labels_table.csv")
    # small grey note next to each label: the two answers that led to it, and the optional reason
    notes = {(r.id, r.annotator): " | ".join(x for x in [" > ".join(y for y in [r.cart, r.condition] if y), r.reason] if x)
             for r in df.itertuples()}
    write_html(wide, notes, annotators, returned / "labels_review.html")
    print(f"\nTable  -> {returned / 'labels_table.csv'}")
    print(f"Photos -> {returned / 'labels_review.html'}  (open it in a browser)")


if __name__ == "__main__":
    main()
