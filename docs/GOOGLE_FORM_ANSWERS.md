# Annotation request form: answers ready to paste

**Form link (from the handout, Section 6):** https://forms.gle/8shoZUUuj3fhyQVVA

The form opens only with a UM Google account, so its exact questions could not be read when this sheet was written.
The answers below cover what an annotation request normally asks. Match them to the questions you see.
One submission for the whole team. Everything below is final as of the morning of Oct 6, 2026; nothing is left to replace.

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

**Type of data:** Images (JPEG photos, long side 512 px, phone location data removed).

**Type of annotation:** Classification. Two single-choice questions per photo, plus one optional single-choice question.

**Dataset license:** CC BY-NC-SA 4.0 (360 of the photos come from RealWaste, which carries that license). Code: MIT.

## Size and time

| | |
|---|---|
| Photos in the dataset now | 648 (108 our own, 540 from open datasets). The current labeling round in the tool uses the first 617; Hina's 31 own photos, added on Oct 6, join the next round. |
| Photos per annotator | 200 = 30 shared photos that every annotator labels + the next 170 photos that still need a label. Every photo is labeled by 2 people. |
| Time per photo | About 6 seconds median for us (160-photo pilot on Oct 5, from `python scripts/labeling_time.py`). We plan with 15 to 20 seconds for a first-time annotator, so 200 photos is about one hour. |
| Time per annotator | About 1 hour, including reading the welcome page |
| External annotators requested | 6 (the handout's estimate for our class size: each student annotates for two other teams) |
| Internal annotators | All 4 team members, on the same shared link |
| Multiple annotations per item | Yes: the 30 shared photos get up to 10 labels, every other photo gets 2 |

## What annotators need

- A web browser. The tool runs online at https://bluecart.khurramshafique.com. Nothing to install and nothing to send back.
- No special knowledge. They do not need to know Flint or recycling rules: the rules are on screen, and a welcome page explains the two steps.
- No sensitive content: everyday items only, no people.
- Works on a laptop or a tablet. Keys 1 to 7 answer; on a tablet the key legend is clickable.

## How they do it

1. Open https://bluecart.khurramshafique.com, choose **Register**, pick a username (uniqname is fine) and a password.
2. Read the welcome page (one screen), then label for about one hour: the 30 shared photos first, then about 170 more.
3. Done. Answers save as they go. If the browser is closed, logging in again continues where they stopped.

Prefer to run it locally? A zip pack with the same tool exists; instructions in https://github.com/kskhan77/bluecart/blob/main/annotation/HOW_TO_ANNOTATE.md.

## Links to paste

| | |
|---|---|
| Annotation tool (hosted) | https://bluecart.khurramshafique.com |
| Annotation guidelines | https://github.com/kskhan77/bluecart/blob/main/annotation/guidelines.md (also inside the tool: https://bluecart.khurramshafique.com/media/guidelines.html) |
| Setup instructions | https://github.com/kskhan77/bluecart/blob/main/annotation/HOW_TO_ANNOTATE.md |
| Dataset (photos + manifest, public, UM students can open it) | https://github.com/kskhan77/bluecart (photos in `data/images/`, one row per photo in `data/manifest.csv`, credits in `data/attribution.csv`) |
| Dataset description (README) | https://github.com/kskhan77/bluecart/blob/main/README.md |
| License | https://github.com/kskhan77/bluecart/blob/main/LICENSE.md |
| Changes from proposal | https://github.com/kskhan77/bluecart/blob/main/CHANGES_FROM_PROPOSAL.md |
| Demo page with video and screenshots | https://bluecart.khurramshafique.com/media/demo/index.html |
| Presentation slides | Export the deck as PDF (Share → Export) and post it in `#project-annotation-tasks`; paste that Discord link or attach the PDF |
| Annotator packs | Not needed: the tool is hosted. Packs are made on request with `scripts/make_annotation_packs.py`. |

## Before you submit

- [x] Guidelines v1.0 are locked (Oct 6). The Discord contact is https://discord.gg/2t2DSNyBm
- [x] The timed pilot is done: median 6 seconds on 160 photos. The form uses 15 to 20 seconds for a first-time annotator.
- [x] The hosted tool is 30 shared photos, then 170 more, 200 per person, two labels on every other photo.
- [x] RealWaste stays in the dataset. The dataset license is CC BY-NC-SA 4.0 (`LICENSE.md` says so).
- [x] All links above are public and were checked on Oct 6 (GitHub pages and the hosted tool answer with 200).
- [ ] Post the slides PDF in Discord, then paste that link into the form.
- [ ] Submit the form with a UM Google sign-in. It cannot be submitted from this repo.
