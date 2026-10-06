# Annotation request form: answers ready to paste

**Form link (from the handout, Section 6):** https://forms.gle/8shoZUUuj3fhyQVVA

The form opens only with a UM Google account, so its exact questions could not be read when this sheet was written.
The answers below cover what an annotation request normally asks. Match them to the questions you see.
Replace every `[...]` before you submit. One submission for the whole team.

---

## Team

| | |
|---|---|
| Group | Group 2 |
| Project name | Blue Cart Check |
| Section | ARI 510 (all four members) |
| Members | Daud Jan (dauds@umich.edu), Hina Kramer (hinak@umich.edu), Khurram Shafique (kshafiqu@umich.edu), Ian Slackta (slackta@umich.edu) |
| Contact for annotators | Khurram Shafique, kshafiqu@umich.edu · Hina Kramer, hinak@umich.edu · project Discord https://discord.gg/2t2DSNyBm |

## Task

**Title:** Blue Cart Check: does this item go in Flint's blue recycling cart?

**One-sentence description:**
Annotators look at one photo of an everyday item at a time and answer two short questions, so that each photo gets one of four labels under the City of Flint recycling rules.

**Longer description:**
Each item is a JPEG photo of a single everyday item (a can, a box, a cable, a cup). Step 1 asks what kind of item it is: a kind Flint takes in the blue cart, a kind it never takes, or can't tell. Step 2 appears only for blue cart items and asks about its state: ready, needs prep first, ruined, or can't see enough. From the two answers we compute one of four labels: `accepted`, `accepted_after_prep`, `not_accepted`, `cannot_determine`. An optional "reason" can also be clicked. The rules are shown on screen for every photo, and the full guidelines open from a button in the tool.

**Type of data:** Images (JPEG photos, long side 512 px).

**Type of annotation:** Classification. Two single-choice questions per photo, plus one optional single-choice question.

## Size and time

| | |
|---|---|
| Photos in the dataset now | 617 (more of our own photos are still being added) |
| Photos per annotator | 200 = 30 shared photos that every annotator labels + the next 170 photos that still need a label. Every photo is labeled by 2 people. |
| Time per photo | About 6 seconds median for us (160-photo pilot on Oct 5, from `python scripts/labeling_time.py`). We plan with 15 to 20 seconds for a first-time annotator, so 200 photos is about one hour. |
| Time per annotator | About 1 hour, including reading the welcome page |
| External annotators requested | 6 (the handout's estimate for our class size: each student annotates for two other teams) |
| Internal annotators | All 4 team members, on the same shared link |

## What annotators need

- A computer with **Python 3.9 or newer** and a web browser. Everything runs on their own computer. Nothing is uploaded.
- No special knowledge. They do not need to know Flint or recycling rules: the rules are on screen.
- No sensitive content: everyday items only, no people.

## How they do it

1. Unzip the pack we send (`bluecartcheck_external_XX.zip`).
2. In that folder run `pip install potato-annotation==2.9.4`, then `potato start config.yaml -p 8000`.
3. Open http://localhost:8000, type their uniqname, read the welcome page, and label for about one hour.
4. Zip the `annotation_output` folder and send it to kshafiqu@umich.edu or by Discord DM.

Full instructions are in `annotation/HOW_TO_ANNOTATE.md`, which is also inside every pack.

## Links to paste

| | |
|---|---|
| Annotation guidelines | `[GitHub link to annotation/guidelines.md]` |
| Setup instructions | `[GitHub link to annotation/HOW_TO_ANNOTATE.md]` |
| Dataset | `[Google Drive link, shared with "Anyone at University of Michigan with the link"]` |
| Annotator packs | `[Google Drive folder with the six zip files]` |
| Presentation slides | `[link or PDF posted in #project-annotation-tasks]` |

## Before you submit

- [x] Guidelines v1.0 are locked (Oct 6). The Discord contact is https://discord.gg/2t2DSNyBm
- [x] The timed pilot is done: median 6 seconds on 160 photos. The form uses 15 to 20 seconds for a first-time annotator.
- [x] The hosted tool is 30 shared photos, then 170 more, 200 per person, two labels on every other photo.
- [ ] Replace the `[...]` links below with a UM Drive or GitHub link before submitting. The form needs a UM Google sign-in, so it is not submitted from this repo.
- [x] RealWaste stays in the dataset. The dataset license is CC BY-NC-SA 4.0.
