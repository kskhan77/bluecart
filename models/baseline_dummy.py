"""Dummy baselines (Phase 2a, step 6): majority label, random uniform, random by class share.

The handout asks for a random and a majority baseline and to keep whichever scores better. Three are tried:
  majority         every photo gets the most common training label ("accepted"); same as sample_submission.csv
  random_uniform   each of the four labels with probability 1/4            (seeded)
  random_by_share  each label with its training share                       (seeded)
All three are scored on the validation split and on the test set (the leaderboard's macro-F1), written as Kaggle
submissions to deploy/kaggle/submissions/ and logged in results/results.csv. The one with the best validation
macro-F1 is the dummy benchmark to submit on Kaggle.

    python models/baseline_dummy.py [--seed 42]
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import KAGGLE, LABELS, RESULTS, evaluate, load_split, log_result, report, score_submission, write_submission


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--kaggle", default=str(KAGGLE), help="folder with public/ and private/ (tests)")
    ap.add_argument("--results", default=str(RESULTS))
    args = ap.parse_args()
    kaggle, results = Path(args.kaggle), Path(args.results)
    train, val, test = load_split(kaggle)
    shares = train.label.value_counts().reindex(LABELS).fillna(0); shares = shares / shares.sum()
    majority = shares.idxmax()
    rng = np.random.default_rng(args.seed)
    makers = {
        "majority": lambda n: [majority] * n,
        "random_uniform": lambda n: list(rng.choice(LABELS, n)),
        "random_by_share": lambda n: list(rng.choice(LABELS, n, p=shares.values)),
    }
    best = None
    for name, make in makers.items():
        val_m = evaluate(val.label, make(len(val)))
        path = write_submission(name, test.id, make(len(test)), kaggle / "submissions")
        test_s = score_submission(path, kaggle / "private" / "solution.csv")
        notes = f"seed {args.seed}; training shares " + ", ".join(f"{k} {v:.2f}" for k, v in shares.items()) if name != "majority" else f"always '{majority}'"
        log_result(name, "none", "val", val_m, notes, results)
        log_result(name, "none", "test", {"macro_f1": test_s["All"], "recall_not_accepted": test_s["recall_not_accepted"], "accuracy": test_s["accuracy"]},
                   notes + f"; Public {test_s['Public']:.4f} Private {test_s['Private']:.4f}", results)
        report(name, val_m, test_s)
        if best is None or val_m["macro_f1"] > best[1]:
            best = (name, val_m["macro_f1"])
    print(f"\nbest dummy on validation: {best[0]} (macro-F1 {best[1]:.3f}); submit {kaggle / 'submissions' / best[0]}.csv as the dummy benchmark")


if __name__ == "__main__":
    main()
