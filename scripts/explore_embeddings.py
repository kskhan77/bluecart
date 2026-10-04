"""
explore_embeddings.py: pre-annotation look at the dataset (Lecture 7: PCA + K-means).

For every image in data/manifest.csv:
  1. compute a feature vector
       --features color   (default, no GPU / no torch): 3x8-bin HSV color histogram
                           + 16x16 grayscale thumbnail (rough shape/texture)
       --features resnet  (better): ResNet-18 ImageNet embedding (needs torch + torchvision)
  2. standardize, then PCA to 2-D, and save a scatter colored by category_set
  3. K-means for k = 2..8 with inertia + silhouette (elbow + silhouette charts)
  4. list near-duplicate pairs (cosine similarity above --dup-threshold)

Outputs go to docs/figures/ and are meant for the slides and README.

Usage (from repo root):
  python scripts/explore_embeddings.py                      # quick, color features
  python scripts/explore_embeddings.py --features resnet    # after: pip install -r requirements-ml.txt
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

REPO = Path(__file__).resolve().parents[1]
FIG = REPO / "docs" / "figures"


def color_features(path):
    img = Image.open(path).convert("RGB")
    hsv = np.asarray(img.convert("HSV")).reshape(-1, 3)
    hist = np.concatenate([np.histogram(hsv[:, c], bins=8, range=(0, 255))[0] for c in range(3)]).astype(float)
    hist /= hist.sum()
    thumb = np.asarray(img.convert("L").resize((16, 16)), dtype=float).ravel() / 255.0
    return np.concatenate([hist, thumb])


def resnet_extractor():
    import torch
    from torchvision.models import resnet18, ResNet18_Weights

    weights = ResNet18_Weights.DEFAULT
    model = resnet18(weights=weights)
    model.fc = torch.nn.Identity()
    model.eval()
    prep = weights.transforms()

    def f(path):
        with torch.no_grad():
            x = prep(Image.open(path).convert("RGB")).unsqueeze(0)
            return model(x).squeeze(0).numpy()
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", choices=["color", "resnet"], default="color")
    ap.add_argument("--color-by", default="category_set")
    ap.add_argument("--dup-threshold", type=float, default=0.995)
    args = ap.parse_args()

    df = pd.read_csv(REPO / "data" / "manifest.csv")
    if len(df) < 10:
        raise SystemExit("Need at least 10 images in the manifest.")
    feat = color_features if args.features == "color" else resnet_extractor()
    X = np.stack([feat(REPO / "data" / p) for p in df["image_path"]])
    Xs = StandardScaler().fit_transform(X)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)

    # 1. PCA scatter
    pca = PCA(n_components=2, random_state=0)
    Z = pca.fit_transform(Xs)
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for name, g in df.groupby(args.color_by):
        ax.scatter(Z[g.index, 0], Z[g.index, 1], s=14, alpha=0.75, label=name)
    ev = pca.explained_variance_ratio_
    ax.set_xlabel(f"PC1 ({ev[0]:.0%} of variance)")
    ax.set_ylabel(f"PC2 ({ev[1]:.0%} of variance)")
    ax.set_title(f"Blue Cart Check: {len(df)} images, PCA of {args.features} features", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8, title=args.color_by)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / f"pca_{args.features}.png", dpi=200); plt.close(fig)

    # 2. K-means elbow + silhouette
    ks = list(range(2, min(9, len(df))))
    inertia, sil = [], []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xs)
        inertia.append(km.inertia_)
        sil.append(silhouette_score(Xs, km.labels_))
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    axes[0].plot(ks, inertia, marker="o"); axes[0].set_title("Elbow (inertia)", loc="left"); axes[0].set_xlabel("k")
    axes[1].plot(ks, sil, marker="o", color="#c05621"); axes[1].set_title("Silhouette", loc="left"); axes[1].set_xlabel("k")
    for a in axes:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / f"kmeans_{args.features}.png", dpi=200); plt.close(fig)

    # 3. near duplicates
    U = Xs / (np.linalg.norm(Xs, axis=1, keepdims=True) + 1e-9)
    S = U @ U.T
    iu = np.triu_indices(len(df), k=1)
    hits = [(df.id[i], df.id[j], S[i, j]) for i, j in zip(*iu) if S[i, j] >= args.dup_threshold]
    pd.DataFrame(hits, columns=["id_a", "id_b", "cosine"]).sort_values("cosine", ascending=False) \
        .to_csv(FIG / f"near_duplicates_{args.features}.csv", index=False)

    best_k = ks[int(np.argmax(sil))]
    print(f"PCA: PC1+PC2 explain {ev.sum():.0%} of variance -> {FIG / f'pca_{args.features}.png'}")
    print(f"K-means: best silhouette at k={best_k} ({max(sil):.2f}) -> {FIG / f'kmeans_{args.features}.png'}")
    print(f"Near-duplicate pairs (cos >= {args.dup_threshold}): {len(hits)} -> near_duplicates_{args.features}.csv")


if __name__ == "__main__":
    main()
