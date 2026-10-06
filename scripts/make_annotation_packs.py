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
      welcome.html         welcome page shown once before the first photo
      data/items.jsonl     agreement set + this annotator's batch, shuffled
      media/               only the images this annotator needs
      media/guidelines.html  the guidelines as a web page (opens from the "Guidelines" button in the tool)
      media/how_it_works.html  the welcome page again, for the round help button (Potato shows welcome.html only once)
      media/demo/          the project demo page with screenshots (the video is left out to keep the zip small)
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
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
POTATO = REPO / "annotation" / "potato"


GUIDELINES_CSS = """
body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; line-height: 1.55; max-width: 880px;
       margin: 0 auto; padding: 24px 20px 60px; color: #1f2430; background: #ffffff; }
h1 { font-size: 1.6rem; } h2 { font-size: 1.25rem; margin-top: 2rem; border-bottom: 1px solid #d9dee8; padding-bottom: 4px; }
h3 { font-size: 1.05rem; margin-top: 1.4rem; }
table { border-collapse: collapse; margin: 0.8rem 0; width: 100%; }
th, td { border: 1px solid #d0d6e2; padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: #eef2f8; }
blockquote { margin: 1rem 0; padding: 8px 14px; border-left: 4px solid #e0a100; background: #fff7df; }
code { background: #eef1f6; padding: 1px 5px; border-radius: 4px; font-size: 0.92em; }
a { color: #2456b3; }
@media (prefers-color-scheme: dark) {
  body { color: #e6e8ee; background: #16181d; } th { background: #262b36; } th, td { border-color: #3a4150; }
  h2 { border-color: #3a4150; } blockquote { background: #332a10; } code { background: #262b36; } a { color: #8ab4ff; }
}
"""


def guidelines_html(md_text):
    """Turn guidelines.md into one self-contained web page (no internet needed to view it)."""
    import markdown  # pip install markdown (in requirements.txt)
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists", "nl2br"])
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Blue Cart Check: Annotation Guidelines</title>"
            f"<style>{GUIDELINES_CSS}</style></head><body>{body}</body></html>")


HOW_IT_WORKS_CSS = """
body { margin: 0; padding: 18px 16px 40px; background: #f6f1e4; color: #1f2430;
       font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
.bcc-w .go a { display: inline-block; background: #1565c0; color: #fff; text-decoration: none; border-radius: 12px;
               padding: 12px 30px; font-size: 1.1rem; font-weight: 700; }
.bcc-w .go a:hover { background: #0f4f99; }
"""


def how_it_works_html(welcome):
    """The welcome page again, as a plain web page the round help button can open in a new tab.

    Potato shows welcome.html only once (before the first photo). This copy keeps its text
    and styling, but the "Start labeling" form becomes a link back to the photos.
    """
    body = re.sub(r"<!--.*?-->", "", welcome, count=1, flags=re.S)                     # the note for developers
    body, n = re.subn(r'<form class="go".*?</form>',
                      '<p class="go"><a href="/annotate">Back to the photos <span class="fas fa-arrow-right"></span></a>'
                      '<small>This page is always one click away: the round <b>?</b> button at the bottom right.</small></p>',
                      body, flags=re.S)
    if n != 1:
        raise SystemExit("welcome.html: the 'Start labeling' form was not found; update how_it_works_html().")
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Blue Cart Check: How it works</title>"
            # the icons: Potato serves its own copy of Font Awesome (same file the tool pages use)
            "<link rel='stylesheet' href='/static/vendor/font-awesome-6.7.2/css/all.min.css'>"
            f"<style>{HOW_IT_WORKS_CSS}</style></head><body>{body}</body></html>")


def add_help_pages(media, with_video):
    """Write the pages the round help button opens into a tool's media/ folder.

    media/how_it_works.html   the welcome page again
    media/demo/index.html     docs/PROJECT_DEMO.html with its screenshots (docs/figures/tool_*)
    with_video=False leaves the 13 MB demo video out (zips for annotators stay small) and says so on the page.
    """
    media.mkdir(parents=True, exist_ok=True)
    welcome = (POTATO / "welcome.html").read_text(encoding="utf-8")
    (media / "how_it_works.html").write_text(how_it_works_html(welcome), encoding="utf-8")

    demo = REPO / "docs" / "PROJECT_DEMO.html"
    if not demo.exists():
        return
    page = demo.read_text(encoding="utf-8")
    (media / "demo" / "figures").mkdir(parents=True, exist_ok=True)
    figures = REPO / "docs" / "figures"
    for p in sorted(figures.glob("tool_*")) if figures.exists() else []:
        if p.suffix == ".webm" and not with_video:
            continue
        shutil.copy(p, media / "demo" / "figures" / p.name)
    if not with_video:
        page = re.sub(r"<video[^>]*tool_demo\.webm[^>]*>\s*</video>",
                      "<p><i>The 2-minute video is not in this pack, to keep the zip small. "
                      "It is <code>docs/figures/tool_demo.webm</code> in the project repository.</i></p>", page)
    (media / "demo" / "index.html").write_text(page, encoding="utf-8")


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

    guidelines_md = (REPO / "annotation" / "guidelines.md").read_text(encoding="utf-8")
    page = guidelines_html(guidelines_md)
    unfinished = "TEAM TODO" in guidelines_md or re.search(r"`<[^`>]+>`", guidelines_md)

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
        (pack / "media" / "guidelines.html").write_text(page, encoding="utf-8")
        add_help_pages(pack / "media", with_video=False)                 # pages behind the round help button
        shutil.copy(POTATO / "config.yaml", pack / "config.yaml")
        shutil.copy(POTATO / "welcome.html", pack / "welcome.html")     # the config's "phases" block needs it
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
    if unfinished:
        print("\nWARNING: annotation/guidelines.md still has a TEAM TODO box or <...> placeholders.\n"
              "         These packs are fine for our own testing, but finish the guidelines and\n"
              "         rebuild before sending packs to external annotators.")


if __name__ == "__main__":
    main()
