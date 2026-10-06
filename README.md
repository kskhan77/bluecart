# Blue Cart Check: Dataset (ARI 410/510, Group 2, UM-Flint, Fall 2026)

**Task:** given one phone photo of an everyday item, decide whether it goes in Flint's blue recycling cart under the City of Flint curbside rules (Priority Waste).
**Labels (assigned by annotators, not included at collection time):** `accepted` · `accepted_after_prep` · `not_accepted` · `cannot_determine`. Annotators answer two questions per photo (what kind of item, and what state it is in); the label is computed from the two answers (`annotation/guidelines.md` Section 2).

**Team:** Daud Jan · Hina Kramer · Khurram Shafique · Ian Slackta
**Dataset link (UM access):** https://github.com/kskhan77/bluecart (public, so every UM student can open it). The photos are in `data/images/`, one row per photo in `data/manifest.csv`, credits in `data/attribution.csv`.
**License:** CC BY-NC-SA 4.0 (see `LICENSE.md`). The RealWaste photos require the non-commercial, share-alike terms.
**Annotation tool (hosted):** https://bluecart.khurramshafique.com · **Project Discord:** https://discord.gg/2t2DSNyBm

**Phase 1a deliverables, where each one is (handout Section 6):**

| | Deliverable | Where |
|---|---|---|
| (a) | Dataset link with UM access | this repository, `data/` folder (link above) |
| (b) | Dataset description | this README, Sections 1 to 6 |
| (c) | License | [`LICENSE.md`](LICENSE.md) |
| (d) | Annotation instructions | [`annotation/HOW_TO_ANNOTATE.md`](annotation/HOW_TO_ANNOTATE.md) and the guidelines [`annotation/guidelines.md`](annotation/guidelines.md); annotators label at https://bluecart.khurramshafique.com |
| (e) | Changes from proposal | [`CHANGES_FROM_PROPOSAL.md`](CHANGES_FROM_PROPOSAL.md) |
| (f) | Custom annotation platform note | not applicable: we configured Potato, the handout's recommended tool. The AI help used along the way is logged in [`docs/AI_USE_LOG.md`](docs/AI_USE_LOG.md) |

---

## 1. What one instance is
One instance = **one JPEG photo of a single everyday item** (or a small group of items when the point is that they are bagged together), shown the way a person would see it just before choosing a bin. Every image has one row in `data/manifest.csv`.

## 2. Size and composition
| | Count |
|---|---|
| Total images | 617 |
| Team-photographed | 77 (12%), all by Ian Slackta, category set `hard` |
| Sourced | 540 (88%): RealWaste 360, Kaggle Drinking Waste 160, Wikimedia Commons 20 |
| Category sets: containers / paper / disposables / hard | 340 / 140 / 0 / 137 |
| Collection dates | 2026-09-28 to 2026-10-04 |

Responsibility sets are written in the `notes` column: Daud Jan 175, Hina Kramer 115, Khurram Shafique 185, Ian Slackta 142. Ian's 142 are his 77 phone photos plus 65 sourced images. The other three sets are sourced images that member is responsible for. There are no `disposables` rows yet, because Khurram's own campus-disposables photos are not in the dataset.

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
  labeling_time.py           seconds per photo from the annotation tool's log
  show_labels.py             table + photo review page of the labels given so far
  make_hf_space.py           optional: build the folder for hosting the tool on Hugging Face
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
| `source` | `team`, `wikimedia`, `openverse`, `openimages`, `realwaste`, `kaggle_drinking_waste` |
| `source_url` | original URL (sourced images only) |
| `license` | `CC-BY-4.0` (team) or the source image's own license (`CC0-1.0`, `CC-BY-x.x`, and for RealWaste `CC-BY-NC-SA-4.0`, see `LICENSE.md`) |
| `attribution` | photographer (team) or the original author of a sourced image. Never a team member for an image we did not take. If a sourced batch is assigned to a team member's set, that is written in `notes` |
| `capture_date` | date taken, read from the phone's EXIF "date taken" (team) or date downloaded (sourced). If a team photo has no EXIF date, the file's date is used and `notes` says so |
| `setting` | `kitchen`, `office`, `bin_station`, `outdoor`, `dining`, `other` |
| `category_set` | which collection set it belongs to (`containers`, `paper`, `disposables`, `hard`) |
| `item_count` | number of items in the photo |
| `item_group_id` | same physical object photographed in several states (e.g. clean/dirty) shares one id; splits keep a group together |
| `sha1` | hash of the original file, used to drop duplicates |
| `notes` | free text. Entries starting with `REVIEW:` flag a photo that a team member must check (e.g. a person in frame) before release |

## 4. How the data was collected (reproducible procedure)
**Team photos (77 images, 12%).** Ian Slackta photographed not-accepted and hard cases with his phone between 2026-09-28 and 2026-09-29. Daud Jan, Hina Kramer, and Khurram Shafique have not added their own phone photos yet. The sets named below are what each person is responsible for. Sourced images in those sets keep the original author in `attribution.csv`:
- **Daud Jan:** containers (plastic tubs/jugs/bottles, glass jars, cans, foil trays, aerosol cans)
- **Hina Kramer:** paper and cardboard (boxes flat and unflattened, pizza boxes, newspaper, cartons, paper cups)
- **Khurram Shafique:** campus disposables (coffee cups, plastic cups and lids, straws, cutlery, packets, styrofoam, takeout containers, water bottles)
- **Ian Slackta:** not-accepted and hard cases (bags and film, bagged recyclables, bubble wrap, hangers, cords, batteries/electronics, ceramic/Pyrex, deliberately ambiguous shots)

Rules followed: one item per photo (except bagged-group shots); vary background and lighting; when an item can appear in two states (clean/dirty, loose/bagged, flat/unflattened), photograph **both** as separate images; no people, faces, names or addresses in frame; items we hold or placed ourselves, never other people's bin contents.

**Sourced photos (540 images, 88%).** URL, author, and license are in `attribution.csv`. Existing material-type tags were **not** used as labels. The proposal named Wikimedia Commons, Openverse, and Open Images. This release uses Wikimedia Commons plus two existing datasets (RealWaste and Kaggle Drinking Waste). Openverse and Open Images were not used.

**Images we did not take ourselves (added Oct 4, 2026).** 540 images come from two public datasets and Wikimedia Commons. They were added in two rounds: a first sample with seed 42, and a second sample for the containers set with seed 7. Their own class labels (material type) were not used and are not stored in the manifest; the original file name is kept only in `attribution.csv` so each image can be traced back.
- **RealWaste** (Sam Single et al., https://github.com/sam-single/realwaste): 360 of its 4,752 images. A random sample per folder with `--sample N --seed 42`: Cardboard 70, Paper 70, Glass 30, Metal 40, Plastic 50, Miscellaneous Trash 30, Food Organics 10, Textile Trash 10, Vegetation 10. Second round with `--seed 7`: Glass 10, Metal 15, Plastic 15. Waste items photographed one at a time at a landfill facility in Australia.
- **Drinking Waste Classification** (Arkadiy Serezhkin, Kaggle, CC0): 160 of its about 4,828 photos from `rawimgs/` (cans, glass bottles, plastic milk bottles, plastic drink bottles): 25 per folder with seed 42, then 15 per folder with seed 7.
- **Wikimedia Commons**: 20 photos chosen by hand from the categories "Disposable aluminium foil food containers", "Spray cans", "Cans", "Glass jars", "Plastic food containers" and "Margarine tubs". Only CC0, public domain and CC BY files that show one everyday item and no people were kept. Each has its own author, license and page link in `attribution.csv`.

**Processing.** `scripts/prepare_images.py` read the capture date from each photo, applied the EXIF rotation, then removed all metadata (including GPS), resized to 512 px on the long edge, renamed to `bcc_#####.jpg` and dropped byte-identical duplicates. Raw files of the same object in different states were named `object__state.jpg`, which sets a shared `item_group_id`.

**Sampling.** For the team photos, every file in `data/raw/ian/` was kept except byte-identical duplicates, which the script skips. No separate count was kept of shots discarded before that folder was handed in. The 540 sourced images are a described sample, not the whole source dataset: RealWaste and Kaggle rows were drawn at random with a fixed seed (seed 42, then seed 7 for the containers round). The 20 Wikimedia photos were chosen by hand (one everyday item, no people, CC0 / public domain / CC BY only).

**Missing data.** `source_url` is blank for team photos on purpose. `setting` is `other` for all 617 rows, because both the team batch and the sourced batches were ingested with that one setting. `item_count` is 1 for every row and was not checked photo by photo on the sourced images. Fourteen team photos had no EXIF date, so `capture_date` is the file date and `notes` says so. Sourced `capture_date` values are the download date (2026-10-04), not the day the original photographer took the picture. Six rows are flagged `REVIEW:` and still included: `bcc_00040` (part of a person at the edge), `bcc_00025`, `bcc_00026`, and `bcc_00073` (looking into a bin), `bcc_00410` and `bcc_00413` (a shoe tip). They were left in because annotators have already started on the live tool.

## 5. Estimated labeling time
From our timed internal pilot on Oct 5, 2026 (160 photos, 3 team annotators, measured with `scripts/labeling_time.py` from the tool's click log): **about 6 seconds per photo** (median; mean 11 s), so roughly **300 to 500 photos per hour** for someone who already knows the rules. Classmates who see the guidelines for the first time will be slower, so we plan with **about 200 photos per hour**, including reading the welcome page. Hard cases (cup vs. tub, residue) take longer.

## 6. Annotation plan
About 6 external annotators × 1 hour (each student in the class annotates for two other teams), plus the four of us as internal annotators, all on the hosted tool at https://bluecart.khurramshafique.com.
- **Agreement set:** 30 photos labeled by **every** annotator (up to 10 labels each) for inter-annotator agreement and a majority-vote check in Phase 2.
- **Coverage with a second opinion:** every other photo is labeled by **2** annotators. Each annotator gets the 30 shared photos and then the next 170 photos that still need a label, 200 in total, about one hour.
- **Result:** when 7 annotators finish, all 617 photos have 2 labels and the 30 shared ones have up to 10. With only 6 classmates, 540 photos have 2 labels and the team labels the remaining 77. Where the two labels disagree (about a quarter of the photos in our pilot), a team member adds a third label, so every photo ends with a majority.

Why: two labels per photo keep every photo checkable and give the two annotators per image our proposal promised, while fitting the roughly 6 classmate-hours the handout predicts for our class size. Three labels everywhere would need about 9 hours we will not get; one label would leave the disagreements we saw in the pilot undetected.

The hosted tool is built with `python scripts/make_hf_space.py --out deploy/local_server --no-backup --shared 30 --per-annotator 200 --annotators 10 --labels-per-photo 2`. The zip packs from `make_annotation_packs.py` remain as the offline alternative.

## 7. Use of AI tools
The processing scripts, Potato config and README template were drafted with Claude (Anthropic) and reviewed/tested by the team. Claude Code also ran the pipeline and the end-to-end test of the annotation tool, and copied the rule wording in the guidelines from the city and hauler pages. No annotation was done by an AI tool. The full log is in `docs/AI_USE_LOG.md`.
