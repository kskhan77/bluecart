# Baselines (Phase 2a, step 6)

Reference points for the leaderboard. Every number here is reproduced by the scripts in `models/` and logged in
`results/results.csv`; the test numbers are what `scripts/score_submission.py` computes from the Kaggle files
(macro-F1 on the Public half, the Private half and all test photos).

**Final labels (2026-11-05):** the majority vote for 554 photos plus the team tiebreak on the 63 ties
(`scripts/merge_adjudication.py`). All 463 train/val photos and all 154 test photos are used; the split is the one
frozen on 2026-11-04. The LLM answers are the run of 2026-11-04 (the model never saw labels), rescored here.

## Results

| model | val macro-F1 | test macro-F1 | Public | Private | recall not_accepted | accuracy |
|---|---|---|---|---|---|---|
| majority (always `accepted`) | 0.170 | 0.174 | 0.171 | 0.176 | 0.000 | 0.532 |
| random, uniform over 4 labels (seed 42) | 0.204 | 0.199 | 0.180 | 0.218 | 0.185 | 0.234 |
| random, by training share (seed 42) | 0.218 | 0.232 | 0.230 | 0.234 | 0.296 | 0.409 |
| logistic regression on ResNet-50 embeddings | 0.657 | 0.539 | 0.455 | 0.595 | 0.722 | 0.760 |
| Claude, zero-shot from the photo | n/a | 0.525 | 0.480 | 0.578 | 0.907 | 0.831 |

Test = all 154 photos (82 accepted, 54 not_accepted, 13 accepted_after_prep, 5 cannot_determine); val = all 58.

**Dummy benchmark for Kaggle:** random by training share, the best of the three on validation (handout: keep the
better of random and majority). It beats "majority" on macro-F1 only because it sometimes guesses the small classes.

**Trained benchmark for Kaggle:** the logistic regression. Its per-class F1 on the test set: accepted 0.84,
not_accepted 0.77, accepted_after_prep 0.36, cannot_determine 0.18 (1 of 5 right).

## How each baseline was made

- **Dummies** (`models/baseline_dummy.py`): majority = the most common training label; random uniform draws each of
  the four labels with probability 1/4; random by share draws with the training shares (accepted 0.57,
  not_accepted 0.31, accepted_after_prep 0.08, cannot_determine 0.04). Seed 42; another seed moves the random rows
  by a few points.
- **Trained model** (`models/baseline_lr.py`, the Lab 3 recipe): every photo becomes a 2048-d vector from
  torchvision's ResNet-50 (ImageNet weights `IMAGENET1K_V2`, last layer removed, CPU, about two minutes for 617
  photos, cached in `models/cache/`). StandardScaler + LogisticRegression with `class_weight="balanced"`;
  C chosen on the validation split by macro-F1 (0.1 won among 0.01 to 3), then refit on train + val. The test set
  was never used for any choice.
- **LLM baseline** (`models/baseline_llm.py`): model **Claude Fable 5.1** (Anthropic), run through the Claude Agent
  SDK as eight fresh instances, 19 or 20 test photos each, so that no instance saw anything but the prompt and its
  photos. The prompt is `models/llm_prompt.txt`, verbatim: the labeling rules written out, no labeled examples
  (zero-shot). Each instance opened the photos one at a time and answered one `<id>,<label>` line per photo; the
  eight answer files are gathered and scored by the script. All 154 test photos were answered, so this run can go on
  the leaderboard too. Run on 2026-11-04, rescored on the final labels on 2026-11-05.

## What the numbers say (for the slide)

- The LLM is the most accurate model (0.83) and the safest on the gate (it catches 91% of `not_accepted`), yet it
  ends just behind a 2048-feature logistic regression on macro-F1 (0.525 against 0.539). The reason is the two small
  classes: it never answered `cannot_determine` correctly (0 of 5) and called 10 of the 13 `accepted_after_prep`
  photos plain `accepted`. The
  state of an item (rinsed or not, flattened or not, in a bag or not) is exactly the part of the task the proposal
  called non-trivial, and that is where the zero-shot model fails.
- The Public / Private gap of the logistic regression (0.46 vs 0.60) is not a modeling effect: each half has 77
  photos with 2 or 3 `cannot_determine` among them, so one photo moves that class's F1 by a third. Expect noisy
  leaderboard positions among models that are close; the private ranking at the end is the one that counts.
- Majority accuracy is 53% on the test set (55% over all 617 photos); macro-F1 0.17. That is the number to quote when
  explaining why accuracy is not the metric.
