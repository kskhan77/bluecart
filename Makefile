.PHONY: help setup setup-ml test stats explore packs annotate agreement splits check
PY := .venv/bin/python

help:            ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*##"}{printf "  make %-10s %s\n",$$1,$$2}'

setup:           ## create .venv, install deps, run tests
	bash setup_wsl.sh

setup-ml:        ## setup + torch/torchvision (CPU)
	bash setup_wsl.sh --ml

test:            ## run smoke tests
	$(PY) -m pytest -q

stats:           ## dataset stats + charts (docs/)
	$(PY) scripts/dataset_stats.py

explore:         ## PCA / k-means / near-duplicates (docs/figures)
	$(PY) scripts/explore_embeddings.py

packs:           ## build annotator packs (edit A/B: make packs A=100 B=150)
	$(PY) scripts/make_annotation_packs.py --agreement $(or $(A),100) --batch $(or $(B),150) --external 5 --internal 1

annotate:        ## run Potato on the internal pack at http://localhost:8000
	cd annotation/packs/internal_01 && ../../../.venv/bin/potato start config.yaml -p 8000

agreement:       ## Phase 2: kappa/alpha + majority labels
	$(PY) scripts/compute_agreement.py

splits:          ## group-safe train/val/test split
	$(PY) scripts/make_splits.py --test 0.2 --val 0.1

check: test stats ## quick health check
