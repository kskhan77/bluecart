# Phase 1 Requirements (distilled from the handout)

Source: `docs/course/ARI410-510_Project_Phase1a_Group.pdf` ("ARI 410/510 Project Phase 1: Data Collection & Annotation Setup")
Canvas: *Project Phase 1a: Annotation Prep (Group)*, 100 pts, **due Tue Oct 6 2026, 2:30pm (before class)**. One submission counts for the whole group.

## Steps the handout requires
1. **Collect unlabeled data** that a person *could* label by looking at it.
2. **Annotation guidelines + interface**; label a portion yourselves (internal annotation).
3. **Present** the task + annotation setup to the class (≤ 5 min).

## Requirement → where it lives in this repo → status
Status column last updated **Oct 6, 2026 (morning)**. ✅ done · 🟡 partly · ❌ not started.

| # | requirement (handout §) | file / action | owner | status |
|---|---|---|---|---|
| R1 | Data stored in an easy-to-access way: folder of files or csv/json (§2) | `data/images/` + `data/manifest.csv` | Daud | 🟡 617 photos: 77 team photos (Ian's set only) + 540 from two existing datasets and Wikimedia Commons. Daud's, Hina's and Khurram's own photo sets are still missing |
| R2 | Respect terms of service; check source licenses (§2) | credits in `data/attribution.csv`; RealWaste kept as CC BY-NC-SA 4.0 | Daud | ✅ 540 sourced images, each with a credit row. RealWaste's NC-SA license is now the dataset license |
| R3 | Choose a dataset license (§2) | `LICENSE.md` (CC BY-NC-SA 4.0) | Daud | ✅ locked Oct 6 so the RealWaste images can stay |
| R4 | README: source, **reproducible collection procedure**, format, what one instance is, total count, collection dates, sampling, missing data (§2) | `README.md` §1–4 | Daud + Khurram | ✅ 617 images, 77 team / 540 sourced, dates 2026-09-28 to 2026-10-04 |
| R5 | README: **estimated time to label one item** (time yourself during internal annotation) (§2) | `README.md` §5, `scripts/labeling_time.py` | Hina (pilot) | ✅ median 6 s on 160 photos (Oct 5); plan with 15–20 s for a first-time annotator |
| R6 | Guidelines: concise overview of the job (§3.1) | `annotation/guidelines.md` §1 | Hina | ✅ draft |
| R7 | Guidelines: label set with short descriptions (§3.1) | §2 | Hina | ✅ draft |
| R8 | Guidelines: unambiguous rules that still need human judgment, not rules that "solve" the task (§3.1) | §3–4 | Hina | ✅ v1.0 locked Oct 6, including cups and rigid vs foam clamshells |
| R9 | Guidelines: ≥1 example per label with an explanation of why (and why not the others) (§3.1) | §5 | Hina | ✅ 12 written examples covering all four labels. Photos are not embedded |
| R10 | Guidelines: contact info (§3.1) | §7 | Hina | ✅ emails plus https://discord.gg/2t2DSNyBm |
| R11 | Understandable without a meeting; extra scaffolding for expert-ish tasks (§3.1) | watch-out table, checklist, rules cheat sheet inside the tool | Hina | 🟡 not yet tried by someone outside the team |
| R12 | **Real annotation interface** (not a bare spreadsheet), one item at a time, structured output (§3.2) | Potato: `annotation/potato/config.yaml` | Hina | ✅ tested in a browser |
| R13 | Complete instructions to use it: install, run, **what output file, how to send it back**; test end to end yourself (§3.2) | `annotation/HOW_TO_ANNOTATE.md` | Hina | ✅ written and tested; still needs one person who did not build it |
| R14 | If custom tool built with Claude Code: document the prompts, what it is, how it works (§3.2, §6f) | we use Potato (configured, not custom-built); `docs/AI_USE_LOG.md` records the AI help | Khurram | ✅ log is current |
| R15 | **More than one annotation per item for some items** (§3.3) | agreement set via `make_annotation_packs.py` | Hina | 🟡 mechanism works; final sizes wait for the full dataset |
| R16 | Plan around about 5 external annotators × 1 h each + ≥1 internal annotator (≥1 h); justify the redundancy vs. coverage trade-off (§3.3) | `README.md` §6 | Hina + Khurram | ✅ 30 shared + 170 each, two labels per other photo, justified from the 6 s median |
| R17 | Internal annotation started early, using the **final** scheme (§3.3, §4) | pilot → lock v1.0 | all | 🟡 rules locked Oct 6. Pilot so far is about 30 minutes (Hina 21, Ian 7, Khurram 2), short of one person-hour |
| R18 | "Changes from proposal" note, even if nothing changed (§4) | `CHANGES_FROM_PROPOSAL.md` | Khurram | ✅ placeholders removed Oct 6 |
| R19 | Presentation: task + why + example; descriptive stats (count, format, source, a distribution or two, per-item time); live look at the interface + guidelines (§5) | slides (`docs/PHASE1_CHECKLIST.md` outline); backup screenshots and demo video in `docs/figures/` | Khurram + all | 🟡 8-slide draft exists (https://claude.ai/artifact/Bqw5rtb5iC3hisUafkBFWf, private until shared). The labeling time on it is from a 2-photo test; the model check promised in the proposal is not in it; not rehearsed |

## Deliverables (§6), all 3 required for full credit
| # | deliverable | status |
|---|---|---|
| 1 | **Canvas:** PDF *or* GitHub link containing (a) dataset link with UM-student access, (b) dataset description (README), (c) license, (d) annotation instructions, (e) changes-from-proposal note, (f) custom-platform note (only if applicable) | ❌ no GitHub repo or Drive link yet |
| 2 | **Google Form:** annotation request | 🟡 answers drafted in `docs/GOOGLE_FORM_ANSWERS.md`; the form itself needs a UM sign-in and is not submitted |
| 3 | **Discord** `#project-annotation-tasks`: post the slides (PDF or link) and **present in class on Oct 6** | ❌ |

## Grading-risk checklist
- [ ] Dataset link opens for a UM account that isn't on the team
- [ ] No unlabeled-data violation: no pre-existing labels used as our labels
- [ ] Guidelines don't need us in the room
- [ ] Interface tested by someone who didn't build it
- [ ] Agreement set exists (otherwise Phase 2 is impossible)
- [ ] Talk ≤ 5:00 with a live demo that doesn't depend on Wi-Fi luck (have screenshots as backup)
