---
name: phase1-check
description: Audit the repo against the ARI 410/510 Phase 1 requirements and report what is done, missing, or risky before the Oct 6 deadline.
---

Audit Blue Cart Check against Phase 1. Read `docs/REQUIREMENTS_PHASE1.md` first, then check each item below by **looking at files and running commands**, not by assuming.

1. **Dataset**: `data/manifest.csv` row count; every `image_path` exists; no `data/raw/` files are tracked (`git ls-files data/raw`); there's no label column in the manifest. Run `python scripts/dataset_stats.py`.
2. **Privacy**: sample 10 random images from `data/images/` and confirm `PIL.Image.open(p).info` has no `exif`. Report any filenames whose `notes` mention people or names.
3. **Licenses**: every manifest row with `source != team` has a matching row in `data/attribution.csv`; `LICENSE.md` exists.
4. **README**: count remaining `<...>` placeholders in `README.md`; check it has the per-item labeling time estimate, the collection dates, the sampling description and the missing-data note.
5. **Guidelines**: `annotation/guidelines.md` has all 5 required parts (overview, labels, rules, ≥1 example per label, contact). Count remaining `TODO`/`<...>`.
6. **Interface**: `annotation/potato/config.yaml` exists; packs build (`python scripts/make_annotation_packs.py` with sensible --agreement/--batch); `HOW_TO_ANNOTATE.md` states the output file and how to return it.
7. **Multiple annotations**: the agreement-set size and per-annotator batch are justified in README §6.
8. **Changes note**: `CHANGES_FROM_PROPOSAL.md` has no placeholders left.
9. **AI-use note**: `docs/AI_USE_LOG.md` exists and is current.
10. **Tests**: `pytest -q` passes.
11. **Non-repo items** (ask Khurram): Drive link shared with UM, Google Form submitted, Discord post with slides, presentation rehearsed (≤5 min).

Output a table: item | status (✅ / ⚠️ / ❌) | evidence | fix. End with the 3 most urgent fixes and who owns each (Khurram lead, Daud data, Hina annotation, Ian modeling).
