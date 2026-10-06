"""
assign_sets.py: divide the open-dataset photos between the four team members' sets.

Every team member owns one group of items (proposal): Daud containers, Hina paper and
cardboard, Khurram campus disposables, Ian the "never" and hard cases. Photos a member
took are in their set by definition. Photos from the open datasets (RealWaste, the Kaggle
drinking-waste set, Wikimedia Commons) are ASSIGNED to a set here, by the kind of item,
so that each person knows which photos they are responsible for.

The assignment is written into the `notes` column of data/manifest.csv as
"assigned to <Name>'s set". Nothing else changes: the original author stays in
`attribution` and in data/attribution.csv (hard rule 4 in CLAUDE.md).

Usage (from the repo root):
    python scripts/assign_sets.py                                   # defaults below
    python scripts/assign_sets.py --ian 142 --hina 115 --daud 175 --khurram 185
    python scripts/assign_sets.py --dry-run                          # only print the result

The targets must add up to the number of photos in the manifest. The kinds are read
from the original file names kept in data/attribution.csv (RealWaste folder names such
as "Cardboard", Kaggle class prefixes such as "PET").
"""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "data" / "manifest.csv"
ATTRIBUTION = REPO / "data" / "attribution.csv"

FULL_NAME = {"daud": "Daud Jan", "hina": "Hina Kramer", "khurram": "Khurram Shafique", "ian": "Ian Slackta"}

# Which kinds each person takes, in order of preference. A person fills up to their target
# from the first kind, then the next, and so on. The last person takes whatever is left.
PREFERENCES = {
    "hina": ["realwaste:Cardboard", "realwaste:Paper"],
    "ian": ["realwaste:Miscellaneous Trash", "realwaste:Textile Trash", "realwaste:Vegetation",
            "realwaste:Food Organics", "realwaste:Plastic"],
    "daud": ["wikimedia:*", "realwaste:Glass", "realwaste:Metal", "kaggle_drinking_waste:Glass",
             "kaggle_drinking_waste:AluCan", "realwaste:Plastic"],
    "khurram": ["kaggle_drinking_waste:PET", "kaggle_drinking_waste:HDPEM", "kaggle_drinking_waste:AluCan",
                "realwaste:Plastic", "realwaste:Paper", "*"],
}
ORDER = ["hina", "ian", "daud", "khurram"]


def kind_of(source, title):
    """'realwaste:Cardboard', 'kaggle_drinking_waste:PET', 'wikimedia:*' from the original file name."""
    if source == "realwaste":
        return "realwaste:" + title.split("/")[-1].split("_")[0]
    if source == "kaggle_drinking_waste":
        return "kaggle_drinking_waste:" + re.match(r"[A-Za-z]+", title.split("/")[-1]).group(0)
    return source + ":*"


def assign(rows, credits, targets):
    """Return {id: person} for the sourced photos, or raise SystemExit when the targets cannot be met."""
    own = Counter(r["attribution"].split()[0].lower() for r in rows if r["source"] == "team")
    pool = defaultdict(list)                                   # kind -> ids, in a fixed order
    for r in sorted(rows, key=lambda r: r["id"]):
        if r["source"] != "team":
            pool[kind_of(r["source"], credits[r["id"]]["title"])].append(r["id"])

    result = {}
    for person in ORDER:
        need = targets[person] - own.get(person, 0)
        if need < 0:
            raise SystemExit(f"{FULL_NAME[person]} already has {own[person]} own photos, more than the target {targets[person]}.")
        for pref in PREFERENCES[person]:
            kinds = list(pool) if pref == "*" else [k for k in pool if k == pref or (pref.endswith(":*") and k.startswith(pref[:-1]))]
            for k in kinds:
                while need and pool[k]:
                    result[pool[k].pop(0)] = person
                    need -= 1
        if need:
            raise SystemExit(f"Not enough photos of the kinds {FULL_NAME[person]} takes: {need} short of the target {targets[person]}. "
                             f"Lower --{person} or widen PREFERENCES.")
    left = sum(len(v) for v in pool.values())
    if left:
        raise SystemExit(f"{left} photos were not assigned: the targets add up to less than the dataset.")
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--daud", type=int, default=175)
    ap.add_argument("--hina", type=int, default=115)
    ap.add_argument("--khurram", type=int, default=185)
    ap.add_argument("--ian", type=int, default=142)
    ap.add_argument("--dry-run", action="store_true", help="print the result, do not write the manifest")
    args = ap.parse_args()
    targets = {"daud": args.daud, "hina": args.hina, "khurram": args.khurram, "ian": args.ian}

    with MANIFEST.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows, fields = list(reader), reader.fieldnames
    with ATTRIBUTION.open(newline="", encoding="utf-8") as f:
        credits = {r["id"]: r for r in csv.DictReader(f)}
    if sum(targets.values()) != len(rows):
        raise SystemExit(f"The targets add up to {sum(targets.values())} but the manifest has {len(rows)} photos.")

    result = assign(rows, credits, targets)
    changed = 0
    for r in rows:
        if r["id"] in result:
            new = f"assigned to {FULL_NAME[result[r['id']]]}'s set"
            notes, n = re.subn(r"assigned to [^;]+'s set", new, r["notes"])
            if n == 0:
                notes = (notes + "; " if notes else "") + new
            if notes != r["notes"]:
                r["notes"] = notes
                changed += 1

    # summary: per person, how many photos and of which kinds
    sets = defaultdict(Counter)
    for r in rows:
        person = result.get(r["id"]) or r["attribution"].split()[0].lower()
        kind = "own photos" if r["source"] == "team" else kind_of(r["source"], credits[r["id"]]["title"])
        sets[person][kind] += 1
    for person in ["daud", "hina", "khurram", "ian"]:
        total = sum(sets[person].values())
        kinds = ", ".join(f"{k} {n}" for k, n in sets[person].most_common())
        print(f"{FULL_NAME[person]:18s} {total:4d}   {kinds}")
    print(f"{'total':18s} {len(rows):4d}   ({changed} notes changed)")

    if args.dry_run:
        print("dry run: manifest not written")
        return
    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"written: {MANIFEST.relative_to(REPO)}")


if __name__ == "__main__":
    main()
