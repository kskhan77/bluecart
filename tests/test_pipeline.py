"""Smoke tests: run with `pytest -q` from the repo root.

They build a throwaway copy of the repo with fake phone photos (with GPS EXIF)
and check that the pipeline strips metadata, resizes, groups, and packs correctly.
"""

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture()
def repo(tmp_path):
    dst = tmp_path / "repo"
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", ".venv", "images", "packs", "returned", "course"))
    (dst / "data" / "images").mkdir(parents=True, exist_ok=True)
    (dst / "data" / "manifest.csv").write_text(
        "id,image_path,width,height,source,source_url,license,attribution,capture_date,"
        "setting,category_set,item_count,item_group_id,sha1,notes\n")
    raw = dst / "data" / "raw" / "t"
    raw.mkdir(parents=True)
    import piexif
    for i in range(30):
        exif = piexif.dump({"0th": {piexif.ImageIFD.Orientation: 6},
                            "GPS": {piexif.GPSIFD.GPSLatitudeRef: b"N",
                                    piexif.GPSIFD.GPSLatitude: ((43, 1), (0, 1), (0, 1))}})
        name = f"cup{i // 3:02d}__v{i % 3}.jpg"
        Image.new("RGB", (3000, 4000), (i * 8 % 255, 90, 160)).save(raw / name, exif=exif)
    return dst


def run(repo, *args):
    return subprocess.run([sys.executable, *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def test_prepare_strips_exif_and_groups(repo):
    run(repo, "scripts/prepare_images.py", "--input", "data/raw/t", "--photographer", "Test Person",
        "--category-set", "disposables", "--setting", "bin_station")
    rows = list(csv.DictReader(open(repo / "data" / "manifest.csv")))
    assert len(rows) == 30
    im = Image.open(repo / "data" / rows[0]["image_path"])
    assert max(im.size) == 512
    assert im.size == (512, 384)            # portrait EXIF rotation applied
    assert not im.info.get("exif")          # metadata gone
    groups = {r["item_group_id"] for r in rows}
    assert len(groups) == 10 and "TP-cup00" in groups
    # re-running must not duplicate
    run(repo, "scripts/prepare_images.py", "--input", "data/raw/t", "--photographer", "Test Person",
        "--category-set", "disposables", "--setting", "bin_station")
    assert len(list(csv.DictReader(open(repo / "data" / "manifest.csv")))) == 30


def test_packs(repo):
    run(repo, "scripts/prepare_images.py", "--input", "data/raw/t", "--photographer", "Test Person",
        "--category-set", "disposables", "--setting", "bin_station")
    run(repo, "scripts/make_annotation_packs.py", "--agreement", "10", "--batch", "3", "--external", "5", "--internal", "1")
    packs = repo / "annotation" / "packs"
    items = [json.loads(l) for l in open(packs / "external_01" / "data" / "items.jsonl")]
    assert len(items) == 13
    assert all((packs / "external_01" / "media" / Path(i["image"]).name).exists() for i in items)
    plan = json.load(open(repo / "annotation" / "assignment_plan.json"))
    assert len(plan["agreement_ids"]) == 10


def test_splits_keep_groups_together(repo):
    run(repo, "scripts/prepare_images.py", "--input", "data/raw/t", "--photographer", "Test Person",
        "--category-set", "disposables", "--setting", "bin_station")
    run(repo, "scripts/make_splits.py", "--test", "0.2", "--val", "0.2", "--no-labels-ok")
    rows = list(csv.DictReader(open(repo / "data" / "splits.csv")))
    by_group = {}
    for r in rows:
        by_group.setdefault(r["item_group_id"], set()).add(r["split"])
    assert all(len(s) == 1 for s in by_group.values())
