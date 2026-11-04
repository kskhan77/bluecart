"""Shared helpers for the baseline scripts in models/: load the split, write a submission, score it, log the result.

Every baseline writes its test predictions as a Kaggle submission (deploy/kaggle/submissions/<name>.csv), scores it
with scripts/score_submission.py (the leaderboard's macro-F1 on the Public, Private and all test rows) and appends
one row per split to results/results.csv: model, features, split, macro_f1, recall_not_accepted, accuracy, date, notes.
"""
import csv
import datetime
import importlib.util
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score

REPO = Path(__file__).resolve().parents[1]
KAGGLE = REPO / "deploy" / "kaggle"
SUBMISSIONS = KAGGLE / "submissions"
RESULTS = REPO / "results" / "results.csv"
LABELS = ["accepted", "accepted_after_prep", "not_accepted", "cannot_determine"]


def load_split(kaggle=KAGGLE):
    """train, val, test DataFrames (id, image, label for train/val) from the Kaggle public folder."""
    tv = pd.read_csv(kaggle / "public" / "train.csv", dtype=str)
    test = pd.read_csv(kaggle / "public" / "test.csv", dtype=str)
    pending = int((~tv.label.isin(LABELS)).sum())
    if pending:                                   # preview files: ties not adjudicated yet carry "undecided"
        print(f"  ({pending} train/val photos skipped: label not adjudicated yet, preview run)")
        tv = tv[tv.label.isin(LABELS)]
    return tv[tv.split == "train"].reset_index(drop=True), tv[tv.split == "val"].reset_index(drop=True), test


def evaluate(y_true, y_pred):
    """macro-F1, recall on not_accepted, accuracy."""
    return {"macro_f1": f1_score(y_true, y_pred, labels=LABELS, average="macro", zero_division=0),
            "recall_not_accepted": recall_score(y_true, y_pred, labels=["not_accepted"], average="macro", zero_division=0),
            "accuracy": accuracy_score(y_true, y_pred)}


def write_submission(name, ids, labels, folder=SUBMISSIONS):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.csv"
    pd.DataFrame({"id": list(ids), "label": list(labels)}).to_csv(path, index=False)
    return path


def score_submission(path, solution=KAGGLE / "private" / "solution.csv", partial=False):
    """Run scripts/score_submission.py's scorer on a submission file; returns its dict (Public, Private, All, ...)."""
    spec = importlib.util.spec_from_file_location("score_submission", REPO / "scripts" / "score_submission.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.score(solution, path, partial=partial)


def log_result(model, features, split, metrics, notes="", results=RESULTS):
    """Append one row to results/results.csv (header written once)."""
    results.parent.mkdir(parents=True, exist_ok=True)
    new = not results.exists()
    with results.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["model", "features", "split", "macro_f1", "recall_not_accepted", "accuracy", "date", "notes"])
        w.writerow([model, features, split, f"{metrics['macro_f1']:.4f}", f"{metrics['recall_not_accepted']:.4f}",
                    f"{metrics['accuracy']:.4f}", datetime.date.today().isoformat(), notes])


def report(name, val_metrics, test_scores):
    """One readable block per baseline."""
    print(f"{name}")
    print(f"  val   macro-F1 {val_metrics['macro_f1']:.3f}   recall(not_accepted) {val_metrics['recall_not_accepted']:.3f}   accuracy {val_metrics['accuracy']:.3f}")
    print(f"  test  macro-F1 Public {test_scores['Public']:.3f}  Private {test_scores['Private']:.3f}  All {test_scores['All']:.3f}"
          f"   recall(not_accepted) {test_scores['recall_not_accepted']:.3f}   accuracy {test_scores['accuracy']:.3f}"
          + (f"   ({test_scores['undecided_skipped']} test photos skipped, label not adjudicated yet)" if test_scores.get("undecided_skipped") else ""))
