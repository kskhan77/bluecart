# Kaggle competition: setup checklist and texts to paste (Phase 2a, step 5)

The competition is a **Kaggle Community Competition** ("Machine Learning Competition"), private, reachable only
through its invitation link. Everything below is ready to paste; the numbers come from `scripts/make_kaggle_files.py`
(rerun it after the adjudication and check the printed counts against the ones here).

**Status 2026-11-05:** the competition exists at https://www.kaggle.com/competitions/blue-cart-check (private, unlaunched, host account kskhan77). Done on Kaggle: rules, overview, description and evaluation texts, dataset description, licence CC BY-NC-SA 4.0, metric, solution file, the pre-launch test (answer key 1.00000 on both leaderboards; sample submission 0.17094 public, 0.17647 private, equal to `scripts/score_submission.py`) and four benchmarks. Still open: set the end date (Settings, Key Dates), upload the data zip (Data tab), launch, add the teammates as hosts. The invitation link is on the launch checklist page and in the team Discord; it is not written in this public repository on purpose.

## 0. Make the files (after `merge_adjudication.py`)

```bash
python scripts/make_kaggle_files.py --write-repo
python scripts/score_submission.py deploy/kaggle/public/sample_submission.csv
python scripts/score_submission.py deploy/kaggle/private/solution.csv      # must print 1.0000 three times
```

| upload where | file |
|---|---|
| Data tab (participants download these) | `deploy/kaggle/blue_cart_check_kaggle_data.zip` (train.csv, test.csv, sample_submission.csv, README.txt, images/) |
| Evaluation tab, "solution file" | `deploy/kaggle/private/solution.csv` only here, nowhere else |
| Evaluation tab, "sample submission" | `deploy/kaggle/public/sample_submission.csv` |

`private/` is gitignored and must never go to GitHub, Drive or Discord. With `--write-repo` the script also writes
`data/splits.csv` and `data/labels_trainval.csv` (train and validation labels only), which can be committed.

## 1. Checklist in the Kaggle host interface

1. kaggle.com → Competitions → Host a competition → Community → Machine Learning Competition. Title: **Blue Cart Check**.
2. Visibility **Private**. Add the other three team members as hosts (full access).
3. Timeline: launch by the Phase 2a due date; **end date = end of Phase 2b** (when the private leaderboard is revealed). Kaggle shows UTC: Flint is UTC−5 after Nov 1, so a 11:59 pm Flint deadline is 04:59 UTC the next day.
4. Data tab: upload the zip; paste section 3 as the data description.
5. Settings, Evaluation Metric: metric **F1 Score** (Kaggle's wrapper of scikit-learn's `f1_score`), then Edit the hyperparameters and set `average` to `"macro"`. Do not pick the older "F-Score (Macro)": it only accepts numeric labels and fails on our text labels. Upload `solution.csv` (first column = id, last column `Usage` sets the Public/Private rows). The daily limit of 5 submissions is the default under Settings, Scoring.
6. Overview: paste sections 2 and 4. Rules page: paste section 5 (participants must accept it before downloading).
7. Test before launch: submit `solution.csv` as a prediction (score must be 1.00000) and `sample_submission.csv` (public score 0.171, private 0.176 on the final labels). Delete those test submissions or mark them as benchmarks.
8. Submit the baselines from step 6 and tick **Benchmark** on them so they show on the leaderboard as reference points. Expected public / private scores: `random_by_share.csv` 0.230 / 0.234, `lr_resnet50.csv` 0.455 / 0.595, `llm_claude.csv` 0.480 / 0.578.
9. Launch, then copy the **invitation link** from the launch checklist into the Discord post (#project-competitions) and the slides.

## 2. Overview (Description)

**Does this item go in Flint's blue recycling cart?**

You get one phone photo of one everyday item (a can, a box, a cable, a cup, a bag) and predict what the City of
Flint's curbside recycling program does with it:

| label | meaning |
|---|---|
| `accepted` | accepted material, ready as it is: clean, empty, loose |
| `accepted_after_prep` | accepted material that needs a rinse, emptying, flattening or un-bagging first |
| `not_accepted` | never the blue cart: plastic bags, cups, styrofoam, greasy paper, electronics, or ruined material |
| `cannot_determine` | the photo does not show enough to decide |

Why it matters: Flint residents sort recycling at the cart, and one wrong item (a plastic bag, a greasy box) can
contaminate a whole load. A model that answers this from a phone photo could sit behind a "can I recycle this?"
app. Missing a `not_accepted` item is the costly mistake, so besides the leaderboard metric we report recall on
`not_accepted` for every model in class.

The photos are 648 single-item pictures: 108 taken by the project team in Flint kitchens, offices and bin stations,
540 selected from open datasets (RealWaste, Drinking Waste Classification, Wikimedia Commons). 617 of them carry a
label from the class annotation round: 15 annotators, 3 to 6 labels per photo, Krippendorff's alpha 0.46 on the
four-way label. The label is the majority vote; the 63 photos with a tied vote were settled by a tiebreak decision
of the project team against the written guideline. The guideline is public:
https://github.com/kskhan77/bluecart/blob/main/annotation/guidelines.md

## 3. Data description

- `train.csv`: `id`, `image`, `split` (`train` or `val`), `label`. 463 photos (405 train, 58 val). Use our validation
  split or make your own; the split keeps the few objects photographed in several states on one side.
- `test.csv`: `id`, `image`. 154 photos, no labels. Half of them score the public leaderboard, half the private one.
- `sample_submission.csv`: `id`, `label`. Exactly the file you upload: one row per test id, label one of the four
  strings above. As given it predicts `accepted` for every photo, which is the majority baseline.
- `images/`: every photo as JPEG, long side 512 px, no metadata, named `<id>.jpg`. The `image` column holds this path.
- The class shares are unequal: roughly 55% `accepted`, 32% `not_accepted`, 9% `accepted_after_prep`,
  4% `cannot_determine`. The small classes are small in the test set too; that is why the metric is macro-F1.

## 4. Evaluation

Submissions are scored with **macro-F1**: the F1 score of each of the four labels, averaged with equal weight.
Accuracy would reward a model that always says `accepted` (about 55% accuracy, macro-F1 0.17); macro-F1 makes the
two rare labels count as much as the two common ones. The public leaderboard uses half of the test photos; the final
ranking is the private half, revealed at the end date.

Submission format: a CSV with a header and one row per test photo. These are the first rows of
`sample_submission.csv`; replace each label with your model's prediction (one of the four strings):

```
id,label
bcc_00004,accepted
bcc_00005,accepted
```

## 5. Rules

1. The data is for ARI 410/510 (University of Michigan-Flint, Fall 2026) only. Do not redistribute it.
2. Predictions must come from a model you ran. Labeling test photos by hand, or by looking at them yourself and
   correcting the model, is not allowed. The team that hosts the task does not compete.
3. Do not look for the labels elsewhere: the annotation tool, the hosts, other teams. Do not use the test images for
   anything except producing predictions (no training, no clustering, no manual checks).
4. Pretrained models and embeddings (ImageNet, CLIP, any vision backbone or multimodal LLM) are allowed, as is
   extra training data from elsewhere, as long as rule 3 holds. Say what you used in your write-up.
5. Up to 5 submissions per day; your team name must include your project group number so hosts can tell who is who.
6. Be ready to share your code with the hosts and the instructor on request.

## 6. Data licence

The photos and labels are released under **CC BY-NC-SA 4.0** for use in ARI 410/510 only. 360 photos come from
RealWaste (CC BY-NC-SA 4.0), 160 from Drinking Waste Classification (CC0), 20 from Wikimedia Commons (various free
licences), 108 were taken by the project team (CC BY 4.0). Per-photo author and licence: `data/attribution.csv` in
https://github.com/kskhan77/bluecart. The repository holds the photos and the train/validation labels, never the
test labels.
