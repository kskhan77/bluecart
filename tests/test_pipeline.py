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
    # never copy raw downloads or photos into the throwaway repo: they are large and can hold GPS data
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", ".venv", "images", "packs", "returned", "course", "raw", "figures"))
    (dst / "data" / "images").mkdir(parents=True, exist_ok=True)
    (dst / "data" / "manifest.csv").write_text(
        "id,image_path,width,height,source,source_url,license,attribution,capture_date,"
        "setting,category_set,item_count,item_group_id,sha1,notes\n")
    # the throwaway repo also starts with an empty credits file
    (dst / "data" / "attribution.csv").write_text("id,source,source_url,title,author,license,license_url,downloaded_on\n")
    raw = dst / "data" / "raw" / "t"
    raw.mkdir(parents=True)
    import piexif
    for i in range(30):
        exif_dict = {"0th": {piexif.ImageIFD.Orientation: 6},
                     "GPS": {piexif.GPSIFD.GPSLatitudeRef: b"N",
                             piexif.GPSIFD.GPSLatitude: ((43, 1), (0, 1), (0, 1))}}
        if i < 15:                              # half the fake photos carry a "date taken"
            exif_dict["Exif"] = {piexif.ExifIFD.DateTimeOriginal: b"2026:09:28 10:00:00"}
        exif = piexif.dump(exif_dict)
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
    # capture date: EXIF "date taken" when present, otherwise the file date (and the notes say so)
    with_exif = [r for r in rows if r["capture_date"] == "2026-09-28"]
    fallback = [r for r in rows if "file timestamp" in r["notes"]]
    assert len(with_exif) == 15 and len(fallback) == 15
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
    # the "Guidelines" button in the tool opens this page, so every pack must carry it
    page = (packs / "external_01" / "media" / "guidelines.html").read_text(encoding="utf-8")
    assert "<table>" in page and "Decision rules" in page
    assert "annotation_codebook_url: /media/guidelines.html" in (packs / "external_01" / "config.yaml").read_text()
    # the welcome page is part of the config (phases block), so every pack must carry the file
    assert "file: welcome.html" in (packs / "external_01" / "config.yaml").read_text()
    assert "Welcome to Blue Cart Check" in (packs / "external_01" / "welcome.html").read_text(encoding="utf-8")
    # the round help button opens these pages, so every pack must carry them (and the config must point at them)
    how = (packs / "external_01" / "media" / "how_it_works.html").read_text(encoding="utf-8")
    assert "Welcome to Blue Cart Check" in how and 'href="/annotate"' in how and "<form" not in how
    demo = (packs / "external_01" / "media" / "demo" / "index.html").read_text(encoding="utf-8")
    assert "<video" not in demo and "not in this pack" in demo          # packs leave the big video out
    config_text = (packs / "external_01" / "config.yaml").read_text()
    assert "/media/how_it_works.html" in config_text and "/media/demo/index.html" in config_text
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


def test_agreement_reads_save_file_when_export_is_stale(tmp_path):
    """Potato's export can lag; labels that are only in user_state.json must still be counted."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("compute_agreement", REPO / "scripts" / "compute_agreement.py")
    ca = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ca)

    out = tmp_path / "returned" / "external_01" / "annotation_output"
    (out / "exports" / "jsonl").mkdir(parents=True)
    (out / "ann1").mkdir()
    # export only has the first item, and with an older answer
    (out / "exports" / "jsonl" / "annotations.jsonl").write_text(json.dumps(
        {"instance_id": "bcc_00001", "user_id": "ann1", "labels": {"label": {"accepted": "accepted"}}}) + "\n")
    (out / "ann1" / "user_state.json").write_text(json.dumps({
        "user_id": "ann1",
        "instance_id_to_label_to_value": {
            "bcc_00001": [[{"schema": "label", "name": "not_accepted"}, "not_accepted"],
                          [{"schema": "reason", "name": "material"}, "material"]],
            "bcc_00002": [[{"schema": "label", "name": "cannot_determine"}, "cannot_determine"]],
        }}))
    df = ca.load(tmp_path / "returned").set_index("id")
    assert len(df) == 2
    assert df.loc["bcc_00001", "label"] == "not_accepted" and df.loc["bcc_00001", "reason"] == "material"
    assert df.loc["bcc_00002", "label"] == "cannot_determine"


def test_labeling_time_from_potato_log():
    """Time per item = load -> last action, summed over visits; long breaks are ignored."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("labeling_time", REPO / "scripts" / "labeling_time.py")
    lt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lt)
    events = [
        {"timestamp": 100.0, "target": "instance_load"},
        {"timestamp": 104.0, "target": "key:3"},
        {"timestamp": 105.0, "target": "next"},            # first visit: 5 s
        {"timestamp": 300.0, "target": "instance_load"},
        {"timestamp": 302.0, "target": "key:1"},            # second visit: 2 s
        {"timestamp": 900.0, "target": "instance_load"},
        {"timestamp": 1500.0, "target": "next"},           # 600 s: a break, ignored
    ]
    assert lt.item_seconds(events, max_seconds=120) == (7.0, 1)


def test_show_labels_writes_table_and_review_page(tmp_path):
    """show_labels.py turns returned annotation_output folders into a table and a review page."""
    out = tmp_path / "returned" / "p1" / "annotation_output" / "ann1"
    out.mkdir(parents=True)
    (out / "user_state.json").write_text(json.dumps({"user_id": "ann1", "instance_id_to_label_to_value": {
        "bcc_00001": [[{"schema": "label", "name": "accepted"}, "accepted"]]}}))
    out2 = tmp_path / "returned" / "p2" / "annotation_output" / "ann2"
    out2.mkdir(parents=True)
    (out2 / "user_state.json").write_text(json.dumps({"user_id": "ann2", "instance_id_to_label_to_value": {
        "bcc_00001": [[{"schema": "label", "name": "not_accepted"}, "not_accepted"]]}}))
    text = run(REPO, "scripts/show_labels.py", "--returned", str(tmp_path / "returned"))
    assert "disagree" in text
    rows = list(csv.DictReader(open(tmp_path / "returned" / "labels_table.csv")))
    assert rows == [{"id": "bcc_00001", "ann1": "accepted", "ann2": "not_accepted"}]
    assert "only disagreements" in (tmp_path / "returned" / "labels_review.html").read_text()


def test_two_step_answers_become_one_label(tmp_path):
    """Step 1 (cart) + Step 2 (condition) -> one of the four labels; a stale Step 2 answer is ignored."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("compute_agreement", REPO / "scripts" / "compute_agreement.py")
    ca = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ca)
    assert ca.derive_label("blue_cart", "ready") == "accepted"
    assert ca.derive_label("blue_cart", "needs_prep") == "accepted_after_prep"
    assert ca.derive_label("blue_cart", "ruined") == "not_accepted"
    assert ca.derive_label("blue_cart", "cannot_tell") == "cannot_determine"
    assert ca.derive_label("not_blue_cart", "") == "not_accepted"
    assert ca.derive_label("cannot_tell", "") == "cannot_determine"
    assert ca.derive_label("blue_cart", "") == ""          # Step 2 missing: unfinished

    def pick(**answers):
        return [[{"schema": q, "name": a}, a] for q, a in answers.items()]
    out = tmp_path / "returned" / "p1" / "annotation_output" / "ann1"
    out.mkdir(parents=True)
    (out / "user_state.json").write_text(json.dumps({"user_id": "ann1", "instance_id_to_label_to_value": {
        "bcc_00001": pick(cart="blue_cart", condition="needs_prep", reason="bagged"),
        "bcc_00002": pick(cart="not_blue_cart", condition="ready"),     # changed mind: old Step 2 answer left behind
        "bcc_00003": pick(cart="blue_cart"),                            # Step 2 not answered yet
        "bcc_00004": pick(label="accepted"),                            # older one-question format
    }}))
    df = ca.load(tmp_path / "returned").set_index("id")
    assert dict(df.label) == {"bcc_00001": "accepted_after_prep", "bcc_00002": "not_accepted", "bcc_00004": "accepted"}
    assert df.loc["bcc_00002", "condition"] == "" and df.loc["bcc_00001", "reason"] == "bagged"


def test_sourced_images_keep_original_author_and_get_credit_rows(repo):
    """Images we did not take: random sample, original author in the manifest, one credit row each."""
    args = ["scripts/prepare_images.py", "--input", "data/raw/t", "--source", "realwaste",
            "--source-url", "https://example.org/dataset", "--license", "CC-BY-NC-SA-4.0",
            "--attribution", "Original Author", "--sample", "7", "--seed", "1",
            "--category-set", "paper", "--setting", "other", "--notes", "assigned to Test Person's set"]
    run(repo, *args)
    rows = list(csv.DictReader(open(repo / "data" / "manifest.csv")))
    credits = list(csv.DictReader(open(repo / "data" / "attribution.csv")))
    assert len(rows) == 7 and len(credits) == 7
    assert {r["attribution"] for r in rows} == {"Original Author"} and {r["source"] for r in rows} == {"realwaste"}
    assert all("assigned to Test Person" in r["notes"] for r in rows)
    assert [c["id"] for c in credits] == [r["id"] for r in rows]
    assert all(c["title"].startswith("cup") and c["author"] == "Original Author" for c in credits)
    assert "label" not in rows[0] and not Image.open(repo / "data" / rows[0]["image_path"]).info.get("exif")
    # a sourced batch without the original author's name is refused
    bad = subprocess.run([sys.executable, "scripts/prepare_images.py", "--input", "data/raw/t", "--source", "realwaste",
                          "--category-set", "paper", "--setting", "other"], cwd=repo, capture_output=True, text=True)
    assert bad.returncode != 0 and "ORIGINAL author" in bad.stderr


def test_assign_sets_divides_sourced_photos_by_kind():
    """Open-dataset photos go to the member who owns that kind of item; team photos stay with their photographer."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("assign_sets", REPO / "scripts" / "assign_sets.py")
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)

    rows, credits = [], {}
    def add(i, source, title, attribution="Someone"):
        rows.append({"id": f"bcc_{i:05d}", "source": source, "attribution": attribution, "notes": ""})
        credits[f"bcc_{i:05d}"] = {"title": title}
    for i in range(3):
        add(i, "team", f"cable{i}.jpg", attribution="Ian Slackta")
    for i in range(3, 7):
        add(i, "realwaste", f"Cardboard_{i}.jpg")
    for i in range(7, 11):
        add(i, "realwaste", f"Miscellaneous Trash_{i}.jpg")
    for i in range(11, 15):
        add(i, "kaggle_drinking_waste", f"PET{i}.jpg")
    for i in range(15, 17):
        add(i, "wikimedia", f"tub0{i}.jpg")

    result = a.assign(rows, credits, {"hina": 4, "ian": 5, "daud": 2, "khurram": 6})
    who = lambda ids: {result[f"bcc_{i:05d}"] for i in ids}
    assert who(range(3, 7)) == {"hina"}                      # cardboard -> Hina
    assert who(range(7, 9)) == {"ian"}                       # Ian: 3 own + 2 trash = 5
    assert who(range(15, 17)) == {"daud"}                    # Wikimedia containers -> Daud
    assert who(range(11, 15)) == {"khurram"} and who(range(9, 11)) == {"khurram"}   # the rest -> Khurram
    assert all(f"bcc_{i:05d}" not in result for i in range(3))                     # team photos are not reassigned

    with pytest.raises(SystemExit):                          # targets that leave photos over are refused
        a.assign(rows, credits, {"hina": 4, "ian": 5, "daud": 2, "khurram": 5})
    with pytest.raises(SystemExit):                          # Hina cannot be given more paper than exists
        a.assign(rows, credits, {"hina": 10, "ian": 3, "daud": 2, "khurram": 2})


def test_hf_space_folder_puts_the_shared_photos_first(repo):
    """Hosted version: the photos Potato's own sampler shares with everyone must be the first lines of the list."""
    import yaml
    from potato.server_utils.overlap_sampler import apply_overlap_sample

    run(repo, "scripts/prepare_images.py", "--input", "data/raw/t", "--photographer", "Test Person",
        "--category-set", "disposables", "--setting", "bin_station")
    run(repo, "scripts/make_hf_space.py", "--shared", "3", "--per-annotator", "5", "--annotators", "4",
        "--labels-per-photo", "2", "--backup-repo", "someone/some-dataset")
    space = repo / "deploy" / "hf_space"
    lines = [json.loads(l)["id"] for l in open(space / "data" / "items.jsonl")]
    shared = json.load(open(space / "shared_ids.json"))["shared_ids"]
    assert len(lines) == 30 and lines[:3] == shared

    config = yaml.safe_load(open(space / "config.yaml"))          # the generated config is valid YAML
    assert config["require_password"] is True and config["max_annotations_per_user"] == 5
    assert config["num_annotators_per_item"]["default"] == 2     # every non-shared photo is labeled twice
    assert config["huggingface_backup"] == {"enabled": True, "repo_id": "someone/some-dataset", "repo_type": "dataset",
                                            "private": True, "schedule_minutes": 5}
    assert "sdk: docker" in (space / "README.md").read_text() and (space / "Dockerfile").exists()
    assert (space / "media" / "guidelines.html").exists() and (space / "welcome.html").exists()
    assert (space / "media" / "how_it_works.html").exists()
    assert "<video" in (space / "media" / "demo" / "index.html").read_text(encoding="utf-8")   # hosted: video kept

    # ask Potato itself which photos it would share, using a minimal stand-in for its item list
    class FakeItem:
        def __init__(self): self.meta = {}
        def get_metadata(self, key): return self.meta.get(key)
        def add_metadata(self, key, value): self.meta[key] = value
    class FakeItems:
        random_seed = 42
        items = {i: FakeItem() for i in lines}
        def get_instance_ids(self): return list(self.items)
        def get_item(self, i): return self.items[i]
    picked = apply_overlap_sample(FakeItems(), config)
    assert set(picked) == set(shared) and set(picked.values()) == {4}
