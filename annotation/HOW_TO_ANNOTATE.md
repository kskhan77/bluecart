# How to annotate Blue Cart Check (about 1 hour)

You need Python 3.9+ on your computer. Everything runs locally; nothing is uploaded.

## 1. Set up (about 3 minutes)
1. Unzip `bluecartcheck_<your_id>.zip` to a folder.
2. Open a terminal in that folder and run:
   ```
   pip install potato-annotation
   ```
3. Read `guidelines.md` (about 5 minutes). It has the rules and examples.

## 2. Start the tool
```
potato start config.yaml -p 8000
```
Open **http://localhost:8000** in your browser. Type any username (use your **umich uniqname**) and press Enter. No password is needed.

## 3. Label
- Look at the photo and press **1–4** (or click) to choose the label.
- Optional: pick a reason.
- Click **Next** (or press →). You can go back with ←.
- The progress counter at the top shows how many you've done. Stop after about **1 hour**, even if you haven't finished. Your work saves automatically.

## 4. Send your labels back
1. Stop the tool (Ctrl+C in the terminal).
2. Zip the **`annotation_output`** folder. Your labels are in `annotation_output/exports/jsonl/annotations.jsonl`, and the rest of the folder holds your per-item timing.
3. Send it to **kshafiqu@umich.edu**, or DM it on Discord, with the subject *"Blue Cart Check labels: <uniqname>"*.

## Troubleshooting
- `potato: command not found` → try `python -m potato start config.yaml -p 8000`.
- Port in use → change `8000` to `8001`.
- Images don't load → make sure you run the command **inside** the unzipped folder (next to `config.yaml`).
- Still stuck? Message us on Discord `#<team-channel>`.
