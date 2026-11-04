# Baselines (Phase 2a, step 6)

Reference points for the leaderboard. Every number here is reproduced by the scripts in `models/` and logged in
`results/results.csv`; the test numbers are what `scripts/score_submission.py` computes from the Kaggle files
(macro-F1 on the Public half, the Private half and all test photos).

**Preview status (2026-11-04):** the labels are the majority vote with 63 ties still open, so 47 train/val photos
and 16 test photos were left out. After the adjudication is merged, rerun the three scripts (the split stays the
same) and replace the table.

## Results

| model | val macro-F1 | test macro-F1 | Public | Private | recall not_accepted | accuracy |
|---|---|---|---|---|---|---|
| majority (always `accepted`) | 0.175 | 0.178 | 0.178 | 0.178 | 0.000 | 0.551 |
| random, uniform over 4 labels (seed 42) | 0.194 | 0.216 | 0.165 | 0.266 | 0.261 | 0.261 |
| random, by training share (seed 42) | 0.319 | 0.316 | 0.321 | 0.301 | 0.478 | 0.507 |
| logistic regression on ResNet-50 embeddings | 0.645 | 0.590 | 0.457 | 0.696 | 0.804 | 0.804 |
| Claude, zero-shot from the photo | n/a | 0.541 | 0.502 | 0.580 | 0.913 | 0.848 |

Test = 138 adjudicated photos of 154; val = 54 of 58; recall and accuracy are on all test rows.

**Dummy benchmark for Kaggle:** random by training share, the best of the three on validation (handout: keep the
better of random and majority). It beats "majority" on macro-F1 only because it sometimes guesses the small classes.

**Trained benchmark for Kaggle:** the logistic regression. Its per-class F1 on the test set: accepted 0.88,
not_accepted 0.82, accepted_after_prep 0.46, cannot_determine 0.20 (1 of 5 right).

## How each baseline was made

- **Dummies** (`models/baseline_dummy.py`): majority = the most common training label; random uniform draws each of
  the four labels with probability 1/4; random by share draws with the training shares (accepted 0.55,
  not_accepted 0.33, accepted_after_prep 0.08, cannot_determine 0.04). Seed 42; another seed moves the random rows
  by a few points.
- **Trained model** (`models/baseline_lr.py`, the Lab 3 recipe): every photo becomes a 2048-d vector from
  torchvision's ResNet-50 (ImageNet weights `IMAGENET1K_V2`, last layer removed, CPU, about two minutes for 617
  photos, cached in `models/cache/`). StandardScaler + LogisticRegression with `class_weight="balanced"`;
  C chosen on the validation split by macro-F1 (0.01 won among 0.01 to 3), then refit on train + val. The test set
  was never used for any choice.
- **LLM baseline** (`models/baseline_llm.py`): model **Claude Fable 5.1** (Anthropic), run through the Claude Agent
  SDK as eight fresh instances, 19 or 20 test photos each, so that no instance saw anything but the prompt and its
  photos. The prompt is `models/llm_prompt.txt`, verbatim: the labeling rules written out, no labeled examples
  (zero-shot). Each instance opened the photos one at a time and answered one `<id>,<label>` line per photo; the
  eight answer files are gathered and scored by the script. All 154 test photos were answered, so this run can go on
  the leaderboard too. Date: 2026-11-04.

## What the numbers say (for the slide)

- The LLM is the most accurate model (0.85) and the safest on the gate (it catches 91% of `not_accepted`), yet it
  loses on macro-F1 to a 2048-feature logistic regression. The reason is the two small classes: it never answered
  `cannot_determine` correctly (0 of 5) and called 8 of the 11 `accepted_after_prep` photos plain `accepted`. The
  state of an item (rinsed or not, flattened or not, in a bag or not) is exactly the part of the task the proposal
  called non-trivial, and that is where the zero-shot model fails.
- The Public / Private gap of the logistic regression (0.46 vs 0.70) is not a modeling effect: each half has 77
  photos with 2 or 3 `cannot_determine` among them, so one photo moves that class's F1 by a third. Expect noisy
  leaderboard positions among models that are close; the private ranking at the end is the one that counts.
- Majority accuracy is 55%; macro-F1 0.18. That is the number to quote when explaining why accuracy is not the metric.
