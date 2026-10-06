# Blue Cart Check: Annotation Guidelines (v1.0)

**Task:** ARI 410/510 Project, Group 2, UM-Flint, Fall 2026
**Rules version:** City of Flint curbside recycling (hauler: Priority Waste), as published on **October 4, 2026** (sources in Section 3). Locked **October 6, 2026**. If the city rules change, we keep this version for the whole project.
**Questions:** Khurram Shafique (kshafiqu@umich.edu) · Hina Kramer (hinak@umich.edu) · [project Discord](https://discord.gg/2t2DSNyBm)

---

## 1. Your job (read this first)

You will see one photo at a time. Each photo shows an everyday item, the way someone would see it just before throwing it away.

**You answer two short questions about the main item, under the City of Flint recycling rules:**

- **Step 1. What kind of item is it?** A kind Flint takes in the blue recycling cart, or a kind it never takes?
- **Step 2 (only for blue cart items). What state is it in, as shown?** Ready to go in, needs a quick fix first, or ruined.

Judge only what you can **see**. Don't guess what the item looked like before the photo was taken, and don't use what *your* hometown accepts. Flint's rules are different from many places (see the Watch-out list in Section 4).

Expect about **15 to 20 seconds per photo** the first time (our own median, after practice, was 6 seconds). Each answer is a button with an icon (a blue bin, a black bin, and so on). Click it, or use the keyboard: **1, 2, 3** answer Step 1 and **4, 5, 6, 7** answer Step 2.

---

## 2. The two questions

### Step 1: what kind of item is this?

| Key | Answer | Choose it when |
|---|---|---|
| 1 | **Blue cart item** (blue bin icon) | It is one of the kinds Flint accepts (Section 3, "In short"), whatever state it is in. A dirty jar and a greasy pizza box are still blue cart *kinds*. Their state is Step 2. |
| 2 | **Never the blue cart** (black bin icon) | It is a kind Flint never takes: named as not accepted, or simply not on the accepted list. It goes in the trash (black or gray bin) or to a special drop-off. |
| 3 | **Can't tell** | The photo itself blocks the decision: you can't identify the item or its material, it is cut off or blurry, or there is no single main item. |

### Step 2: what state is it in, as shown? (appears only after "Blue cart item")

| Key | Answer | Choose it when |
|---|---|---|
| 4 | **Ready** | Empty, reasonably clean, loose (not in a bag), box flattened. It can go in the blue cart exactly as it is. |
| 5 | **Needs prep first** | One quick fix makes it ready: rinse or empty it, flatten it, or take it out of a plastic bag. |
| 6 | **Ruined** | Grease or food has soaked into paper or cardboard. It can't be rinsed, so it goes in the trash. |
| 7 | **Can't see enough** | The state decides the answer, but the photo doesn't show it (for example, you can't see inside an opaque container). |

### How your two answers become our label

You don't pick this. We compute it from your two answers.

| Step 1 | Step 2 | Final label |
|---|---|---|
| Blue cart item | Ready | `accepted` |
| Blue cart item | Needs prep first | `accepted_after_prep` |
| Blue cart item | Ruined | `not_accepted` |
| Blue cart item | Can't see enough | `cannot_determine` |
| Never the blue cart | (not asked) | `not_accepted` |
| Can't tell | (not asked) | `cannot_determine` |

**Optional "reason" field:** pick the main reason for your choice (material / contamination / bagged / form factor / hazard or electronics / unclear). It helps us improve these guidelines. Skip it if you're unsure.

---

## 3. What Flint accepts (the rule source, quoted word for word)

Everything in quotation marks below is the source's own wording, copied on October 4, 2026. You don't need to memorize it: Section 4 turns it into rules, and Section 6 is a one-screen checklist.

### A. City of Flint, "Acceptable Recycling Materials" info card
[PDF](https://www.cityofflint.com/wp-content/uploads/2024/09/Recycling-Info-Card.pdf), linked from [cityofflint.com/recycling](https://www.cityofflint.com/recycling/)

"THANK YOU FOR RECYCLING THESE:"

| Group | The card says |
|---|---|
| Paper | "Paper and Cartons (empty and clean)" |
| Cardboard | "Cardboard (flatten)" |
| Metal | "Aluminum Cans, Steel Cans, and Foil Trays (empty and dry)" |
| Plastic | "Bottles, Jars and Jugs (empty and dry)" |
| Glass | "Bottles and Jars (empty and dry)" |

"NO!"

- "No Bagged Recyclables (no garbage)"
- "No Plastic Bags or Plastic Wrap"
- "No Hoses, Cords or Wires"
- "No Batteries or Electronics (drop-off only)"
- "No Food or Liquid (empty all containers)"

### B. City of Flint, Recycling page and cart FAQ
[Recycling page](https://www.cityofflint.com/recycling/) · [FAQ PDF](https://www.cityofflint.com/wp-content/uploads/2024/09/Recycling-FAQ-1.pdf)

- "All recyclable materials must be loose inside of the blue recycling cart. Please do not bag your recyclables."
- What the FAQ says is collected: "Plastic bottles and containers", "Aluminum and steel cans", "Glass bottles and jars", "Cardboard (flattened)", "Newspaper, junk mail, mixed paper—all colors and types".
- "All containers should be empty and dry. Replace caps on empty containers."
- Hoses, cords, wires, or clothes: "No. These items wrap around equipment at the recycling processing facility, creating a safety hazard for workers and causing facility shutdowns."
- Plastic bags or plastic wrap: "No. Plastic bags and wrap cause equipment jams at the recycling processing facility." The FAQ names "grocery bags, drink case wrapping, cling wrap, and bubble wrap" as plastic film.

### C. Priority Waste (the city's hauler), Flint page
[prioritywaste.com/municipality/flint-mi](https://www.prioritywaste.com/municipality/flint-mi/)

"What are acceptable recyclable materials?"

- "Paper: Newspaper, junk mail, flattened cardboard and box board, magazines, mixed paper."
- "Metal: Empty cans and aerosol cans, aluminum, tin."
- "Plastic: Bottles, jugs, storage containers, tubs."
- The hauler's ["Acceptable Recyclable Materials" flyer](https://www.prioritywaste.com/wp-content/uploads/2023/02/Priority-Waste-Acceptable-Recycling-Materials.pdf) adds "Glass: Clear and colored glass".

"What materials are not accepted for recycling?"

- "Materials not accepted include: Plastic Bags or Film, Plastic Cups, Styrofoam, Food Waste, Storage Bags, Soiled Pizza Boxes, Pyrex or Ceramic, Bubble Wrap Packing Materials, Plastic Silverware, Metal or Plastic Hangers"

### D. UM-Flint campus program (for comparison; we label to the city rules)
[The Michigan Times, Sept 1, 2026](https://mtimes.org/2026/09/01/new-recycling-system-aims-to-make-waste-sorting-easier-at-um-flint/)

- "paper, plastic, cardboard and aluminum can be placed together in the blue recycling bins as long as materials are clean and dry"
- "hot and cold beverage cups, plastic bags and single-serve packets are not accepted in the University's recycling system"

### In short

**Accepted in the blue cart (empty, clean/dry, loose):**
- Paper: newspaper, junk mail, magazines, mixed paper; cartons
- Cardboard and box board (cereal-type boxes), flattened
- Aluminum and steel (tin) cans, **foil trays**, **empty aerosol cans**
- Plastic bottles, jugs, jars, tubs and storage containers
- Glass bottles and jars

**Named as not accepted (never the blue cart):**
- Plastic bags, plastic wrap/film, storage (zip) bags, bubble wrap
- **Plastic cups**, plastic silverware, Styrofoam
- Food and liquid; **soiled pizza boxes**
- Batteries and electronics; hoses, cords, wires; clothes
- Pyrex and ceramic; metal or plastic hangers

---

## 4. Decision rules

**Rule 0: Judge the main item.**
Judge the item the photo is *about*: the one that is centered or fills most of the frame. Ignore the table, floor and anything in the background.
If the photo shows several different things and none of them is clearly the main one → Step 1: **Can't tell** (key 3).
*Exception: recyclables inside a bag are judged together (Rule 1e).*

### Step 1 rules: the kind of item

- **1a. Named as not accepted** (Section 3 "not accepted" list) → **Never the blue cart**, no matter how clean it is.
  *Example: a spotless plastic cup is still "never".*
- **1b. Not on the accepted list at all.** The accepted list is the complete list. If you can tell what the item is and it is not one of the accepted kinds (a backpack, a toy, a wooden spoon, a chip bag) → **Never the blue cart**. Don't use "Can't tell" just because the rules never mention the item.
- **1c. Paper cups.** The city lists name only "Plastic Cups". Paper coffee cups are not named on either city list. They are not on the accepted list, and the UM-Flint campus program rejects "hot and cold beverage cups", so every disposable cup, paper or plastic → **Never the blue cart**.
- **1d. Check the shape.** Plastic **bottles, jugs, jars and tubs** are blue cart items. Plastic **cups** are not.
  - **Tub:** a container sold with food in it (yogurt, butter, deli), usually with a snap lid.
  - **Cup:** made to drink from. Wide rim, often tapered, often has a straw/sip lid, often a café logo.
  - If you really can't tell → **Can't tell**.
  - **Takeout clamshells.** A rigid plastic clamshell counts as a plastic container: **Blue cart item**, then Step 2 (food left inside means needs prep). A foam clamshell is Styrofoam → **Never the blue cart**.
- **1e. Bagged items.** Accepted items inside a closed or tied plastic bag → judge the items: **Blue cart item**, then Step 2 **Needs prep first** (they must come out of the bag). *An empty plastic bag on its own → Never the blue cart.*
- **1f. When to use "Can't tell".** Only when the photo itself blocks the decision: the item or its material can't be identified (plastic or glass? foil or plastic film?), the item is cut off, blurry or too dark, or there is no single main item. **Don't** use it just because a case feels hard. If you're about 70% sure, pick the answer.

### Step 2 rules: the state (blue cart items only)

- **2a. Ready.** Empty, reasonably clean, loose, and flat if it is a big box. Light printing, a label or a small dry crumb counts as clean. A cap or lid on an empty container is fine: the city says to put caps back on. Small box-board (a cereal box) doesn't need flattening.
- **2b. Needs prep first.** One quick fix makes it ready:
  - visible leftover food or liquid in a container (sauce in a jar, soda in a can, peanut butter on the walls),
  - a large cardboard box still standing as a box,
  - accepted items inside a plastic bag (Rule 1e).
- **2c. Ruined.** Grease or food soaked into paper or cardboard (dark oily stains, cheese stuck on a pizza box). Paper can't be rinsed. *The hauler also names "Soiled Pizza Boxes" as not accepted, so if you answered "Never the blue cart" at Step 1 for a greasy pizza box, the final label is the same.*
- **2d. Can't see enough.** You can't see inside a container to check whether it is empty or dirty, and that decides the answer.

### Watch-out list: where Flint differs from what people assume
| Item | People often think | Your answers |
|---|---|---|
| Paper coffee cup | recyclable (it's paper) | Step 1: **Never** (Rule 1c) |
| Clear plastic cold-drink cup | recyclable (it's plastic) | Step 1: **Never** |
| Clean aluminum foil tray | trash | **Blue cart item**, **Ready** |
| Empty aerosol can | hazardous | **Blue cart item**, **Ready** |
| Recyclables in a plastic bag | fine | **Blue cart item**, **Needs prep first** |
| Greasy pizza box | cardboard → recyclable | **Blue cart item**, **Ruined** |
| Zip / storage bag, even a clean one | plastic → recyclable | Step 1: **Never** |
| Charging cable, earbuds, batteries | "e-waste goes in recycling" | Step 1: **Never** (drop-off only) |

---

## 5. Worked examples (at least one per final label)

| # | Photo shows | Step 1 | Step 2 | Final label | Why (and why not the others) |
|---|---|---|---|---|---|
| 1 | Empty, rinsed plastic milk jug, cap on | Blue cart item | Ready | `accepted` | Jug = accepted shape, clean, loose. Nothing to fix, so not "needs prep". |
| 2 | Flattened Amazon box | Blue cart item | Ready | `accepted` | Cardboard, already flat. |
| 3 | Clean foil pie tray | Blue cart item | Ready | `accepted` | Foil trays are on Flint's accepted list. |
| 4 | Salsa jar with sauce still inside | Blue cart item | Needs prep first | `accepted_after_prep` | Glass jars are accepted, but it needs emptying and rinsing. Not "ruined": glass can be rinsed. |
| 5 | Three cans tied inside a grocery bag | Blue cart item | Needs prep first | `accepted_after_prep` | Cans are accepted but must come out of the bag. |
| 6 | Large unflattened shipping box | Blue cart item | Needs prep first | `accepted_after_prep` | Cardboard is accepted but must be flattened. |
| 7 | Pizza box with oil stains and cheese | Blue cart item | Ruined | `not_accepted` | Cardboard is a blue cart kind, but grease has soaked in and can't be rinsed out. |
| 8 | Paper coffee cup with lid | Never the blue cart | (not asked) | `not_accepted` | A cup is not on the city's accepted list and the campus program rejects beverage cups (Rule 1c), even though it looks like paper. |
| 9 | Empty plastic grocery bag | Never the blue cart | (not asked) | `not_accepted` | Plastic bags are never accepted. |
| 10 | Clear plastic cup with dome lid and straw | Never the blue cart | (not asked) | `not_accepted` | Cup, not tub (Rule 1d). |
| 11 | Close-up of an opaque container; can't tell if empty | Blue cart item | Can't see enough | `cannot_determine` | It is an accepted kind, but emptiness decides between ready and needs prep, and the photo doesn't show it. |
| 12 | Shiny wrapper; can't tell foil from plastic film | Can't tell | (not asked) | `cannot_determine` | Material unclear: foil would be a blue cart item, plastic film would not. |

---

## 6. Quick checklist per photo
1. Which item is the photo about? No clear main item → **3**
2. What kind of item is it?
   - Named as not accepted, a cup, or not on the accepted list → **2**. Done.
   - Can't identify the item or its material → **3**. Done.
   - A kind Flint accepts → **1**, then Step 2:
3. Grease or food soaked into paper or cardboard → **6**
4. Food or liquid left in a container, a big box not flattened, or inside a plastic bag → **5**
5. Can't see its state, and that matters → **7**
6. Otherwise → **4**

---

## 7. Contact
Stuck, or the tool isn't working? Message us on the [project Discord](https://discord.gg/2t2DSNyBm) or email **kshafiqu@umich.edu** / **hinak@umich.edu**. We usually answer within a few hours.
