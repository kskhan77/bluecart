"""Phase 2a, step 3 (second half): turn the filled adjudication workbook(s) into one gold label per photo.

    python scripts/merge_adjudication.py                                   # annotation/returned/adjudication.xlsx
    python scripts/merge_adjudication.py --workbook a.xlsx b.xlsx c.xlsx   # one filled copy per team member
    python scripts/merge_adjudication.py --strict                          # exit 1 while any photo is unresolved

Rule per photo, in this order:
  1. a team_decision in any workbook wins (two different decisions for one photo = conflict, stays unresolved)
  2. otherwise the majority label (status unanimous or majority)
  3. a tie with no decision stays unresolved
Output: <returned>/gold_labels.csv with photo_id, label, source (team / majority / unanimous / unresolved), status,
note. exclude_photo is kept as a label so the split step can drop those photos. The file holds the labels of the
future hidden test set, so it stays in the gitignored annotation/returned folder.
"""
import argparse
import collections
import csv
import sys
from pathlib import Path

from openpyxl import load_workbook

REPO = Path(__file__).resolve().parents[1]
DECISIONS = {"accepted", "accepted_after_prep", "not_accepted", "cannot_determine", "exclude_photo"}


def read_decisions(path):
    """{photo_id: (status, majority_label, team_decision, note)} from the Decide sheet of one workbook."""
    ws = load_workbook(path, data_only=True, read_only=True)["Decide"]
    rows = ws.iter_rows(values_only=True)
    head = [str(h).strip() if h is not None else "" for h in next(rows)]
    col = {name: head.index(name) for name in ("photo_id", "status", "majority_label", "team_decision", "note")}
    out = {}
    for r in rows:
        if not r or r[col["photo_id"]] in (None, ""):
            continue
        get = lambda name: str(r[col[name]]).strip() if r[col[name]] is not None else ""
        out[get("photo_id")] = (get("status"), get("majority_label"), get("team_decision"), get("note"))
    return out


def merge(books):
    """books = {path: decisions dict}. Returns rows for gold_labels.csv and a list of problems."""
    photos = {}
    for path, dec in books.items():
        for pid, (status, majority, decision, note) in dec.items():
            p = photos.setdefault(pid, {"status": status, "majority": majority, "decisions": {}, "notes": []})
            if decision:
                p["decisions"][decision] = Path(path).name
            if note:
                p["notes"].append(note)
    rows, problems = [], []
    for pid in sorted(photos):
        p = photos[pid]; bad = [d for d in p["decisions"] if d not in DECISIONS]
        if bad:
            problems.append(f"{pid}: unknown decision {bad} (allowed: {sorted(DECISIONS)})")
        if len(p["decisions"]) > 1:
            problems.append(f"{pid}: conflicting decisions " + ", ".join(f"{d} ({f})" for d, f in p["decisions"].items()))
            label, source = "", "unresolved"
        elif len(p["decisions"]) == 1 and not bad:
            label, source = next(iter(p["decisions"])), "team"
        elif p["majority"] and p["status"] in ("unanimous", "majority"):
            label, source = p["majority"], p["status"]
        else:
            label, source = "", "unresolved"
        rows.append({"photo_id": pid, "label": label, "source": source, "status": p["status"], "note": " | ".join(p["notes"])})
    return rows, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workbook", nargs="+", default=None, help="filled workbook(s); default <returned>/adjudication.xlsx")
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"))
    ap.add_argument("--strict", action="store_true", help="exit 1 if any photo is unresolved or any decision is invalid")
    args = ap.parse_args()
    folder = Path(args.returned)
    paths = [Path(w) for w in args.workbook] if args.workbook else [folder / "adjudication.xlsx"]
    books = {str(p): read_decisions(p) for p in paths}
    rows, problems = merge(books)
    out = folder / "gold_labels.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["photo_id", "label", "source", "status", "note"]); w.writeheader(); w.writerows(rows)
    source = collections.Counter(r["source"] for r in rows); labels = collections.Counter(r["label"] for r in rows if r["label"])
    print(f"{out}: {len(rows)} photos from {len(paths)} workbook(s)")
    print("  decided by: " + ", ".join(f"{k} {v}" for k, v in source.most_common()))
    print("  labels: " + ", ".join(f"{k} {v}" for k, v in labels.most_common()))
    unresolved = [r["photo_id"] for r in rows if r["source"] == "unresolved"]
    if unresolved:
        print(f"  still unresolved ({len(unresolved)}): " + ", ".join(unresolved[:15]) + (" ..." if len(unresolved) > 15 else ""))
    for p in problems:
        print("  PROBLEM " + p)
    if args.strict and (unresolved or problems):
        sys.exit(1)


if __name__ == "__main__":
    main()
