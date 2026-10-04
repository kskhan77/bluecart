---
name: presentation-stats
description: Produce the numbers and figures for the Phase 1 class presentation (dataset description stats, per-item labeling time, annotation plan sizing).
---

Gather everything slide 4 ("dataset") and slide 7 ("the ask") need.

1. `python scripts/dataset_stats.py` → total images, team vs. sourced, per category set, per setting, image size, date range. Charts land in `docs/`.
2. `python scripts/explore_embeddings.py` (and `--features resnet` if torch is installed) → `docs/figures/pca_*.png`, `kmeans_*.png`. Explain in 1 sentence what the PCA plot shows (do category sets/photographers cluster separately? = possible photographer bias).
3. Per-item labeling time: if pilot outputs exist under `annotation/returned/internal_*`, read Potato's `user_state.json` behavioral data (`instance_id_to_behavioral_data` → session_start/session_end) and compute the median seconds per item; otherwise ask Khurram for the timed pilot result.
4. Annotation plan: rate R = 3600 / median_seconds × 0.85. Suggest agreement set A ≈ R/3 and batch B ≈ R − A, total ≈ A + 6B. Show the trade-off in one line.
5. Output a markdown block with the slide-ready numbers + figure paths, and update the `<...>` placeholders in README §2, §5, §6 only after Khurram confirms.
