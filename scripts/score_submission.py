"""Score a submission file the way the Kaggle leaderboard will: macro-F1 over the four labels, on the Public rows,
the Private rows and all test rows. Also prints accuracy, per-class precision / recall / F1, recall on not_accepted
(the safety gate) and the confusion matrix.

    python scripts/score_submission.py deploy/kaggle/public/sample_submission.csv        # the majority baseline
    python scripts/score_submission.py my_predictions.csv --solution deploy/kaggle/private/solution.csv
    python scripts/score_submission.py llm_50.csv --partial      # a file that covers only some test ids (LLM baseline)

A submission is a CSV with the columns id and label, one row per test photo (same ids as test.csv).
"""
import argparse
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

REPO = Path(__file__).resolve().parents[1]
LABELS = ["accepted", "accepted_after_prep", "not_accepted", "cannot_determine"]
SHORT = {"accepted": "accepted", "accepted_after_prep": "after_prep", "not_accepted": "not_acc", "cannot_determine": "cannot"}


def macro_f1(truth, pred):
    return f1_score(truth, pred, labels=LABELS, average="macro", zero_division=0)


def score(solution, submission, partial=False):
    """Return a dict of scores; raises SystemExit on a malformed submission."""
    sub = pd.read_csv(submission, dtype=str).fillna("")
    for col in ("id", "label"):
        if col not in sub.columns:
            sys.exit(f"{submission}: no column '{col}' (columns: {list(sub.columns)})")
    bad = sorted(set(sub.label) - set(LABELS))
    if bad:
        sys.exit(f"{submission}: unknown labels {bad}; allowed: {LABELS}")
    if sub.id.duplicated().any():
        sys.exit(f"{submission}: duplicate ids " + ", ".join(sub.id[sub.id.duplicated()].head(5)))
    sub = sub[["id", "label"]]                      # extra columns (e.g. Usage when scoring the solution itself) are ignored
    sol = pd.read_csv(solution, dtype=str)
    extra = sorted(set(sub.id) - set(sol.id)); missing = sorted(set(sol.id) - set(sub.id))
    if extra:
        sys.exit(f"{submission}: ids that are not test photos: " + ", ".join(extra[:5]))
    if missing and not partial:
        sys.exit(f"{submission}: {len(missing)} test ids missing (first: {', '.join(missing[:5])}); pass --partial to score a subset")
    m = sol.merge(sub, on="id", suffixes=("_true", "_pred"))
    out = {"rows": len(m)}
    for name, part in (("Public", m[m.Usage == "Public"]), ("Private", m[m.Usage == "Private"]), ("All", m)):
        out[name] = macro_f1(part.label_true, part.label_pred) if len(part) else float("nan")
    out["accuracy"] = accuracy_score(m.label_true, m.label_pred)
    p, r, f, n = precision_recall_fscore_support(m.label_true, m.label_pred, labels=LABELS, zero_division=0)
    out["per_class"] = pd.DataFrame({"precision": p, "recall": r, "f1": f, "photos": n}, index=LABELS)
    out["recall_not_accepted"] = r[LABELS.index("not_accepted")]
    out["confusion"] = pd.DataFrame(confusion_matrix(m.label_true, m.label_pred, labels=LABELS), index=[f"true {l}" for l in LABELS], columns=[f"pred {SHORT[l]}" for l in LABELS])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("submission")
    ap.add_argument("--solution", default=str(REPO / "deploy" / "kaggle" / "private" / "solution.csv"))
    ap.add_argument("--partial", action="store_true", help="score only the ids present in the submission")
    args = ap.parse_args()
    s = score(args.solution, args.submission, args.partial)
    print(f"{Path(args.submission).name}: {s['rows']} test photos scored")
    print(f"  macro-F1  Public {s['Public']:.4f}   Private {s['Private']:.4f}   All {s['All']:.4f}")
    print(f"  accuracy {s['accuracy']:.4f}   recall on not_accepted {s['recall_not_accepted']:.4f}")
    print(s["per_class"].round(3).to_string()); print(s["confusion"].to_string())


if __name__ == "__main__":
    main()
