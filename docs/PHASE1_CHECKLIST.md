# Phase 1 checklist: due Tue Oct 6, 2:30 pm (before class)

Only ONE submission per team. Tick each box as you go.

## Status after the Oct 4 setup session
- [x] Repo set up in WSL (`.venv`, tests pass, git initialised locally; **not yet on GitHub**)
- [x] Ian's 77 photos processed into `data/images/` (target 200, minimum 150). Four are flagged `REVIEW:` in `manifest.csv`
- [x] Potato tested end to end in a browser (keys 1-4, next/back, save, export, timing log)
- [x] Guidelines Section 3 quotes the city and hauler rules word for word (copied Oct 4)
- [ ] **Team decisions marked ⚑ in `annotation/guidelines.md`** must be agreed before the pilot
- [ ] Photos from Daud, Hina and Khurram, plus the sourced CC0/CC-BY images, are still missing

## Sun Oct 4 (today)
- [ ] **Everyone:** send your sections by end of day (Ian ✅ done)
- [ ] **Khurram:** shoot the disposables set (`docs/SHOT_LIST_KHURRAM.md`), run `prepare_images.py`
- [ ] **Khurram:** create the GitHub repo from this folder; add teammates
- [ ] **Daud:** sourced CC0/CC-BY images + `attribution.csv`; Drive folder shared to UM ("Anyone at University of Michigan with the link: Viewer")
- [ ] **Hina:** finalize `annotation/guidelines.md` (paste exact city wording, add example photos, fill contact/channel)

## Mon Oct 5
- [ ] **Everyone:** all photos processed and in `data/images/` + `manifest.csv` (one merged manifest; Daud owns the merge)
- [ ] **Internal pilot (all 4):** each label the same ~40 images in Potato and **time it** → per-image seconds for the README
- [ ] **Lock guidelines v1.0** after the pilot (fix any rule people disagreed on)
- [ ] **Run** `python scripts/dataset_stats.py` → numbers + 2 charts for slides/README
- [ ] **Run** `python scripts/make_annotation_packs.py --agreement <A> --batch <B>`. Size A and B from the measured rate (see the box below)
- [ ] **End-to-end test:** someone who didn't build it unzips a pack, runs Potato, labels 5 images, sends back `annotation_output`
- [ ] **Fill** README `<...>` placeholders + `CHANGES_FROM_PROPOSAL.md`
- [ ] **Slides (5 min max)**, then a practice run with a timer

## Tue Oct 6, before 2:30 pm
- [ ] **Canvas:** PDF or GitHub link containing (a) dataset link, (b) description/README, (c) license, (d) annotation instructions, (e) changes note, (f) AI-use note
- [ ] **Google Form:** annotation request
- [ ] **Discord** `#project-annotation-tasks`: slides PDF/link
- [ ] **Present:** laptop ready with Potato running (`potato start config.yaml -p 8000`) for the live demo

## Sizing the annotation packs
Measured rate R = images/hour from the pilot (e.g. 10 s/image → about 300/h; leave about 15% for reading the guidelines → about 250).
- Agreement set A = about 1/3 of R (e.g. **80–100**), labeled by all 6 annotators
- Coverage batch B = R − A per annotator (e.g. **150**)
- Total labeled ≈ A + 6·B (e.g. 100 + 900 = **1,000**)

## 5-minute slide outline
1. **Title + task:** "Blue Cart Check: does this go in Flint's blue cart?" Plus one example photo.
2. **Why it matters:** UM-Flint's July 2026 single-stream switch; contamination gets loads rejected; local rules ≠ national habits.
3. **Labels + the hard cases:** the 4 labels; cup vs. tub, greasy vs. clean, bagged vs. loose.
4. **Dataset stats:** total N, team vs. sourced, per-category chart, settings, 512 px JPEG, time per image.
5. **AI model check (Ian):** a table of where the models contradicted themselves or the rules.
6. **Live demo:** Potato interface + guidelines.
7. **Ask:** "Each of you gets a zip: about 1 hour, keys 1–4, send back `annotation_output`."
