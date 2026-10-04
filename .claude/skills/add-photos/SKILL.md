---
name: add-photos
description: Ingest a teammate's batch of raw photos into the dataset safely (EXIF strip, resize, rename, manifest, checks). Use when new photos arrive in data/raw/.
---

Ingest new photos. Ask for anything missing: input folder under `data/raw/`, photographer name, category set, setting, and source/license if not team photos.

1. Do NOT open or display files in `data/raw/` (they contain GPS). Only count them: `ls data/raw/<folder> | wc -l`.
2. Check the filenames use the `object__state.jpg` convention for multi-state items; if not, warn that each photo will be its own item group and ask whether to continue.
3. Run `python scripts/prepare_images.py --input ... --photographer ... --category-set ... --setting ...` (plus `--source/--license/--source-url/--attribution` for non-team images). HEIC needs `pip install pillow-heif`.
4. Run `pytest -q` and `python scripts/dataset_stats.py`; report the new totals per category set and source.
5. Run `python scripts/explore_embeddings.py` and report any near-duplicate pairs.
6. Show the ids of 5 random new images so a human can spot-check them for faces/names.
7. Suggest a commit: `git add data/images data/manifest.csv data/attribution.csv && git commit -m "data: add N <category> photos (<name>)"`. Don't push without asking.
