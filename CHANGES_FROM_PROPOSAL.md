# Changes from proposal

> TEAM TODO: keep what's true, delete what isn't, and add anything else that changed.

- **Guidelines and annotation tool moved earlier.** The proposal planned the guidelines for Milestone 2. Phase 1 requires them now, so we wrote guidelines v1.0 and piloted them internally before release.
- **Annotation tool: Potato** (the course's recommended tool) instead of building our own form with Streamlit/Gradio. It shows one image at a time, has keyboard shortcuts, records time per item, and exports clean JSONL. Gradio/Streamlit stay on the list for the later deployment phase.
- **Labels unchanged:** `accepted`, `accepted_after_prep`, `not_accepted`, `cannot_determine`, plus the optional reason code.
- **Decision rules sharpened after the pilot:** `<e.g. defined cup vs. tub; "soaked-in grease = not_accepted, removable residue = after_prep"; cannot_determine only when the photo blocks the decision>`
- **Dataset size:** `<target was ~1,200; Phase 1 release has N because ...>`. Collection continues, and later images will be labeled in the next round.
- **Annotation design:** `<A>`-image agreement set labeled by all annotators + `<B>` coverage images each (see README §6).
- **Manifest:** added `category_set`, `item_group_id` (same object in several states, for leakage-free splits) and `sha1` (duplicate detection) columns.
