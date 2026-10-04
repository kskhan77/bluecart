# Blue Cart Check: Annotation Guidelines (v1.0 DRAFT)

**Task:** ARI 410/510 Project, Group 2, UM-Flint, Fall 2026
**Rules version:** City of Flint curbside recycling (Priority Waste), accessed `<DATE>`. If the rules change, we keep this version for the whole project.
**Questions:** Khurram Shafique (kshafiqu@umich.edu) · Hina Kramer (hinak@umich.edu) · Discord: `#<team-channel>`

> TEAM TODO before release: replace every `<...>` placeholder, paste the exact wording from the two rule pages into Section 3, and add one real photo from our dataset for each example in Section 5.

---

## 1. Your job (read this first)

You will see one photo at a time. Each photo shows an everyday item, the way someone would see it just before throwing it away.

**Decide where this item should go under the City of Flint recycling rules, as it looks in the photo:**

- the blue recycling cart,
- the blue cart, but only after it is cleaned/emptied/flattened/unbagged,
- never the blue cart, or
- you can't tell from the photo.

Judge only what you can **see**. Don't guess what the item looked like before the photo was taken, and don't use what *your* hometown accepts. Flint's rules are different from many places (see the Watch-out list in Section 4).

Expect about **`<X>` seconds per photo**. Use the keyboard: **1, 2, 3, 4** pick the label.

---

## 2. The labels

| Key | Label | Meaning |
|---|---|---|
| 1 | **accepted** | Accepted material, **ready right now**: empty, reasonably clean, loose (not in a bag). Put it in the blue cart as it is. |
| 2 | **accepted_after_prep** | Accepted material, but it **needs one fix first**: rinse/empty it, flatten it, or take it out of a plastic bag. |
| 3 | **not_accepted** | **Never** the blue cart, even if cleaned. Trash or special disposal. |
| 4 | **cannot_determine** | The photo doesn't give enough to decide (see Rule 6). |

**Optional "reason" field:** pick the main reason for your choice (material / contamination / bagged / form factor / hazard or electronics / unclear). It helps us improve these guidelines. Skip it if you're unsure.

---

## 3. What Flint accepts (the rule source)

> TEAM TODO: replace the lists below with the **exact** wording from
> https://www.cityofflint.com/recycling/ and https://www.prioritywaste.com/municipality/flint-mi/

**Accepted in the blue cart:**
- Plastic bottles, jugs and tubs (rinsed, empty)
- Aluminum and steel cans; **empty aerosol cans**; **aluminum foil and foil trays** (clean)
- Glass bottles and jars (rinsed)
- Cardboard (flattened) and box board (cereal-type boxes)
- Newspaper, magazines, mail, mixed paper
- Cartons
- City rule: *"All recyclable materials must be loose inside of the blue recycling cart. Please do not bag your recyclables."*

**Not accepted (never the blue cart):**
- Plastic bags, plastic wrap/film, bubble wrap
- **Disposable cups**: paper coffee cups and plastic cups (also not accepted on the UM-Flint campus)
- Styrofoam / foam (cups, trays, takeout boxes, packing peanuts)
- Food-soiled paper, e.g. a **greasy pizza box**; food waste
- Batteries and electronics; hoses, cords, cables, wires
- Ceramic, Pyrex, drinking glasses, window glass
- Hangers, plastic cutlery
- Single-serve packets (UM-Flint campus rule)

---

## 4. Decision rules (apply in this order)

**Rule 1: Identify the material.**
If the material is on the *not accepted* list → **not_accepted**, no matter how clean it is.
*Example: a spotless plastic cup is still not_accepted.*

**Rule 2: Check the shape.**
Plastic **bottles, jugs and tubs** are accepted. Plastic **cups** are not.
- **Tub:** a container sold with food in it (yogurt, butter, deli), usually with a snap lid.
- **Cup:** made to drink from. Wide rim, often tapered, often has a straw/sip lid, often a café logo.
- If you really can't tell → **cannot_determine** (reason: unclear).

**Rule 3: Is it bagged?**
Accepted items inside a closed or tied plastic bag → **accepted_after_prep** (reason: bagged). The bag itself is never accepted.
*An empty plastic bag on its own → not_accepted.*

**Rule 4: Is it dirty or full?**
- **Visible leftover food or liquid** in a container (sauce in a jar, soda in a can, peanut butter on the walls) → **accepted_after_prep** (reason: contamination). A quick rinse fixes it.
- **Grease or food soaked into paper/cardboard** (dark oily stains, cheese stuck on a pizza box) → **not_accepted**. Paper can't be rinsed.
- Light printing, a label or a small dry crumb → treat as clean.

**Rule 5: Is cardboard flattened?**
Large cardboard box still standing as a box → **accepted_after_prep** (reason: form factor). Already flat → **accepted**. Small box-board (cereal box) doesn't need flattening.

**Rule 6: When to use cannot_determine.**
Use it **only** when the photo itself blocks the decision:
- the material can't be identified (plastic or glass? foil or plastic?),
- you can't see inside a container to check if it's empty or dirty, and that matters,
- the item is cut off, blurry, or too dark,
- the item isn't covered by any rule above.

**Don't** use it just because a case feels hard. If you're about 70% sure, pick the label.

### Watch-out list: where Flint differs from what people assume
| Item | People often think | Flint says |
|---|---|---|
| Paper coffee cup | recyclable (it's paper) | **not_accepted** |
| Clear plastic cold-drink cup | recyclable (it's plastic) | **not_accepted** |
| Clean aluminum foil tray | trash | **accepted** |
| Empty aerosol can | hazardous | **accepted** |
| Recyclables in a plastic bag | fine | **accepted_after_prep** |
| Greasy pizza box | cardboard → recyclable | **not_accepted** |

---

## 5. Worked examples (at least one per label)

> TEAM TODO: insert a real photo from our dataset under each example (e.g. `![](examples/ex1.jpg)`).

| # | Photo shows | Correct label | Why (and why not the others) |
|---|---|---|---|
| 1 | Empty, rinsed plastic milk jug, cap on | **accepted** | Jug = accepted shape, clean, loose. Not after_prep: nothing to fix. |
| 2 | Flattened Amazon box | **accepted** | Accepted material, already flat. |
| 3 | Clean foil pie tray | **accepted** | Foil trays are on Flint's accepted list. |
| 4 | Salsa jar with sauce still inside | **accepted_after_prep** | Glass jar is accepted, but needs emptying and rinsing (contamination). |
| 5 | Three cans tied inside a grocery bag | **accepted_after_prep** | Cans are accepted but must come out of the bag (bagged). |
| 6 | Large unflattened shipping box | **accepted_after_prep** | Cardboard is accepted but must be flattened (form factor). |
| 7 | Starbucks paper cup with lid | **not_accepted** | Disposable cups are rejected by the city and campus, even though they look like paper. |
| 8 | Pizza box with oil stains and cheese | **not_accepted** | Grease soaks into the cardboard and can't be rinsed out (contamination). |
| 9 | Empty plastic grocery bag | **not_accepted** | Plastic bags are never accepted. |
| 10 | Clear plastic cup with dome lid and straw | **not_accepted** | Cup, not tub (form factor). |
| 11 | Close-up of an opaque container; can't tell if empty | **cannot_determine** | Emptiness decides between accepted and after_prep, and the photo doesn't show it. |
| 12 | Shiny wrapper; can't tell foil from plastic film | **cannot_determine** | Material unclear. |

---

## 6. Quick checklist per photo
1. What material is it? On the never list? → **3**
2. Cup, or bottle/jug/tub?
3. In a bag? → **2**
4. Food or liquid left in it? Container → **2**. Grease soaked into paper → **3**
5. Big box not flattened? → **2**
6. All good → **1**. Photo doesn't show enough → **4**

---

## 7. Contact
Stuck, or the tool isn't working? Message us on Discord `#<team-channel>` or email **kshafiqu@umich.edu** / **hinak@umich.edu**. We usually answer within a few hours.
