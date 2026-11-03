"""Phase 2a, step 3: the Excel workbook the team uses to settle disagreements (adjudication).

Input, in annotation/returned/ (gitignored; made by compile_annotations.py and agreement_phase2.py):
  annotations_long.csv   one row per photo and person: Step 1, Step 2, reason, final label
  majority_labels.csv    one row per photo: majority label, votes, status (unanimous / majority / tie)
Output:
  annotation/returned/adjudication.xlsx   plus a copy in --copy-to (default C:\\Fall-2026\\project)

The "Decide" sheet has one row per photo: a thumbnail, a link to the full photo, who said what, the reasons that were
clicked, the majority label, and two cells for the team to fill: team_decision (a dropdown) and note. The photos that
need a human decision come first (ties, then majorities below two thirds) and are coloured; a suggested reviewer
splits them evenly between the four team members. "Read me" explains the job, "Summary" has the counts.

When the team has filled it in (one file, or one copy per person):
    python scripts/merge_adjudication.py --workbook <filled file(s)>

    python scripts/make_adjudication_workbook.py                 # default folders
    python scripts/make_adjudication_workbook.py --no-copy       # only the repo copy
"""
import argparse
import collections
import csv
import io
import shutil
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.utils.units import pixels_to_EMU
from openpyxl.worksheet.datavalidation import DataValidation
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
TEAM = ["Daud Jan", "Hina Kramer", "Ian Slackta", "Khurram Shafique"]
DECISIONS = ["accepted", "accepted_after_prep", "not_accepted", "cannot_determine", "exclude_photo"]
WEAK = 0.67                      # a majority below two thirds still needs a human look
THUMB = 100                      # thumbnail: longest side in pixels
PHOTO_URL = "https://raw.githubusercontent.com/kskhan77/bluecart/main/data/images/{pid}.jpg"
GUIDELINES_URL = "https://github.com/kskhan77/bluecart/blob/main/annotation/guidelines.md"

COLUMNS = [  # (header, width in characters)
    ("photo_id", 12), ("thumbnail", 16), ("full photo", 10), ("needs_decision", 9), ("status", 11), ("agreement", 10),
    ("majority_label", 20), ("votes", 34), *[(t, 19) for t in TEAM], ("other annotators", 40), ("reasons clicked", 28),
    ("reviewer", 17), ("team_decision", 21), ("note", 40)]
HEAD = [c for c, _ in COLUMNS]
C = {name: get_column_letter(i + 1) for i, name in enumerate(HEAD)}      # column letter by header

README = [
    ("Blue Cart Check: adjudication (Phase 2a, step 3)", True),
    ("", False),
    ("What this is: every photo was labeled by 3 to 6 people. Where they disagree, the team decides the final label. "
     "That decision becomes the ground truth for the leaderboard, so take the guidelines, not your memory, as the rule book: "
     + GUIDELINES_URL, False),
    ("", False),
    ("How to work on the Decide sheet", True),
    ("1. Filter the column needs_decision to YES (the coloured rows: red = tie, amber = weak majority). The other rows are "
     "already settled by a clear majority; you may still correct one if you spot a mistake.", False),
    ("2. The column reviewer suggests who takes which photo so the work splits evenly, about 48 photos each. "
     "Filter it to your name. If you want a second opinion, write that in note and leave team_decision empty.", False),
    ("3. Look at the thumbnail, or click 'open' to see the full photo. Read who said what and the reasons they clicked.", False),
    ("4. Pick the label in team_decision (dropdown). Use exclude_photo only when the photo cannot be used at all "
     "(more than one item, nothing recognisable, a duplicate). Add a short note when the choice was not obvious.", False),
    ("5. Save the file under the same name and send it back (Discord or Drive). Khurram merges all copies with "
     "scripts/merge_adjudication.py; a photo with two different decisions comes back to the group.", False),
    ("", False),
    ("Filter freely, but do NOT sort the sheet: the thumbnails are pictures that stay where they are when rows are "
     "sorted, so they would no longer match the photo_id next to them. The rows are already in priority order.", True),
    ("", False),
    ("The labels", True),
    ("accepted: the kind of item Flint takes in the blue cart and it is ready as it is (clean, empty, loose).", False),
    ("accepted_after_prep: accepted material, but it must be rinsed, emptied, flattened or taken out of a bag first.", False),
    ("not_accepted: never the blue cart (plastic bags, cups, styrofoam, greasy paper, electronics, ...), or an "
     "accepted material that is ruined.", False),
    ("cannot_determine: the photo does not show enough to decide (too dark, too far, the item is hidden).", False),
    ("exclude_photo: not a usable photo for the dataset at all. Say why in note.", False),
    ("", False),
    ("Columns: agreement is the share of annotators behind the majority label; votes lists every label with its count; "
     "the four team columns show each member's own label; other annotators lists the classmates' labels; "
     "reasons clicked are the optional reasons people chose.", False),
]


def thumbnail(path, size=THUMB):
    """Return (jpeg_bytes, width, height) of a thumbnail of the photo, or None if the file is missing."""
    if not path.exists():
        return None
    with Image.open(path) as im:
        im = im.convert("RGB"); im.thumbnail((size, size))
        buf = io.BytesIO(); im.save(buf, format="JPEG", quality=80)
        return buf.getvalue(), im.width, im.height


def load(folder):
    rows = list(csv.DictReader((folder / "annotations_long.csv").open(encoding="utf-8")))
    maj = {r["photo_id"]: r for r in csv.DictReader((folder / "majority_labels.csv").open(encoding="utf-8"))}
    per_photo = collections.defaultdict(list)
    for r in rows:
        per_photo[r["photo_id"]].append(r)
    return per_photo, maj


def decide_rows(per_photo, maj):
    """One dict per photo, in the order the sheet shows them: ties, weak majorities, majorities, unanimous."""
    def priority(m):
        if m["status"] == "tie":
            return 0
        if m["status"] == "majority":
            return 1 if float(m["share"]) < WEAK else 2
        return 3

    out = []
    for pid in sorted(maj, key=lambda p: (priority(maj[p]), p)):
        m = maj[pid]; labels = per_photo[pid]; share = float(m["share"])
        needs = m["status"] == "tie" or (m["status"] == "majority" and share < WEAK)
        by_person = {r["person"]: r["final_label"] for r in labels}
        others = "; ".join(f"{r['person']}: {r['final_label']}" for r in labels if r["person"] not in TEAM)
        reasons = collections.Counter(r["reason"] for r in labels if r["reason"])
        out.append({"photo_id": pid, "needs_decision": "YES" if needs else "", "status": m["status"], "agreement": share,
                    "majority_label": m["majority_label"], "votes": m["votes"].replace("=", " x"),
                    **{t: by_person.get(t, "") for t in TEAM}, "other annotators": others,
                    "reasons clicked": ", ".join(f"{k} x{v}" for k, v in reasons.most_common()),
                    "reviewer": "", "team_decision": "", "note": ""})
    i = 0
    for r in out:                                     # split the photos that need a decision evenly, in sheet order
        if r["needs_decision"]:
            r["reviewer"] = TEAM[i % len(TEAM)]; i += 1
    return out


def build(per_photo, maj, images, out_path):
    rows = decide_rows(per_photo, maj)
    wb = Workbook()
    ws = wb.active; ws.title = "Decide"
    bold = Font(bold=True); wrap = Alignment(wrap_text=True, vertical="top")
    for i, (name, width) in enumerate(COLUMNS, start=1):
        ws.cell(row=1, column=i, value=name).font = bold
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "D2"
    missing = 0
    for n, r in enumerate(rows, start=2):
        for i, name in enumerate(HEAD, start=1):
            if name in ("thumbnail", "full photo"):
                continue
            cell = ws.cell(row=n, column=i, value=r[name]); cell.alignment = wrap
        ws[f"{C['agreement']}{n}"].number_format = "0%"
        link = ws[f"{C['full photo']}{n}"]; link.value = "open"; link.hyperlink = PHOTO_URL.format(pid=r["photo_id"]); link.style = "Hyperlink"
        ws.row_dimensions[n].height = THUMB * 0.75 + 6
        thumb = thumbnail(images / f"{r['photo_id']}.jpg")
        if thumb is None:
            missing += 1; continue
        data, w, h = thumb
        img = XLImage(io.BytesIO(data))
        col = HEAD.index("thumbnail")
        img.anchor = TwoCellAnchor(editAs="twoCell",
                                   _from=AnchorMarker(col=col, colOff=pixels_to_EMU(4), row=n - 1, rowOff=pixels_to_EMU(4)),
                                   to=AnchorMarker(col=col, colOff=pixels_to_EMU(4 + w), row=n - 1, rowOff=pixels_to_EMU(4 + h)))
        ws.add_image(img)
    last = len(rows) + 1
    ws.auto_filter.ref = f"A1:{C['note']}{last}"
    dv = DataValidation(type="list", formula1='"' + ",".join(DECISIONS) + '"', allow_blank=True, showErrorMessage=True,
                        errorTitle="Not a label", error="Pick one of: " + ", ".join(DECISIONS))
    ws.add_data_validation(dv); dv.add(f"{C['team_decision']}2:{C['team_decision']}{last}")
    body = f"A2:{C['note']}{last}"
    ws.conditional_formatting.add(f"{C['team_decision']}2:{C['team_decision']}{last}",
                                  FormulaRule(formula=[f'${C["team_decision"]}2<>""'], fill=PatternFill("solid", start_color="C6EFCE", end_color="C6EFCE"), stopIfTrue=True))
    ws.conditional_formatting.add(body, FormulaRule(formula=[f'${C["status"]}2="tie"'], fill=PatternFill("solid", start_color="FFC7CE", end_color="FFC7CE"), stopIfTrue=True))
    ws.conditional_formatting.add(body, FormulaRule(formula=[f'${C["needs_decision"]}2="YES"'], fill=PatternFill("solid", start_color="FFEB9C", end_color="FFEB9C")))

    rd = wb.create_sheet("Read me"); rd.column_dimensions["A"].width = 120
    for i, (text, is_bold) in enumerate(README, start=1):
        cell = rd.cell(row=i, column=1, value=text); cell.alignment = Alignment(wrap_text=True, vertical="top")
        if is_bold:
            cell.font = bold

    sm = wb.create_sheet("Summary"); sm.column_dimensions["A"].width = 34; sm.column_dimensions["B"].width = 12
    status = collections.Counter(r["status"] for r in rows); needs = [r for r in rows if r["needs_decision"]]
    lines = [("photos", len(rows)), ("labels", sum(len(v) for v in per_photo.values())),
             ("people", len({r["person"] for v in per_photo.values() for r in v})),
             ("unanimous", status["unanimous"]), ("clear majority (2/3 or more)", status["majority"] - sum(1 for r in needs if r["status"] == "majority")),
             ("weak majority (needs a decision)", sum(1 for r in needs if r["status"] == "majority")), ("tie (needs a decision)", status["tie"]),
             ("photos that need a decision", len(needs)), ("", "")]
    lines += [(f"reviewer: {t}", sum(1 for r in needs if r["reviewer"] == t)) for t in TEAM] + [("", "")]
    lines += [("majority label so far (ties excluded)", "")] + [(k, v) for k, v in collections.Counter(r["majority_label"] for r in rows if r["majority_label"]).most_common()]
    for i, (k, v) in enumerate(lines, start=1):
        sm.cell(row=i, column=1, value=k); sm.cell(row=i, column=2, value=v)
    sm["A1"].font = bold
    wb.save(out_path)
    return rows, needs, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"))
    ap.add_argument("--images", default=str(REPO / "data" / "images"))
    ap.add_argument("--out", default=None, help="default: <returned>/adjudication.xlsx")
    ap.add_argument("--copy-to", default="/mnt/c/Fall-2026/project", help="folder for a second copy (Windows side)")
    ap.add_argument("--no-copy", action="store_true")
    args = ap.parse_args()
    folder = Path(args.returned); out = Path(args.out) if args.out else folder / "adjudication.xlsx"
    per_photo, maj = load(folder)
    rows, needs, missing = build(per_photo, maj, Path(args.images), out)
    print(f"{out}: {len(rows)} photos, {len(needs)} need a decision "
          f"({sum(1 for r in needs if r['status'] == 'tie')} ties, {sum(1 for r in needs if r['status'] == 'majority')} weak majorities), "
          f"{len(rows) - len(needs)} settled by a clear majority; {out.stat().st_size / 1e6:.1f} MB"
          + (f"; {missing} thumbnails missing" if missing else ""))
    for t in TEAM:
        print(f"  {t}: {sum(1 for r in needs if r['reviewer'] == t)} photos to decide")
    if not args.no_copy:
        dest = Path(args.copy_to)
        if dest.is_dir():
            shutil.copy(out, dest / "Blue_Cart_Check_adjudication.xlsx"); print(f"copied to {dest / 'Blue_Cart_Check_adjudication.xlsx'}")
        else:
            print(f"(no copy: {dest} is not a folder)")


if __name__ == "__main__":
    main()
