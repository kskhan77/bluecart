# How to annotate Blue Cart Check (about 1 hour)

You need Python 3.9+ on your computer. Everything runs locally; nothing is uploaded.

## 1. Set up (about 3 minutes)
1. Unzip `bluecartcheck_<your_id>.zip` to a folder.
2. Open a terminal in that folder and run:
   ```
   pip install potato-annotation==2.9.4
   ```
   (2.9.4 is the version we tested this task with.)
3. Read `guidelines.md` (about 5 minutes). It has the rules and examples.

## 2. Start the tool
```
potato start config.yaml -p 8000
```
Open **http://localhost:8000** in your browser. Type your **umich uniqname** and press Start. No password is needed.

The first time, you see a **welcome page** that explains the task in one screen. Read it, then press **Start labeling**.

## 3. Label
The photo is on the left. On the right are a short summary of the rules, two questions, and an optional reason. Every answer is a button with an icon: click it or press its number.

- **Step 1: what kind of item is it?** Press **1** (blue cart item, blue bin icon), **2** (never the blue cart, black bin icon) or **3** (can't tell).
- **Step 2 appears only if you chose 1: what state is it in?** Press **4** (ready), **5** (needs prep first), **6** (ruined) or **7** (can't see enough).
- You can click instead of using keys. Press another number to change an answer.
- Optional: click a reason.
- Press **→** (or click **Next**) for the next photo. **←** goes back, and your earlier answers are still there.
- You must answer Step 1, and Step 2 when it is shown, before you can go to the next photo.
- The round **?** button (bottom right) opens the help panel: **Full guidelines** there opens the full rules and examples in a new tab.
- The **line above Step 1** always tells you what to do next. After you answer, it shows what your answers mean, for example "Your answer: Accepted after prep".
- Hover over the photo for **+ / − / ⟲** to zoom in, zoom out and reset. Hover over an answer for a one-line reminder.
- Top bar: **Progress** shows how many photos you have labeled. The two double-arrow buttons jump to the previous / next photo you have not labeled yet. To jump to a specific photo, first answer the one you are on, then type a number in the **#** box and press Enter.
- Your work saves automatically. If you close the browser, log in with the same username and you continue where you stopped.
- The round **?** button at the bottom right opens **How it works** (the welcome page again), the **full guidelines** and the **demo page**, lists the keys, and has the email for questions.
- The key legend under the questions is clickable: tap **1 Blue cart**, **→ Next** and so on if you have no keyboard (tablet). Keys light up when you press them. The Step 2 keys are greyed out, and shake if pressed, while Step 2 is not shown.
- Stop after about **1 hour**, even if you haven't finished.
- After the last photo you see a "Thank You" page and can no longer change answers, so fix anything you want to fix before you leave the last photo.

## 4. Send your labels back
1. Stop the tool (Ctrl+C in the terminal).
2. Zip the **whole `annotation_output`** folder. It holds your labels in two files: `annotation_output/<your username>/user_state.json` (the tool's own save file) and `annotation_output/exports/jsonl/annotations.jsonl`. Please send the whole folder, not a single file.
3. Send it to **kshafiqu@umich.edu**, or DM it on Discord, with the subject *"Blue Cart Check labels: <uniqname>"*.

## Troubleshooting
- `potato: command not found` → try `python -m potato start config.yaml -p 8000`.
- Port in use → change `8000` to `8001`.
- Images don't load → make sure you run the command **inside** the unzipped folder (next to `config.yaml`).
- Still stuck? Message us on the project Discord: https://discord.gg/2t2DSNyBm
