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
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", ".venv", "images", "packs", "returned", "course", "raw", "figures", "deploy"))
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
        # a reason that was chosen and then CLEARED in the tool: Potato keeps a "not selected" marker (value false)
        "bcc_00005": pick(cart="blue_cart", condition="ready") + [[{"schema": "reason", "name": "material"}, False]],
    }}))
    df = ca.load(tmp_path / "returned").set_index("id")
    assert dict(df.label) == {"bcc_00001": "accepted_after_prep", "bcc_00002": "not_accepted", "bcc_00004": "accepted", "bcc_00005": "accepted"}
    assert df.loc["bcc_00002", "condition"] == "" and df.loc["bcc_00001", "reason"] == "bagged"
    assert df.loc["bcc_00005", "reason"] == ""                       # the cleared reason is not counted


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
    assert config["assignment_strategy"] == "least_annotated" and config["instance_reclaim"] == {"enabled": True, "timeout_hours": 24}
    assert config["huggingface_backup"] == {"enabled": True, "repo_id": "someone/some-dataset", "repo_type": "dataset",
                                            "private": True, "schedule_minutes": 5}
    assert "sdk: docker" in (space / "README.md").read_text() and (space / "Dockerfile").exists()
    assert (space / "media" / "guidelines.html").exists() and (space / "welcome.html").exists()

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


def test_adjudication_workbook_round_trip(tmp_path):
    """Disputed photos come first in the workbook, and a decision typed into it beats the majority when merged back."""
    import openpyxl
    returned = tmp_path / "returned"; returned.mkdir()
    labels = {"bcc_00001": ["not_accepted"] * 3,                                     # unanimous
              "bcc_00002": ["accepted"] * 3 + ["not_accepted"] * 2,                  # weak majority (60%)
              "bcc_00003": ["accepted", "not_accepted"]}                             # tie
    with (returned / "annotations_long.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["photo_id", "person", "account", "cart", "condition", "reason", "final_label"])
        for pid, labs in labels.items():
            for i, lab in enumerate(labs):
                w.writerow([pid, f"p{i}", f"p{i}", "blue_cart" if lab == "accepted" else "not_blue_cart", "", "material" if i == 0 else "", lab])
    for script in ("agreement_phase2.py", "make_adjudication_workbook.py"):
        subprocess.run([sys.executable, f"scripts/{script}", "--returned", str(returned)] + (["--no-copy"] if script.startswith("make") else []),
                       cwd=REPO, check=True, capture_output=True, text=True)
    book = returned / "adjudication.xlsx"
    wb = openpyxl.load_workbook(book); ws = wb["Decide"]
    head = [c.value for c in ws[1]]; col = {h: i + 1 for i, h in enumerate(head)}
    assert [ws.cell(row=r, column=1).value for r in (2, 3, 4)] == ["bcc_00003", "bcc_00002", "bcc_00001"]
    assert [ws.cell(row=r, column=col["needs_decision"]).value for r in (2, 3, 4)] == ["YES", "YES", None]
    assert ws.cell(row=2, column=col["reviewer"]).value and ws.cell(row=4, column=col["reviewer"]).value is None
    assert len(ws._images) == 3 and ws.cell(row=2, column=col["full photo"]).hyperlink.target.endswith("bcc_00003.jpg")
    assert wb["Summary"]["A1"].value == "photos" and wb["Read me"]["A1"].value.startswith("Blue Cart Check")

    ws.cell(row=2, column=col["team_decision"]).value = "accepted"          # the tie gets a team decision
    ws.cell(row=4, column=col["team_decision"]).value = "exclude_photo"     # a unanimous photo is thrown out
    ws._images = []      # openpyxl cannot re-save pictures it loaded (Excel can); the merge never reads them
    wb.save(book)
    out = subprocess.run([sys.executable, "scripts/merge_adjudication.py", "--returned", str(returned), "--strict"],
                         cwd=REPO, check=True, capture_output=True, text=True).stdout
    gold = {r["photo_id"]: r for r in csv.DictReader((returned / "gold_labels.csv").open())}
    assert (gold["bcc_00003"]["label"], gold["bcc_00003"]["source"]) == ("accepted", "team")
    assert (gold["bcc_00002"]["label"], gold["bcc_00002"]["source"]) == ("accepted", "majority")
    assert (gold["bcc_00001"]["label"], gold["bcc_00001"]["source"]) == ("exclude_photo", "team")
    assert "unresolved" not in out

    # a second copy with a different decision for the same photo = conflict, and --strict refuses
    other = returned / "copy.xlsx"; ws.cell(row=2, column=col["team_decision"]).value = "not_accepted"; wb.save(other)
    res = subprocess.run([sys.executable, "scripts/merge_adjudication.py", "--returned", str(returned), "--workbook", str(book), str(other), "--strict"],
                         cwd=REPO, capture_output=True, text=True)
    assert res.returncode == 1 and "conflicting decisions" in res.stdout
    gold = {r["photo_id"]: r for r in csv.DictReader((returned / "gold_labels.csv").open())}
    assert gold["bcc_00003"]["source"] == "unresolved"


def test_label_distribution_chart(tmp_path):
    """The chart comes from the majority preview until gold labels exist, then from the gold labels."""
    returned = tmp_path / "returned"; returned.mkdir(); out = tmp_path / "fig.png"
    cmd = [sys.executable, "scripts/label_distribution.py", "--returned", str(returned), "--out", str(out)]
    with (returned / "majority_labels.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["photo_id", "n_labels", "majority_label", "status", "share", "votes", "team_decision"])
        for i, lab in enumerate(["accepted"] * 5 + ["not_accepted"] * 3 + ["cannot_determine", ""]):
            w.writerow([f"bcc_{i:05d}", 3, lab, "tie" if not lab else "majority", "0.67", "", ""])
    text = subprocess.run(cmd, cwd=REPO, check=True, capture_output=True, text=True).stdout
    assert out.exists() and Image.open(out).size[0] > 1000
    assert "majority vote" in text and "| accepted | 5 | 55.6% |" in text and "undecided (tie) | 1" in text
    with (returned / "gold_labels.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["photo_id", "label", "source", "status", "note"])
        for i, lab in enumerate(["accepted"] * 4 + ["not_accepted"] * 4 + ["exclude_photo", "accepted_after_prep"]):
            w.writerow([f"bcc_{i:05d}", lab, "team", "majority", ""])
    text = subprocess.run(cmd, cwd=REPO, check=True, capture_output=True, text=True).stdout
    assert "adjudicated labels" in text and "1 excluded" in text and "| accepted | 4 | 44.4% |" in text


def test_kaggle_files_split_and_scoring(tmp_path):
    """Group-safe stratified split, the four Kaggle files, and the scorer gives the solution a perfect score."""
    returned = tmp_path / "returned"; returned.mkdir(); out = tmp_path / "kaggle"
    labels = ["accepted"] * 20 + ["not_accepted"] * 12 + ["accepted_after_prep"] * 8 + ["cannot_determine"] * 8
    with (returned / "gold_labels.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["photo_id", "label", "source", "status", "note"])
        for i, lab in enumerate(labels):
            w.writerow([f"bcc_{i:05d}", lab, "majority", "majority", ""])
        w.writerow(["bcc_00099", "exclude_photo", "team", "tie", "two items"])
    with (tmp_path / "manifest.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "item_group_id", "source"])
        for i in range(len(labels)):
            w.writerow([f"bcc_{i:05d}", "G-pair" if i in (0, 1, 2) else f"G-{i}", "team"])   # one 3-photo group
        w.writerow(["bcc_00099", "G-99", "team"])
    text = subprocess.run([sys.executable, "scripts/make_kaggle_files.py", "--returned", str(returned), "--manifest", str(tmp_path / "manifest.csv"),
                           "--out", str(out), "--no-images"], cwd=REPO, check=True, capture_output=True, text=True).stdout
    assert text.startswith("FINAL: 48 photos") and "item groups split across sets: 0" in text
    train = list(csv.DictReader((out / "public" / "train.csv").open())); test = list(csv.DictReader((out / "public" / "test.csv").open()))
    sol = list(csv.DictReader((out / "private" / "solution.csv").open())); sample = list(csv.DictReader((out / "public" / "sample_submission.csv").open()))
    assert len(train) + len(test) == 48 and "bcc_00099" not in {r["id"] for r in train + test}
    assert [r["id"] for r in test] == [r["id"] for r in sol] == [r["id"] for r in sample] and list(sol[0]) == ["id", "label", "Usage"]
    assert {r["Usage"] for r in sol} == {"Public", "Private"} and {r["label"] for r in sample} == {"accepted"}
    assert "label" not in test[0]                                                 # test.csv carries no labels
    splits = {r["id"]: r["split"] for r in csv.DictReader((out / "private" / "splits.csv").open())}
    assert len({splits[f"bcc_0000{i}"] for i in (0, 1, 2)}) == 1                   # the group stays together
    assert {r["label"] for r in sol} == set(labels)                                # every class reaches the test set
    scorer = [sys.executable, "scripts/score_submission.py", "--solution", str(out / "private" / "solution.csv")]
    perfect = subprocess.run(scorer + [str(out / "private" / "solution.csv")], cwd=REPO, check=True, capture_output=True, text=True).stdout
    assert "Public 1.0000   Private 1.0000   All 1.0000" in perfect
    majority = subprocess.run(scorer + [str(out / "public" / "sample_submission.csv")], cwd=REPO, check=True, capture_output=True, text=True).stdout
    assert "recall on not_accepted 0.0000" in majority and "All 1.0000" not in majority
    bad = subprocess.run(scorer + [str(out / "public" / "test.csv")], cwd=REPO, capture_output=True, text=True)
    assert bad.returncode != 0 and "no column 'label'" in bad.stdout + bad.stderr


def _tiny_kaggle(tmp_path, flip=None):
    """A 48-photo gold file + manifest -> make_kaggle_files --no-images; returns (out folder, printed text)."""
    returned = tmp_path / "returned"; returned.mkdir(exist_ok=True); out = tmp_path / "kaggle"
    labels = ["accepted"] * 20 + ["not_accepted"] * 12 + ["accepted_after_prep"] * 8 + ["cannot_determine"] * 8
    if flip is not None:
        labels[flip] = "not_accepted"
    with (returned / "gold_labels.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["photo_id", "label", "source", "status", "note"])
        for i, lab in enumerate(labels):
            w.writerow([f"bcc_{i:05d}", lab, "majority", "majority", ""])
    with (tmp_path / "manifest.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "item_group_id", "source"])
        for i in range(len(labels)):
            w.writerow([f"bcc_{i:05d}", f"G-{i}", "team"])
    text = subprocess.run([sys.executable, "scripts/make_kaggle_files.py", "--returned", str(returned), "--manifest", str(tmp_path / "manifest.csv"),
                           "--out", str(out), "--no-images"], cwd=REPO, check=True, capture_output=True, text=True).stdout
    return out, text


def test_baselines_run_on_any_kaggle_folder_and_the_split_is_reused(tmp_path):
    out, text = _tiny_kaggle(tmp_path)
    assert "new split, seed 42" in text
    first = {r["id"]: (r["split"], r["usage"]) for r in csv.DictReader((out / "private" / "splits.csv").open())}
    out, text = _tiny_kaggle(tmp_path, flip=0)                       # a label changed after adjudication: same split
    assert "split reused" in text
    second = {r["id"]: (r["split"], r["usage"]) for r in csv.DictReader((out / "private" / "splits.csv").open())}
    assert first == second
    sol = {r["id"]: r["label"] for r in csv.DictReader((out / "private" / "solution.csv").open())}
    if "bcc_00000" in sol:
        assert sol["bcc_00000"] == "not_accepted"                     # the new label went into the files

    results = tmp_path / "results.csv"
    text = subprocess.run([sys.executable, "models/baseline_dummy.py", "--kaggle", str(out), "--results", str(results)],
                          cwd=REPO, check=True, capture_output=True, text=True).stdout
    rows = list(csv.DictReader(results.open()))
    assert len(rows) == 6 and {r["model"] for r in rows} == {"majority", "random_uniform", "random_by_share"}
    assert "best dummy on validation" in text and (out / "submissions" / "majority.csv").exists()

    parts = tmp_path / "parts"; parts.mkdir()                        # LLM answers: half the test ids, one bad label
    ids = list(sol)
    with (parts / "part_00.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "label"])
        for pid in ids[: len(ids) // 2]:
            w.writerow([pid, sol[pid]])
        w.writerow([ids[-1], "maybe"])
    text = subprocess.run([sys.executable, "models/baseline_llm.py", "--parts", str(parts), "--kaggle", str(out), "--results", str(results), "--name", "llm_test"],
                          cwd=REPO, check=True, capture_output=True, text=True).stdout
    assert "WARNING 1 answers are not a valid label" in text and f"{len(ids) // 2} of {len(ids)} test photos" in text
    llm = [r for r in csv.DictReader(results.open()) if r["model"] == "llm_test"]
    assert len(llm) == 1 and llm[0]["macro_f1"] == "1.0000" and "partial" in llm[0]["notes"]


def test_merge_reads_one_decision_column_per_member(tmp_path):
    """The team gave each member a column ("team_decision <name>") for the ties: the label most members chose is
    the decision, members split evenly stay unresolved, and a photo nobody decided keeps its majority label."""
    import importlib.util
    from pathlib import Path
    from openpyxl import Workbook
    script = Path(__file__).resolve().parents[1] / "scripts" / "merge_adjudication.py"
    spec = importlib.util.spec_from_file_location("merge_adjudication", script)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    wb = Workbook(); ws = wb.active; ws.title = "Decide"
    ws.append(["photo_id", "status", "majority_label", "team_decision khurram", "note", "team_decision Hina", "team_decision Daud"])
    ws.append(["bcc_1", "tie", None, "accepted", None, None, None])                      # one member decided
    ws.append(["bcc_2", "tie", None, "accepted", None, "not_accepted", "not_accepted"])  # two against one
    ws.append(["bcc_3", "tie", None, "accepted", None, "not_accepted", None])            # split evenly
    ws.append(["bcc_4", "majority", "not_accepted", None, None, None, None])             # nobody decided
    book = tmp_path / "ties.xlsx"; wb.save(book)
    rows, problems = mod.merge({str(book): mod.read_decisions(book)})
    got = {r["photo_id"]: (r["label"], r["source"]) for r in rows}
    assert got == {"bcc_1": ("accepted", "team"), "bcc_2": ("not_accepted", "team"),
                   "bcc_3": ("", "unresolved"), "bcc_4": ("not_accepted", "majority")}
    assert len(problems) == 1 and "bcc_3" in problems[0]
