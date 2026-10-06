# Lecture → Project insights (Lectures 1–7, 9–11)

| lecture | idea | how we use it |
|---|---|---|
| L1 Intro | "Catalog of fruit": a dataset is one *operational definition*, not the truth | Frame the task as "Flint rules v1.0 on phone photos", not "recycling" in general |
| L1 | Gen-AI allowed with disclosure | `docs/AI_USE_LOG.md` + AI note in every deliverable |
| L1/L3 | Project pipeline: task → data → annotation → baselines → leaderboard → API | `docs/PROJECT_OVERVIEW.md` phase table |
| L2 kNN + eval | Macro precision/recall/F1 | Primary metric macro-F1; gate = recall(not_accepted) |
| L2 | Test set must be unseen and representative | `item_group_id` + `make_splits.py` (no clean/dirty twin leakage); later hold out a setting or photographer |
| L2 | Feature scaling matters for kNN | StandardScaler in every distance-based baseline |
| L3–4 LogReg | Softmax for multiclass; feature engineering before deep learning | Baseline #1: softmax LR on color/shape features, then on embeddings |
| L4–5 | Multiclass vs. multilabel; one-vs-rest | Reason codes could become a multilabel side task; one-vs-rest "not_accepted" detector for the safety gate |
| L5 Regularization | Small data overfits; L2 / C tuning | Tune C/λ on validation or CV only |
| L6 SVM + kernels | Hand-engineer → kernel → learned feature map | Baseline ladder: hand features → RBF-SVM → CNN/CLIP embeddings |
| L6 Ground truth | Subjectivity spectrum: "content moderation using a policy" | Use this phrase in the talk: our task is policy-based and fairly objective |
| L6 | Crowd / panel / author / SME labeling | Crowd = classmates; internal = us; possible later SME check with campus sustainability staff |
| L6 | Annotator diversity can change labels | Optionally record annotator context (Flint resident? on campus?) for Phase 2 analysis |
| L6 | IAA: Cohen (2 raters), Fleiss (2+), Krippendorff (missing data) | `compute_agreement.py`: Fleiss on the agreement set, Krippendorff overall, pairwise Cohen |
| L6 | "Can I just use ChatGPT?" flowchart | Show next to Ian's 10-item LLM check in the talk |
| L6 | Generated labels → augmentation | Later: flips/crops/brightness to simulate phones and lighting |
| L6 | Weak supervision risks learning the rule | Labels come from humans, never metadata |
| L7 Clustering/PCA | PCA 2-D map, k-means elbow + silhouette | `explore_embeddings.py` → slide figure + photographer-bias check + near-duplicates |
| L7 | Entropy / information gain | Which reason code best explains the label (Phase 2 analysis) |
| L9 Decision trees | Cross-validation when data is small | StratifiedGroupKFold for model selection |
| L9 | Feature selection (univariate, RFE, sequential) | Apply to hand-crafted features; compare with embeddings |
| L9–10 | Bias vs. variance | Vocabulary for explaining baseline results |
| L10 RF/XGBoost | Strong, fast on tabular features | RF + XGBoost on embeddings as baselines |
| L11 NN + backprop | Neural nets learn features ("end of feature selection") | MLP on embeddings → fine-tuned MobileNet = best model for the API |

## Phase 1 check against the lectures (Oct 4, 2026)

Lecture 8 has no slides in our folder, so this covers Lectures 1 to 7 and 9 to 11. Lectures 6 and 7 are the ones about data and annotation.

### Where the project follows the lectures
| lecture idea | what we do |
|---|---|
| L6 Operational definition: "the statement of procedures the researcher is going to use in order to measure a specific variable" | The guidelines are our operational definition of "belongs in the blue cart": dated rule sources quoted word for word, plus decision rules |
| L6 Four sources of ground truth; ours is human annotation ("assumes humans can do the task correctly and consistently") | Labels come only from annotators, never from file names or metadata |
| L6 Weak supervision risk: "learning to model rule instead of task" | No label column at collection time; rules guide people but do not decide for them |
| L6 What can go wrong with human annotation: "annotators do not have enough information", "instructions are unclear/vague", "task is too difficult/long" | Rules are shown inside the tool; the question is split into two simple steps; packs are sized for one hour |
| L6 Subjectivity spectrum: "content moderation (using a policy)" sits toward the objective side | Our task is policy-based, so we expect good agreement except at the boundaries (cup vs. tub, clean vs. greasy) |
| L6 Labeling strategies: crowd, "ask multiple people and aggregate" | Classmates plus one internal annotator; majority vote on the agreement set |
| L6 Collect / preprocess / annotate questions (permission, sensitive information, format, how much to annotate, label level) | CC0/CC BY only; EXIF and GPS stripped, people flagged; one image-level label; agreement set plus coverage batches |
| L6-7 Agreement: Cohen (2 raters), Fleiss (2+ raters), Krippendorff (incomplete data) | `compute_agreement.py` reports all three |
| L6-7 Low agreement means unclear instructions, missing expertise, or a subjective task | Internal pilot first, then fix the rules people disagreed on, then lock v1.0 |
| L6-7 "Can I just use ChatGPT to do X?" flowchart | The proposal's 10-item model check (Ian) |
| L7 Annotation platforms: Potato, Doccano, Labelme | Potato |
| L7 Entropy and information gain; L9 decision trees | The two-step question is a small decision tree: Step 1 (kind of item) removes most of the uncertainty, Step 2 (state) settles the rest |
| L2 Macro precision / recall; test set must be representative and unseen | Macro-F1 as the main metric; `item_group_id` keeps photos of one object in one split |

### Gaps to close
*Later on Oct 4: 420 photos from two existing datasets were added (cans, bottles, paper, cardboard, mixed trash), so gap 1 is smaller. The team's own photos are still only Ian's 77.*

1. **Representative data (L6: "Will the data be representative?").** Only Ian's set is in: 77 photos from the "not accepted and hard cases" category (cables, electronics, bags). The containers, paper and disposables sets are missing, so there are almost no cans, bottles, paper or cardboard yet and most photos would end up with the same label.
2. **Internal annotation and agreement (L6-7).** Not started. The pilot is also what tells us whether the two-step rules are clear.
3. **Item groups (L2: unseen test set).** Ian's photos were not named with the `object__state` convention, so several photos of the same object are separate groups. Fix before any train/test split.
4. **Sensitive information (L6).** One photo shows part of a person and three look into bins; they are flagged in `manifest.csv` and need a decision.
5. **The model check (L6-7 flowchart).** Promised in the proposal for the first presentation; not done yet.

