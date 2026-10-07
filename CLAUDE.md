# CLAUDE.md: Blue Cart Check (ARI 410/510 ML course project, UM-Flint, Fall 2026)

Project memory for Claude Code. Read this first in every session.

## What this project is
A 4-class **image classification dataset + models** for one question: *does this item go in Flint's blue recycling cart?*
Input = one phone photo of an everyday item. Labels (assigned by human annotators, NEVER at collection time):

| label | meaning |
|---|---|
| `accepted` | blue cart as-is (clean, empty, loose, accepted material) |
| `accepted_after_prep` | accepted material, needs rinse / empty / flatten / un-bag first |
| `not_accepted` | never the blue cart (bags, cups, styrofoam, greasy paper, electronics, ...) |
| `cannot_determine` | the photo doesn't show enough to decide |

Annotators do not pick these four labels directly. The tool asks two questions (Step 1 `cart`: blue_cart / not_blue_cart / cannot_tell; Step 2 `condition`, only for blue_cart: ready / needs_prep / ruined / cannot_tell) and `derive_label()` in `scripts/compute_agreement.py` maps the answers to the label.

Ground-truth rule source: City of Flint curbside program (Priority Waste), cross-checked with UM-Flint campus guidance. The rules are versioned in `annotation/guidelines.md`.
Primary metric: **macro-F1** (4 classes). Safety gate: **recall on `not_accepted`**. Also report accuracy, per-class P/R, and the 4×4 confusion matrix.

Team (Group 2, all ARI 510): Khurram Shafique (project lead), Daud Jan (data lead), Hina Kramer (annotation lead), Ian Slackta (modeling & deployment lead). Instructor: Prof. Steven Wilson.

## Course phases (see docs/PROJECT_OVERVIEW.md)
1. Proposal ✅ (Sep 15)
2. **Phase 1: data collection + annotation setup + 5-min presentation, due Tue Oct 6 2026, 2:30pm** ← current
3. Phase 2: annotation by classmates → inter-annotator agreement → ground truth
4. Baselines (kNN, LR, SVM, DT/RF/XGBoost, NN) → benchmark
5. Leaderboard / competition for classmates → submit to other teams' tasks
6. API / deployment of the best system

Requirements for the current phase: `docs/REQUIREMENTS_PHASE1.md` (distilled from the handout in `docs/course/`).

## Repo map
```
data/images/            processed JPEGs (512px long edge, no metadata), bcc_00001.jpg ...
data/raw/               ORIGINAL phone photos. Contain GPS. NEVER commit, NEVER copy elsewhere
data/manifest.csv       one row per image (schema in README.md §3)
data/attribution.csv    source/author/license for every non-team image
annotation/guidelines.md        annotator rules (owner: Hina)
annotation/HOW_TO_ANNOTATE.md   annotator setup steps
annotation/potato/welcome.html  welcome page shown once after login (team, instructor and TA names are here and in the page footer in config.yaml); the pack/space scripts also serve it again as media/how_it_works.html for the round help button
annotation/potato/config.yaml   Potato annotation tool config (tested with potato-annotation 2.9.4). Its rules cheat sheet must stay in sync with guidelines.md
annotation/packs/       generated per-annotator zips (gitignored)
annotation/returned/    annotators' annotation_output folders (gitignored until anonymized)
scripts/                pipeline (see Commands)
tests/                  pytest smoke tests
docs/                   project docs, figures, course material (docs/course is gitignored)
```

## Commands
Always activate the venv first: `source .venv/bin/activate`
| task | command |
|---|---|
| add photos | `python scripts/prepare_images.py --input data/raw/<folder> --photographer "Name" --category-set <containers/paper/disposables/hard> --setting <kitchen/office/bin_station/outdoor/dining/other>` |
| divide the open-dataset photos between the four members' sets (writes "assigned to ... set" into manifest notes) | `python scripts/assign_sets.py --ian 142 --hina 115 --daud 175 --khurram 185` |
| dataset stats + charts | `python scripts/dataset_stats.py` |
| PCA / k-means / near-dupes | `python scripts/explore_embeddings.py [--features resnet]` |
| annotator packs | `python scripts/make_annotation_packs.py --agreement 100 --batch 150 --external 5 --internal 1` |
| run annotation tool locally | `cd annotation/packs/internal_01 && potato start config.yaml -p 8000` |
| see the labels given so far (table + photo review page) | `python scripts/show_labels.py` |
| seconds per photo (pilot timing) | `python scripts/labeling_time.py` |
| build the Hugging Face Space folder (optional hosting, see docs/HUGGINGFACE_HOSTING.md) | `python scripts/make_hf_space.py --backup-repo <hf-name>/blue-cart-check-annotations` |
| start the PUBLIC tool at https://bluecart.khurramshafique.com (port 8010 + Cloudflare tunnel) | `bash scripts/start_public_tool.sh` |
| install our login/register page into the Potato in this venv (`annotation/potato/login_page.html`; run after any pip install of potato; `--check`, `--restore`) | `python scripts/patch_login_page.py` |
| move the public tool to an Azure VM (Azure for Students), same address, accounts and answers kept | `docs/AZURE_HOSTING.md` + `scripts/azure/{setup_vm,migrate,tunnel_vm}.sh` |
| agreement + majority labels (Phase 2) | `python scripts/compute_agreement.py` |
| group-safe splits | `python scripts/make_splits.py --test 0.2 --val 0.1` |
| tests | `pytest -q` |
| everything via make | `make help` |

## Hard rules (do not break)
1. **Privacy:** never commit `data/raw/`; every image must go through `prepare_images.py` (strips EXIF/GPS). No faces, names, addresses. If an image shows one, flag it, don't "fix" it silently.
2. **No labels at collection time.** Never add a label/expected-label column to `manifest.csv`. Labels only come from annotation (`data/labels_majority.csv`).
3. **Item groups:** the same physical object in several states shares an `item_group_id` (raw files named `cup07__clean.jpg`, `cup07__dirty.jpg`). Splits must keep groups together, so use `make_splits.py`, never a plain random split.
4. **Licenses:** every non-team image gets a row in `data/attribution.csv` with its real author. The dataset is CC BY-NC-SA 4.0 because the RealWaste images require it. Code = MIT. Do not put a team member's name in `attribution` for an image the team did not take.
5. **Don't change the label set or decision rules** after the internal pilot without updating `CHANGES_FROM_PROPOSAL.md` and bumping the guidelines version.
6. **Test-set hygiene:** never tune on the test split. Model selection uses validation or cross-validation (StratifiedGroupKFold).
7. **AI disclosure:** the course allows AI tools but requires disclosure. When you (Claude) write or substantially change a deliverable, add a line to `docs/AI_USE_LOG.md` (date, what, how prompted).
8. Keep it explainable: the team must be able to present every number. Prefer simple, commented code over clever code.

## Conventions
- Python 3.11+, scripts are standalone CLI tools with `argparse` and a docstring at the top explaining usage.
- Paths relative to the repo root via `REPO = Path(__file__).resolve().parents[1]`.
- IDs: `bcc_#####`. Annotator ids: `external_XX`, `internal_XX`.
- New model code → `models/` (one script per baseline) + results appended to `results/results.csv` (model, features, split, macro_f1, recall_not_accepted, accuracy, date, notes).
- Figures → `docs/figures/` at dpi 200, readable on a slide.
- Commit messages: `area: what` (e.g. `data: add 120 disposables photos`, `annotation: guidelines v1.0`).

## How to work with the team
Khurram drives Claude Code. Team members send pieces over Discord/Drive. Before merging someone's images, run `prepare_images.py` + `pytest -q` + `dataset_stats.py` and spot-check 5 images.
