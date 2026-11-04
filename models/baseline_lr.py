"""Trained baseline (Phase 2a, step 6): ImageNet ResNet-50 embeddings + logistic regression (the Lab 3 recipe).

1. Every photo -> a 2048-d vector from torchvision's ResNet-50 (IMAGENET1K_V2 weights, final layer removed), CPU,
   cached in models/cache/resnet50.npz so later runs take seconds.
2. StandardScaler + LogisticRegression(class_weight="balanced"); C chosen on the validation split by macro-F1
   (the test set is never used for choices), then refit on train + val.
3. Test predictions -> deploy/kaggle/submissions/lr_resnet50.csv, scored like the leaderboard, logged in results/results.csv.

    python models/baseline_lr.py                 # first run downloads the weights (~100 MB) and embeds 617 photos (~2 min CPU)
    python models/baseline_lr.py --refresh       # recompute the embeddings
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import KAGGLE, REPO, RESULTS, evaluate, load_split, log_result, report, score_submission, write_submission

CACHE = REPO / "models" / "cache" / "resnet50.npz"
CS = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0]


def embed(paths, batch=32):
    """ResNet-50 penultimate-layer features for a list of image paths (CPU)."""
    import torch
    from PIL import Image
    from torchvision.models import ResNet50_Weights, resnet50
    weights = ResNet50_Weights.IMAGENET1K_V2
    model = resnet50(weights=weights); model.fc = torch.nn.Identity(); model.eval()
    prep = weights.transforms()
    out = []
    with torch.no_grad():
        for i in range(0, len(paths), batch):
            x = torch.stack([prep(Image.open(p).convert("RGB")) for p in paths[i:i + batch]])
            out.append(model(x).numpy())
            print(f"  embedded {min(i + batch, len(paths))}/{len(paths)}", end="\r")
    print()
    return np.concatenate(out)


def features(ids, images, refresh=False):
    """Embeddings for the given ids, from the cache when every id is there."""
    if CACHE.exists() and not refresh:
        z = np.load(CACHE, allow_pickle=False); have = dict(zip(z["ids"], z["X"]))
        if all(i in have for i in ids):
            return np.stack([have[i] for i in ids])
    X = embed([images / f"{i}.jpg" for i in ids])
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE, ids=np.array(list(ids)), X=X)
    return X


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--kaggle", default=str(KAGGLE))
    ap.add_argument("--results", default=str(RESULTS))
    args = ap.parse_args()
    kaggle, results = Path(args.kaggle), Path(args.results)
    train, val, test = load_split(kaggle)
    ids = list(train.id) + list(val.id) + list(test.id)
    X = features(ids, kaggle / "public" / "images", args.refresh)
    Xtr, Xva, Xte = X[:len(train)], X[len(train):len(train) + len(val)], X[len(train) + len(val):]

    scores = {}
    for C in CS:
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=C, class_weight="balanced", max_iter=5000))
        clf.fit(Xtr, train.label)
        scores[C] = evaluate(val.label, clf.predict(Xva))
        print(f"  C={C:<5} val macro-F1 {scores[C]['macro_f1']:.3f}")
    best_C = max(scores, key=lambda c: scores[c]["macro_f1"])
    val_m = scores[best_C]

    final = make_pipeline(StandardScaler(), LogisticRegression(C=best_C, class_weight="balanced", max_iter=5000))
    final.fit(np.concatenate([Xtr, Xva]), pd.concat([train.label, val.label]))
    path = write_submission("lr_resnet50", test.id, final.predict(Xte), kaggle / "submissions")
    test_s = score_submission(path, kaggle / "private" / "solution.csv")
    notes = f"ResNet-50 IMAGENET1K_V2 features, StandardScaler, class_weight=balanced, C={best_C} chosen on val, refit on train+val"
    log_result("logistic_regression", "resnet50", "val", val_m, notes, results)
    log_result("logistic_regression", "resnet50", "test", {"macro_f1": test_s["All"], "recall_not_accepted": test_s["recall_not_accepted"], "accuracy": test_s["accuracy"]},
               notes + f"; Public {test_s['Public']:.4f} Private {test_s['Private']:.4f}", results)
    report(f"logistic regression on ResNet-50 features (C={best_C})", val_m, test_s)
    print(test_s["per_class"].round(3).to_string()); print(test_s["confusion"].to_string())


if __name__ == "__main__":
    main()
