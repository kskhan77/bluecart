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
