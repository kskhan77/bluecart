"""Phase 2a, step 1: compile the hosted tool's answers into one table, one row per photo and one column per person.

Reads the per-account state files of the hosted Potato (annotation_output/<account>/user_state.json), turns each
person's two answers (Step 1 kind, Step 2 state) into the final label with the same rule as compute_agreement.py,
merges accounts that belong to the same person, and writes:

  annotations_table.csv   one row per photo: photo_id, image, n_labels, then one column per person (final label)
  annotations_long.csv    one row per (photo, person): account, cart, condition, reason, final_label

Both files contain the labels of the photos that later become the hidden test set, so they go to a gitignored
folder (annotation/returned/ by default). Do not commit or post them.

    python scripts/compile_annotations.py                       # from deploy/local_server/annotation_output
    python scripts/compile_annotations.py --copy-to /mnt/c/Fall-2026/project   # also drop copies there
"""
import argparse
import collections
import csv
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# accounts that belong to the same person (people registered more than once)
ALIASES = {
    "Khurram Shafique": "Khurram Shafique", "kskhan77@gmail.com": "Khurram Shafique", "kskhan771@gmail.com": "Khurram Shafique",
    "slackta": "Ian Slackta", "Mmslackta": "Ian Slackta",
    "dauds@umich.edu": "Daud Jan", "miandaudjan12@gmail.com": "Daud Jan",
    "hinak@umich.edu": "Hina Kramer",
}


def derive_label(cart, condition):
    """The four final labels from the two answers (same rule as compute_agreement.py)."""
    if cart == "not_blue_cart":
        return "not_accepted"
    if cart == "cannot_tell":
        return "cannot_determine"
    if cart == "blue_cart":
        return {"ready": "accepted", "needs_prep": "accepted_after_prep",
                "ruined": "not_accepted", "cannot_tell": "cannot_determine"}.get(condition, "")
    return ""


def answers_of(entries):
    """Potato stores a list of [{"schema", "name"}, value] pairs per photo; a falsy value is a cleared answer."""
    picked = {}
    for e in entries:
        if isinstance(e, list) and len(e) == 2 and isinstance(e[0], dict) and e[1]:
            picked[e[0].get("schema")] = e[0].get("name")
    return picked


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--server", default=str(REPO / "deploy" / "local_server"), help="the hosted server folder (fetched from the VM)")
    ap.add_argument("--out", default=str(REPO / "annotation" / "returned"), help="where to write the two CSV files (gitignored)")
    ap.add_argument("--copy-to", default=None, help="also copy the two files to this folder (for example the Windows project folder)")
    args = ap.parse_args()
    server, out = Path(args.server), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    items = [json.loads(l) for l in (server / "data" / "items.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    long_rows = []
    for state_file in sorted((server / "annotation_output").glob("*/user_state.json")):
        account = state_file.parent.name
        person = ALIASES.get(account, account)
        state = json.loads(state_file.read_text(encoding="utf-8"))
        for photo_id, entries in (state.get("instance_id_to_label_to_value") or {}).items():
            a = answers_of(entries)
            final = derive_label(a.get("cart"), a.get("condition"))
            if final:
                long_rows.append({"photo_id": photo_id, "person": person, "account": account, "cart": a.get("cart", ""),
                                  "condition": a.get("condition", ""), "reason": a.get("reason", ""), "final_label": final})

    # one label per (photo, person): if the same person labeled a photo from two accounts, keep the first account's answer
    seen = {}
    for r in long_rows:
        seen.setdefault((r["photo_id"], r["person"]), r)
    long_rows = sorted(seen.values(), key=lambda r: (r["photo_id"], r["person"]))
    people = sorted({r["person"] for r in long_rows}, key=lambda p: (p not in set(ALIASES.values()), p.lower()))
    by_photo = collections.defaultdict(dict)
    for r in long_rows:
        by_photo[r["photo_id"]][r["person"]] = r["final_label"]

    wide = out / "annotations_table.csv"
    with wide.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["photo_id", "image", "n_labels"] + people)
        for it in items:
            labels = by_photo.get(it["id"], {})
            w.writerow([it["id"], it["image"], len(labels)] + [labels.get(p, "") for p in people])
    long_path = out / "annotations_long.csv"
    with long_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["photo_id", "person", "account", "cart", "condition", "reason", "final_label"])
        w.writeheader(); w.writerows(long_rows)

    accounts = sorted({r["account"] for r in long_rows})
    dist = collections.Counter(len(by_photo.get(it["id"], {})) for it in items)
    print(f"{wide}: {len(items)} photos x {len(people)} people  ({len(accounts)} accounts, duplicates merged)")
    print(f"{long_path}: {len(long_rows)} labels")
    print("labels per photo:", ", ".join(f"{n} labels: {c} photos" for n, c in sorted(dist.items())))
    print("people:", ", ".join(people))
    if args.copy_to:
        dest = Path(args.copy_to)
        if dest.is_dir():
            shutil.copy(wide, dest / wide.name); shutil.copy(long_path, dest / long_path.name)
            print(f"copies in {dest}")
        else:
            print(f"--copy-to: {dest} is not a folder, nothing copied")


if __name__ == "__main__":
    main()
