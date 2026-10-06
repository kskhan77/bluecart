"""
labeling_time.py: how long does it take to label one photo?

The handout asks for a realistic per-item labeling time in the README (Section 5),
and we use it to size the agreement set and the coverage batches.

Potato logs every action an annotator takes in
    annotation_output/<username>/user_state.json  ->  instance_id_to_behavioral_data
Each item has a list of "interactions" with timestamps: the item being loaded
("instance_load"), key presses, label changes, saves, and moving to the next item.

Time for one item = from the moment it was loaded to the last action on it,
added up over every visit (an annotator may come back to an item).
Visits longer than --max-seconds are treated as a break and left out.

Usage (from the repo root), after copying the pilot outputs to
annotation/returned/<annotator>/annotation_output/ :
    python scripts/labeling_time.py
    python scripts/labeling_time.py --returned some/other/folder --max-seconds 120
"""

import argparse
import json
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def item_seconds(interactions, max_seconds):
    """Seconds spent on one item. Returns (seconds, number_of_visits_dropped_as_breaks)."""
    visits, start, last = [], None, None
    for ev in sorted(interactions, key=lambda e: e["timestamp"]):
        if ev.get("target") == "instance_load":      # a new visit to this item starts
            if start is not None:
                visits.append(last - start)
            start = last = ev["timestamp"]
        elif start is not None:
            last = ev["timestamp"]
    if start is not None:
        visits.append(last - start)
    kept = [v for v in visits if v <= max_seconds]
    return sum(kept), len(visits) - len(kept)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--returned", default=str(REPO / "annotation" / "returned"),
                    help="folder that contains the annotators' annotation_output folders")
    ap.add_argument("--max-seconds", type=float, default=120,
                    help="a visit longer than this counts as a break and is ignored (default 120)")
    args = ap.parse_args()

    all_times = []
    for f in sorted(Path(args.returned).rglob("user_state.json")):
        state = json.loads(f.read_text(encoding="utf-8"))
        labeled = set(state.get("instance_id_to_label_to_value") or {})
        times, breaks = [], 0
        for item, data in (state.get("instance_id_to_behavioral_data") or {}).items():
            if item not in labeled:                  # only count items that actually got a label
                continue
            secs, dropped = item_seconds(data.get("interactions") or [], args.max_seconds)
            breaks += dropped
            if secs > 0:
                times.append(secs)
        if not times:
            continue
        all_times += times
        print(f"{state.get('user_id', f.parent.name):<16} items={len(times):>4}  "
              f"median={statistics.median(times):5.1f}s  mean={statistics.mean(times):5.1f}s  "
              f"total={sum(times) / 60:5.1f} min  breaks ignored={breaks}")

    if not all_times:
        raise SystemExit(f"No timed, labeled items found under {args.returned}")

    med = statistics.median(all_times)
    per_hour = 3600 / med
    print(f"\nAll annotators: {len(all_times)} timed items")
    print(f"  median {med:.1f} s per photo   (mean {statistics.mean(all_times):.1f} s)")
    print(f"  about {per_hour:.0f} photos per hour of pure labeling")
    print(f"  about {per_hour * 0.85:.0f} per hour if 15% of the hour goes to reading the guidelines")


if __name__ == "__main__":
    main()
