# Phase 1 Requirements (distilled from the handout)

Source: `docs/course/ARI410-510_Project_Phase1a_Group.pdf` ("ARI 410/510 Project Phase 1: Data Collection & Annotation Setup")
Canvas: *Project Phase 1a: Annotation Prep (Group)*, 100 pts, **due Tue Oct 6 2026, 2:30pm (before class)**. One submission counts for the whole group.

## Steps the handout requires
1. **Collect unlabeled data** that a person *could* label by looking at it.
2. **Annotation guidelines + interface**; label a portion yourselves (internal annotation).
3. **Present** the task + annotation setup to the class (≤ 5 min).

## Requirement → where it lives in this repo
| # | requirement (handout §) | file / action | owner |
|---|---|---|---|
| R1 | Data stored in an easy-to-access way: folder of files or csv/json (§2) | `data/images/` + `data/manifest.csv` | Daud |
| R2 | Respect terms of service; check source licenses (§2) | CC0/CC BY only, `data/attribution.csv` | Daud |
| R3 | Choose a dataset license (§2) | `LICENSE.md` (CC BY 4.0) | Daud |
| R4 | README: source, **reproducible collection procedure**, format, what one instance is, total count, collection dates, sampling, missing data (§2) | `README.md` §1–4 | Daud + Khurram |
| R5 | README: **estimated time to label one item** (time yourself during internal annotation) (§2) | `README.md` §5 | Hina (pilot) |
| R6 | Guidelines: concise overview of the job (§3.1) | `annotation/guidelines.md` §1 | Hina |
| R7 | Guidelines: label set with short descriptions (§3.1) | §2 | Hina |
| R8 | Guidelines: unambiguous rules that still need human judgment, not rules that "solve" the task (§3.1) | §4 | Hina |
| R9 | Guidelines: ≥1 example per label with an explanation of why (and why not the others) (§3.1) | §5 (add real photos) | Hina |
| R10 | Guidelines: contact info (§3.1) | §7 | Hina |
| R11 | Understandable without a meeting; extra scaffolding for expert-ish tasks (§3.1) | watch-out table + checklist | Hina |
| R12 | **Real annotation interface** (not a bare spreadsheet), one item at a time, structured output (§3.2) | Potato: `annotation/potato/config.yaml` | Hina |
| R13 | Complete instructions to use it: install, run, **what output file, how to send it back**; test end to end yourself (§3.2) | `annotation/HOW_TO_ANNOTATE.md` | Hina |
| R14 | If custom tool built with Claude Code: document the prompts, what it is, how it works (§3.2, §6f) | n/a (we use Potato). Keep `docs/AI_USE_LOG.md` anyway | Khurram |
| R15 | **More than one annotation per item for some items** (§3.3) | agreement set via `make_annotation_packs.py` | Hina |
| R16 | Plan around about 5 external annotators × 1 h each + ≥1 internal annotator (≥1 h); justify the redundancy vs. coverage trade-off (§3.3) | `README.md` §6 | Hina + Khurram |
| R17 | Internal annotation started early, using the **final** scheme (§3.3, §4) | pilot → lock v1.0 | all |
| R18 | "Changes from proposal" note, even if nothing changed (§4) | `CHANGES_FROM_PROPOSAL.md` | Khurram |
| R19 | Presentation: task + why + example; descriptive stats (count, format, source, a distribution or two, per-item time); live look at the interface + guidelines (§5) | slides (`docs/PHASE1_CHECKLIST.md` outline) | Khurram + all |

## Deliverables (§6), all 3 required for full credit
1. **Canvas:** PDF *or* GitHub link containing:
   - (a) dataset link with UM-student access
   - (b) dataset description (README)
   - (c) license
   - (d) annotation instructions
   - (e) changes-from-proposal note
   - (f) custom-platform note (only if applicable)
2. **Google Form:** annotation request.
3. **Discord** `#project-annotation-tasks`: post the slides (PDF or link) and **present in class on Oct 6**.

## Grading-risk checklist
- [ ] Dataset link opens for a UM account that isn't on the team
- [ ] No unlabeled-data violation: no pre-existing labels used as our labels
- [ ] Guidelines don't need us in the room
- [ ] Interface tested by someone who didn't build it
- [ ] Agreement set exists (otherwise Phase 2 is impossible)
- [ ] Talk ≤ 5:00 with a live demo that doesn't depend on Wi-Fi luck (have screenshots as backup)
