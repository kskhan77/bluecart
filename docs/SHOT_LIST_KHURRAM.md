# Khurram's shot list: Campus disposables (target 200, minimum 150)

**Where:** UM-Flint bin stations, dining areas, café, your kitchen/desk.
**Phone:** normal photo mode, JPEG if possible (iPhone: Settings → Camera → Formats → *Most Compatible*).
**Rules:** one item per photo · fill most of the frame with the item · no people/faces/hands with rings or ID · no names on receipts/cups (turn the name to the back or cover it) · don't photograph inside a bin someone else filled · switch background/lighting every few shots.

**Speed trick:** for each item, shoot **2–4 versions** (clean/dirty, lid on/off, loose/bagged, different backgrounds). The "Expected" column is just for checking you cover every label. **Don't write labels anywhere in the data.**

| # | Item | Versions to shoot | Shots | Expected label(s) |
|---|---|---|---|---|
| 1 | Paper hot-coffee cup (with/without lid, sleeve) | clean, coffee stain, lid on, lid off, sleeve on | 20 | not_accepted |
| 2 | Clear plastic cold-drink cup (dome/flat lid, straw) | empty, with ice/drink left, lid on/off | 20 | not_accepted |
| 3 | Plastic cup **vs.** plastic tub look-alikes (yogurt, deli, fruit cup) | same angle & background as the cups, empty and with residue | 20 | tub: accepted / after_prep · cup: not_accepted (**hard case**) |
| 4 | Loose plastic lids (coffee, cold cup) | top, side | 8 | not_accepted |
| 5 | Straws (plastic, paper) | alone, in wrapper | 8 | not_accepted |
| 6 | Plastic cutlery / sporks / stirrers | single, wrapped kit | 10 | not_accepted |
| 7 | Single-serve packets (ketchup, sugar, creamer, soy) | full, torn/empty | 12 | not_accepted |
| 8 | Styrofoam (cups, clamshells, trays) | clean, with food | 14 | not_accepted |
| 9 | Plastic water bottle | empty cap on, half full, crushed | 16 | accepted / after_prep (liquid) |
| 10 | Soda/energy can | empty, liquid visible, crushed | 12 | accepted / after_prep |
| 11 | Plastic takeout clamshell / tub-style container | clean, with food | 14 | clean tub-type: accepted · food: after_prep · **check the city list for clamshells** |
| 12 | Paper takeout box / pizza slice box / fry box | clean, grease-stained | 12 | clean: accepted · greasy: not_accepted |
| 13 | Foil wrap / foil sandwich wrapper / foil tray | clean, with food | 10 | accepted / after_prep |
| 14 | Recyclables in a plastic bag (cans/bottles bagged) | tied bag, open bag | 8 | accepted_after_prep |
| 15 | Deliberately unclear shots (blurry, cut off, opaque cup where you can't see inside, foil vs. film wrapper) | — | 16 | cannot_determine |
| | **Total** | | **200** | |

**Label mix this aims for (your set):** about 35% not_accepted, 30% accepted, 25% after_prep, 10% cannot_determine. Your set is the main source of the cup/lid/packet "not accepted" cases.

## Name multi-state shots (2 min, important)
Rename versions of the SAME object with a shared prefix + `__`:
`cup07__clean.jpg`, `cup07__lid_off.jpg`, `cup07__stain.jpg`. They become one `item_group_id`, which keeps train/test honest later.
Windows tip: select the photos of one object → F2 → type `cup07__` → Windows numbers them `cup07__ (1).jpg`, `cup07__ (2).jpg` and so on, which works.

## After shooting (10 minutes)
1. Copy the photos from your phone to `data/raw/khurram/` (split by setting if you want accurate `setting` values, e.g. `raw/khurram_bin/`, `raw/khurram_dining/`).
2. From the repo root:
   ```
   pip install pillow
   python scripts/prepare_images.py --input data/raw/khurram_bin --photographer "Khurram Shafique" --category-set disposables --setting bin_station
   python scripts/prepare_images.py --input data/raw/khurram_dining --photographer "Khurram Shafique" --category-set disposables --setting dining
   ```
3. Spot-check 5 images in `data/images/`, then upload `data/images/` + `data/manifest.csv` to the Drive folder.
4. Never commit `data/raw/` (it still has GPS data). `.gitignore` already excludes it.
