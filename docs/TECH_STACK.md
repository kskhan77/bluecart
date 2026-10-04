# Tech Stack: Blue Cart Check

Chosen = what this repo uses or plans to. Alternatives are kept for the write-ups and in case a choice fails.

## Environment
| layer | chosen | notes |
|---|---|---|
| OS | WSL 2 Ubuntu on Windows | project in `~/workspace-school/blue-cart-check` |
| Language | Python 3.11+ in `.venv` | `requirements.txt` (core), `requirements-ml.txt` (torch) |
| AI pair-programmer | Claude Code (CLI in WSL) | `CLAUDE.md`, `.claude/settings.json`, `.claude/skills/*` |
| Editor | VS Code + WSL extension | optional Claude Code extension |
| Version control | git + GitHub (team repo) | Issues/Projects board for tasks |
| Notebooks / GPU | Google Colab | the course's default; free GPU for CNN fine-tuning |
| Team comms | Discord team channel, Google Drive | per the team contract |

## By project stage
| stage | chosen | alternatives |
|---|---|---|
| Photo capture | phone camera → Drive → `data/raw/` | Roboflow upload; Google Photos album |
| Cleaning & privacy | Pillow + pillow-heif (`prepare_images.py`): EXIF/GPS strip, rotate, 512 px, rename, dedupe | CleanVision (blur/dark/dupes), imagehash (perceptual near-dupes), MediaPipe/OpenCV face flagging |
| Exploration | scikit-learn PCA + KMeans + silhouette (`explore_embeddings.py`) | t-SNE/UMAP; ResNet/CLIP features |
| Dataset hosting | GitHub (small 512 px images) + Drive link for the class | Hugging Face Datasets (public CC BY; easiest for the leaderboard), DVC, Git LFS |
| Annotation tool | **Potato** 2.9.x (recommended by handout; tested) | Label Studio CE, CVAT, labelme, custom HTML via Claude Code |
| Annotation distribution | per-annotator zip packs (`make_annotation_packs.py`) | hosted Potato/Label Studio on HF Spaces / Render / VM |
| Agreement & ground truth | own implementation of Fleiss κ + Krippendorff α (validated against the `krippendorff` package), sklearn Cohen κ, majority vote | MACE / Dawid-Skene (Potato ships MACE), Cleanlab label-issue detection |
| Splits | `make_splits.py`: StratifiedGroupKFold / GroupShuffleSplit by `item_group_id` | plain stratified k-fold (not safe: leakage) |
| Features | color histograms + thumbnails → ResNet-18 → CLIP / DINOv2 embeddings | HOG (scikit-image) |
| Classic baselines | scikit-learn: kNN, LogisticRegression (softmax, L2), SVM linear + RBF, DecisionTree, RandomForest; XGBoost | LightGBM |
| Neural models | MLP on embeddings; fine-tune MobileNetV3 / EfficientNet-B0 (PyTorch + timm) on Colab | zero-shot CLIP; frontier LLM vision APIs as a comparison |
| Experiment tracking | `results/results.csv` | Weights & Biases (free for students), MLflow |
| Leaderboard | Kaggle Community Competition | Codabench, HF Spaces leaderboard, EvalAI |
| API / demo | FastAPI (+ Docker) or Gradio on Hugging Face Spaces | Streamlit; ONNX / TFLite on-device; phone camera web page |

## Why these choices
- **Potato:** zero-code YAML; one item at a time with keyboard shortcuts; JSONL output; per-item timing; the instructor recommends it (developed at UMich).
- **Group-aware splits:** we photograph the same object in several states on purpose, so a random split would leak and inflate scores.
- **Classic models on pretrained features:** matches the course algorithms (Lectures 2–11) while still working on images.
- **Gradio on HF Spaces:** gives a UI and an API in one, free, and it's linkable from the leaderboard page.
