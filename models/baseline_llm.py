"""LLM baseline (Phase 2a, step 6): a frontier LLM labels test photos zero-shot; this script gathers and scores the answers.

How the answers were produced (reported in docs/BASELINES.md): the exact prompt is models/llm_prompt.txt (rules only,
no labeled examples). The test photos were sent in batches of about 20 to fresh instances of Claude (Claude Fable 5.1
through the Claude Agent SDK), each instance seeing only the prompt and its photos, one image at a time, and
answering one "<id>,<label>" line per photo. Each batch's answers are one CSV (id,label) in the parts folder.

    python models/baseline_llm.py                                   # deploy/kaggle/submissions/llm_parts/*.csv
    python models/baseline_llm.py --parts <folder> --name llm_gemini --model "Gemini 2.5 Flash, free chat"

Gathers the parts into deploy/kaggle/submissions/<name>.csv, scores it like the leaderboard (with --partial if it
does not cover every test photo) and logs results/results.csv.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import KAGGLE, LABELS, RESULTS, load_split, log_result, score_submission, write_submission


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parts", default=None, help="folder of answer CSVs; default <kaggle>/submissions/llm_parts")
    ap.add_argument("--name", default="llm_claude")
    ap.add_argument("--model", default="Claude Fable 5.1 (Claude Agent SDK), zero-shot, prompt models/llm_prompt.txt, ~20 photos per fresh instance")
    ap.add_argument("--kaggle", default=str(KAGGLE))
    ap.add_argument("--results", default=str(RESULTS))
    args = ap.parse_args()
    kaggle, results = Path(args.kaggle), Path(args.results)
    parts = sorted(Path(args.parts or kaggle / "submissions" / "llm_parts").glob("*.csv"))
    if not parts:
        sys.exit(f"no part files in {args.parts}")
    ans = pd.concat([pd.read_csv(p, dtype=str) for p in parts], ignore_index=True)
    ans.columns = [c.strip().lower() for c in ans.columns]
    ans["id"] = ans["id"].str.strip(); ans["label"] = ans["label"].str.strip().str.lower()
    bad = ans[~ans.label.isin(LABELS)]
    if len(bad):
        print(f"WARNING {len(bad)} answers are not a valid label and are dropped: " + "; ".join(f"{r.id}={r.label}" for r in bad.itertuples()))
        ans = ans[ans.label.isin(LABELS)]
    dup = ans[ans.id.duplicated(keep=False)]
    if len(dup):
        print(f"WARNING {dup.id.nunique()} photos answered more than once; first answer kept")
        ans = ans.drop_duplicates("id")
    _, _, test = load_split(kaggle)
    ans = ans[ans.id.isin(test.id)]
    path = write_submission(args.name, ans.id, ans.label, kaggle / "submissions")
    partial = len(ans) < len(test)
    s = score_submission(path, kaggle / "private" / "solution.csv", partial=partial)
    notes = args.model + f"; {len(ans)} of {len(test)} test photos" + ("" if not partial else " (partial, not for the leaderboard)")
    log_result(args.name, "pixels (zero-shot)", "test", {"macro_f1": s["All"], "recall_not_accepted": s["recall_not_accepted"], "accuracy": s["accuracy"]},
               notes + f"; Public {s['Public']:.4f} Private {s['Private']:.4f}", results)
    print(f"{args.name}: {len(ans)} of {len(test)} test photos answered from {len(parts)} part file(s)"
          + (f"; {s['undecided_skipped']} skipped (label not adjudicated yet)" if s.get("undecided_skipped") else ""))
    print(f"  test  macro-F1 Public {s['Public']:.3f}  Private {s['Private']:.3f}  All {s['All']:.3f}   recall(not_accepted) {s['recall_not_accepted']:.3f}   accuracy {s['accuracy']:.3f}")
    print(s["per_class"].round(3).to_string()); print(s["confusion"].to_string())
    print("answer shares: " + ", ".join(f"{k} {v}" for k, v in ans.label.value_counts().items()))


if __name__ == "__main__":
    main()
