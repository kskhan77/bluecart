# Blue Cart Check: Project Overview

**Course:** ARI 410/510 Machine Learning, UM-Flint, Fall 2026 (Prof. Steven Wilson)
**Team:** Group 2 (all ARI 510)
**Project weight:** 45% of the course grade (+10% presentations)

## The task in one line
From one phone photo of an everyday item, decide whether it goes in Flint's blue recycling cart: `accepted` / `accepted_after_prep` / `not_accepted` / `cannot_determine`.

## Why it matters
- UM-Flint switched to single-stream recycling with paired blue/black bins in July 2026. People don't know what goes where.
- Contamination (bags, greasy cardboard, cups) gets whole loads rejected and landfilled.
- Local rules differ from what people assume (foil trays and aerosol cans are accepted; coffee cups aren't).
- Existing datasets (TrashNet, TACO) label the **material**, not **local acceptability** or the **condition** of the item (clean, bagged, flattened). That condition is our contribution.

## Team roles (from the team contract)
| person | role | photo set (~200 each, min 150) |
|---|---|---|
| Khurram Shafique | Project lead: Canvas, deadlines, weekly check-in, instructor contact | campus disposables (cups, lids, straws, cutlery, packets, styrofoam, takeout, bottles) |
| Daud Jan | Data lead: collection checklist, sourced images, attribution, dataset versioning | containers (tubs, jugs, bottles, jars, cans, foil, aerosol) |
| Hina Kramer | Annotation lead: guidelines, annotation app, pilot, agreement analysis | paper & cardboard (boxes, pizza boxes, newspaper, cartons, paper cups) |
| Ian Slackta | Modeling & deployment lead: benchmarks, competition page, deployed app | not-accepted + hard cases (bags, cords, batteries, ceramic, ambiguous shots) |

Internal deadline = 48 h before every Canvas deadline.

## Dataset plan
- Target about 1,200 images: about 65% team photos and about 35% CC0/CC BY open images (Wikimedia, Openverse, Open Images).
- Target label mix: about 35% accepted, 25% after_prep, 30% not_accepted, 10% cannot_determine.
- 512 px JPEG, metadata stripped, one item per photo (except bagged groups), no people or personal info.
- Each image gets at least 2 annotators where possible; a shared agreement set gets labeled by everyone.

## Course pipeline and our plan per phase
| # | phase (course) | what we deliver | key tools | status |
|---|---|---|---|---|
| 0 | Proposal | task, metrics, data plan, team contract | — | ✅ Sep 15 |
| 1 | **Data collection + annotation setup** | dataset + README + license + guidelines + Potato interface + changes note + Google Form + Discord slides + 5-min talk | Pillow, Potato, pandas | **due Oct 6, 2:30pm** |
| 2 | Annotation + ground truth | classmates label (about 5 × 1 h) + our internal labels → Fleiss κ / Krippendorff α → majority-vote labels → datasheet | `compute_agreement.py`, MACE/Cleanlab (optional) | next |
| 3 | Baselines / benchmark | kNN, logistic regression, SVM (linear/RBF), decision tree, RF, XGBoost on image features; MLP / fine-tuned CNN; zero-shot CLIP + frontier LLM comparison | scikit-learn, XGBoost, PyTorch/timm, CLIP | later |
| 4 | Leaderboard | hidden-label test set, public/private leaderboard, starter notebook | Kaggle Community Competition or Codabench; HF Datasets | later |
| 5 | Systems for other teams | submit our models to classmates' tasks | Colab | later |
| 6 | API / deployment | best model behind an API + simple camera web demo | FastAPI or Gradio on HF Spaces | later |

## Metrics (from the proposal)
- **Primary:** macro-F1 over 4 classes.
- **Gate:** recall on `not_accepted` (missing a contaminant is the expensive error).
- **Also:** accuracy, per-class precision/recall, 4×4 confusion matrix (watch accepted ↔ accepted_after_prep).

## Promised extras (from the proposal; don't forget)
- A 10-item frontier-LLM check (2 models × 2 runs, with our instructions): self-contradiction, model-vs-model, model-vs-rule. **Ian** presents the table at the first checkpoint (Oct 6).
- Guidelines quote the city rules word for word, version the rule source and freeze it.

## Key dates
| date | what |
|---|---|
| Oct 4 (Sun) | internal deadline: all sections in |
| Oct 6 (Tue) 2:30pm | Phase 1 Canvas + Google Form + Discord post + presentation; Pset 1 peer eval/corrections |
| Oct 15 | Lab 2 (unsupervised learning + feature selection) |
