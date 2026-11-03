"""Phase 2a, steps 2 and 3 (first half): agreement between annotators, and a majority label with a dispute list.

Input:  annotation/returned/annotations_long.csv  (from scripts/compile_annotations.py; one row per photo and person)
Output (same gitignored folder, they contain labels of the future hidden test set):
  agreement_report.md    the numbers for the slides: Krippendorff's alpha, percent agreement, per-person agreement
  majority_labels.csv    one row per photo: majority label, votes, status (unanimous / majority / tie) for adjudication

Why these metrics: Krippendorff's alpha is the one the handout recommends when every photo is seen by a different
subset of people and the number of annotators per photo varies (ours: 3 to 6). Percent agreement is reported next
to it, as the handout asks, but alpha is the chance-corrected number to quote. Cohen's kappa is given pairwise for
the team members, who share the most photos.

    python scripts/agreement_phase2.py
"""
import argparse
import collections
import csv
import itertools
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LABELS = ["accepted", "accepted_after_prep", "not_accepted", "cannot_determine"]
STEP1 = ["blue_cart", "not_blue_cart", "cannot_tell"]
TEAM = ["Khurram Shafique", "Daud Jan", "Hina Kramer", "Ian Slackta"]


def krippendorff_alpha(units, categories):
    """Nominal Krippendorff's alpha. units = list of lists of category values (one list per photo, >= 2 values)."""
    units = [u for u in units if len(u) >= 2]
    n = sum(len(u) for u in units)
    if n == 0:
        return float("nan")
    totals = collections.Counter(v for u in units for v in u)
    observed = sum(sum(1 for a, b in itertools.permutations(u, 2) if a != b) / (len(u) - 1) for u in units) / n
    expected = sum(totals[a] * totals[b] for a in categories for b in categories if a != b) / (n * (n - 1))
    return 1 - observed / expected if expected else float("nan")


def percent_agreement(units):
    pairs = agree = 0
    for u in units:
        for a, b in itertools.combinations(u, 2):
            pairs += 1; agree += (a == b)
    return 100 * agree / pairs if pairs else float("nan"), pairs


def cohen_kappa(pairs):
    """pairs = list of (label_a, label_b) for photos both people labeled."""
    if len(pairs) < 2:
        return float("nan")
    n = len(pairs); po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"))
    args = ap.parse_args()
    folder = Path(args.returned)
    rows = list(csv.DictReader((folder / "annotations_long.csv").open(encoding="utf-8")))
    by_photo = collections.defaultdict(dict); step1 = collections.defaultdict(dict)
    for r in rows:
        by_photo[r["photo_id"]][r["person"]] = r["final_label"]; step1[r["photo_id"]][r["person"]] = r["cart"]
    photos = sorted(by_photo); people = sorted({r["person"] for r in rows})
    shared = [p for p in photos if len(by_photo[p]) >= 6]        # the 30 photos everyone on the first round saw

    units = [list(by_photo[p].values()) for p in photos]
    alpha_label = krippendorff_alpha(units, LABELS)
    alpha_step1 = krippendorff_alpha([list(step1[p].values()) for p in photos], STEP1)
    alpha_binary = krippendorff_alpha([["blue" if v.startswith("accepted") else v for v in u] for u in units], ["blue", "not_accepted", "cannot_determine"])
    pct, n_pairs = percent_agreement(units)
    alpha_shared = krippendorff_alpha([list(by_photo[p].values()) for p in shared], LABELS)
    pct_shared, _ = percent_agreement([list(by_photo[p].values()) for p in shared])

    # majority label and dispute list
    maj_rows = []; status_count = collections.Counter(); confusions = collections.Counter()
    for p in photos:
        votes = collections.Counter(by_photo[p].values()); top = votes.most_common()
        if len(top) == 1:
            status, label = "unanimous", top[0][0]
        elif top[0][1] > top[1][1]:
            status, label = "majority", top[0][0]
        else:
            status, label = "tie", ""
        status_count[status] += 1
        maj_rows.append({"photo_id": p, "n_labels": len(by_photo[p]), "majority_label": label, "status": status,
                         "share": f"{top[0][1] / len(by_photo[p]):.2f}", "votes": "; ".join(f"{k}={v}" for k, v in top),
                         "team_decision": ""})
        for a, b in itertools.combinations(sorted(by_photo[p].values()), 2):
            if a != b:
                confusions[(a, b)] += 1
    with (folder / "majority_labels.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(maj_rows[0].keys())); w.writeheader(); w.writerows(maj_rows)

    # per person: labels given, agreement with the majority of the OTHER people on the photos they labeled
    person_rows = []
    for person in people:
        mine = [(p, by_photo[p][person]) for p in photos if person in by_photo[p]]
        hits = total = 0
        for p, lab in mine:
            others = collections.Counter(v for q, v in by_photo[p].items() if q != person)
            if not others:
                continue
            top = others.most_common()
            if len(top) > 1 and top[0][1] == top[1][1]:
                continue                                     # the others are tied, no verdict
            total += 1; hits += (lab == top[0][0])
        dist = collections.Counter(lab for _, lab in mine)
        person_rows.append((person, len(mine), 100 * hits / total if total else float("nan"),
                            100 * dist["cannot_determine"] / len(mine), 100 * dist["accepted_after_prep"] / len(mine)))
    person_rows.sort(key=lambda r: -r[2])

    team_kappa = []
    for a, b in itertools.combinations(TEAM, 2):
        pairs = [(by_photo[p][a], by_photo[p][b]) for p in photos if a in by_photo[p] and b in by_photo[p]]
        if len(pairs) >= 10:
            team_kappa.append((a, b, len(pairs), cohen_kappa(pairs)))

    lines = ["# Agreement between annotators (Phase 2a, step 2)", "",
             f"{len(rows)} labels, {len(photos)} photos, {len(people)} people; every photo has {min(len(v) for v in by_photo.values())} to {max(len(v) for v in by_photo.values())} labels.", "",
             "| measure | value |", "|---|---|",
             f"| Krippendorff's alpha, final label (4 classes) | {alpha_label:.2f} |",
             f"| Krippendorff's alpha, blue cart item or not (accepted+prep vs never vs cannot) | {alpha_binary:.2f} |",
             f"| Krippendorff's alpha, Step 1 answer only | {alpha_step1:.2f} |",
             f"| percent agreement, final label (all {n_pairs} pairs of people on a photo) | {pct:.1f}% |",
             f"| shared photos ({len(shared)}, seen by {max(len(by_photo[p]) for p in shared) if shared else 0} people): alpha / percent | {alpha_shared:.2f} / {pct_shared:.1f}% |", "",
             f"Majority vote: {status_count['unanimous']} photos unanimous, {status_count['majority']} with a clear majority, {status_count['tie']} ties to adjudicate (majority_labels.csv).", "",
             "Most common disagreements (pairs of labels on the same photo):", ""]
    lines += [f"- {a} vs {b}: {n}" for (a, b), n in confusions.most_common(5)]
    lines += ["", "Per person: labels given, agreement with the majority of the other people on the same photos, and how often they chose the two rare labels.", "",
              "| person | labels | agrees with others | cannot_determine | accepted_after_prep |", "|---|---|---|---|---|"]
    lines += [f"| {p} | {n} | {ag:.0f}% | {cd:.0f}% | {ap_:.0f}% |" for p, n, ag, cd, ap_ in person_rows]
    if team_kappa:
        lines += ["", "Cohen's kappa between team members (photos both labeled):", ""] + [f"- {a} vs {b}: {k:.2f} on {n} photos" for a, b, n, k in team_kappa]
    lines += ["", "Reading the numbers: alpha above 0.8 is reliable, 0.67 to 0.8 is tentative, below 0.67 means the labels need adjudication before they are used as ground truth."]
    (folder / "agreement_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
