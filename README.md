# Blue Cart Check: Dataset (ARI 410/510, Group 2, UM-Flint, Fall 2026)

**Task:** given one phone photo of an everyday item, decide whether it goes in Flint's blue recycling cart under the City of Flint curbside rules (Priority Waste).
**Labels (assigned by annotators, not included at collection time):** `accepted` · `accepted_after_prep` · `not_accepted` · `cannot_determine`

**Team:** Daud Jan · Hina Kramer · Khurram Shafique · Ian Slackta
**Dataset link (UM access):** `<GOOGLE DRIVE LINK>`
**License:** CC BY 4.0 (see `LICENSE.md`)

> TEAM TODO: fill every `<...>` after the final `python scripts/dataset_stats.py` run.

---

## 1. What one instance is
One instance = **one JPEG photo of a single everyday item** (or a small group of items when the point is that they are bagged together), shown the way a person would see it just before choosing a bin. Every image has one row in `data/manifest.csv`.

## 2. Size and composition
| | Count |
|---|---|
| Total images | `<N>` |
| Team-photographed | `<n>` (`<%>`) |
| Openly licensed (Wikimedia / Openverse / Open Images) | `<n>` (`<%>`) |
| Category sets: containers / paper / disposables / hard | `<a>` / `<b>` / `<c>` / `<d>` |
| Collection dates | `<start>` to `<end>` |

## 3. Files and format
```
data/
  images/bcc_00001.jpg ...   all images: JPEG, RGB, long edge 512 px, no metadata
  manifest.csv               one row per image (columns below)
  attribution.csv            source URL / author / license for every sourced image
annotation/
  guidelines.md              annotation guidelines (v1.0)
  HOW_TO_ANNOTATE.md         annotator setup instructions
  potato/config.yaml         Potato annotation tool config
scripts/
  prepare_images.py          EXIF strip + resize + rename + manifest
  dataset_stats.py           descriptive stats + charts
  make_annotation_packs.py   agreement set + per-annotator packs
  explore_embeddings.py      PCA / k-means / near-duplicate check
  compute_agreement.py       Phase 2: Fleiss kappa, Krippendorff alpha, majority labels
  make_splits.py             group-safe train/val/test split
```

**`manifest.csv` columns**
| Column | Meaning |
|---|---|
| `id` | image ID, `bcc_00001` ... |
| `image_path` | path relative to `data/` |
| `width`, `height` | pixels after resizing |
| `source` | `team`, `wikimedia`, `openverse`, `openimages` |
| `source_url` | original URL (sourced images only) |
| `license` | `CC-BY-4.0` (team) or the source image's license (`CC0-1.0` / `CC-BY-x.x`) |
| `attribution` | photographer (team) or original author |
| `capture_date` | date taken (team) or downloaded (sourced) |
| `setting` | `kitchen`, `office`, `bin_station`, `outdoor`, `dining`, `other` |
| `category_set` | which collection set it belongs to (`containers`, `paper`, `disposables`, `hard`) |
| `item_count` | number of items in the photo |
| `item_group_id` | same physical object photographed in several states (e.g. clean/dirty) shares one id; splits keep a group together |
| `sha1` | hash of the original file, used to drop duplicates |
| `notes` | free text |

## 4. How the data was collected (reproducible procedure)
**Team photos (`<%>`).** Each of the four members photographed everyday items from an assigned category set with their own phone camera, at home, in campus kitchens and offices, at UM-Flint paired bin stations and dining areas, between `<dates>`:
- **Daud Jan:** containers (plastic tubs/jugs/bottles, glass jars, cans, foil trays, aerosol cans)
- **Hina Kramer:** paper and cardboard (boxes flat and unflattened, pizza boxes, newspaper, cartons, paper cups)
- **Khurram Shafique:** campus disposables (coffee cups, plastic cups and lids, straws, cutlery, packets, styrofoam, takeout containers, water bottles)
- **Ian Slackta:** not-accepted and hard cases (bags and film, bagged recyclables, bubble wrap, hangers, cords, batteries/electronics, ceramic/Pyrex, deliberately ambiguous shots)

Rules followed: one item per photo (except bagged-group shots); vary background and lighting; when an item can appear in two states (clean/dirty, loose/bagged, flat/unflattened), photograph **both** as separate images; no people, faces, names or addresses in frame; items we hold or placed ourselves, never other people's bin contents.

**Openly licensed photos (`<%>`).** Searched Wikimedia Commons, Openverse (license filter: CC0 + CC BY) and Google Open Images (CC BY images tagged e.g. "Bottle", "Tin can") for household items in the same categories. Only CC0/CC BY images were kept. URL, author and license were recorded in `attribution.csv`. Existing material-type tags were **not** used as labels.

**Processing.** `scripts/prepare_images.py` applied the EXIF rotation, then removed all metadata (including GPS), resized to 512 px on the long edge, renamed to `bcc_#####.jpg` and dropped byte-identical duplicates. Raw files of the same object in different states were named `object__state.jpg`, which sets a shared `item_group_id`.

**Sampling.** All usable photos taken were kept. Photos were removed only if blurry beyond recognition, duplicated, or containing people or personal information (`<n>` removed).

**Missing data.** `<e.g. source_url blank for team photos by design; any other gaps>`

## 5. Estimated labeling time
From our timed internal pilot (`<n>` images, `<k>` annotators): **about `<X>` seconds per image** (median), so roughly **`<Y>` images per hour**, including reading the guidelines at the start. Hard cases (cup vs. tub, residue) take longer.

## 6. Annotation plan
About 5 external annotators × 1 hour, plus at least 1 internal annotator.
- **Agreement set:** `<A>` images labeled by **every** annotator (inter-annotator agreement + majority-vote ground truth in Phase 2).
- **Coverage:** each annotator also labels `<B>` non-overlapping images.
- **Result:** about `<A + 6B>` labeled images, `<A>` of them with 6 labels each.

Why: `<one-sentence justification of the redundancy vs. coverage tradeoff>`

Generated with `python scripts/make_annotation_packs.py --agreement <A> --batch <B> --external 5 --internal 1 --seed 42`.

## 7. Use of AI tools
The processing scripts, Potato config and README template were drafted with Claude (Anthropic) and reviewed/tested by the team.
