# Phase 2a: Discord post for #project-competitions (before class on the due date)

Replace the two bracketed links, then paste.

---

**Group 2 · Blue Cart Check: does this item go in Flint's blue recycling cart?**

Slides: [slides link]
Competition (private Kaggle, invite link): [Kaggle invite link]

One phone photo of one item → one of four labels: `accepted`, `accepted_after_prep`, `not_accepted`, `cannot_determine`. 617 labeled photos (thanks to the 11 of you who annotated: 2,846 labels), 463 for training, 154 hidden test. Metric: macro-F1. Submission: a CSV with `id,label`, one row per test photo; `sample_submission.csv` is the format.

Bar to beat: 0.59 macro-F1 (logistic regression on ResNet-50 embeddings). Zero-shot Claude gets 0.54, so the small classes are wide open. Rules on the page: course use only, predictions must come from a model, no hand-labeling of test photos, pretrained models welcome. 5 submissions a day; put your group number in your team name.

Questions: this channel or https://discord.gg/2t2DSNyBm. Ends [end of Phase 2b].

---

Before posting: share the deck (Share menu, "anyone with the link" or export the PDF and attach it), create the Kaggle competition from `docs/KAGGLE_COMPETITION.md`, run the pre-launch test, copy the invitation link from the launch checklist.
