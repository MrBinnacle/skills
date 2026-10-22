---
"mrbinnacle-skills": patch
---

The card-file check now refuses a `Re-screen trigger` row whose whole value is a placeholder: `none`, `n/a`, `TBD` or `-`, in any case, with or without a trailing period or backticks. Before this change the check refused only an empty row, so a card could publish with no re-screen trigger while the check reported green. ADMISSION.md criterion 4 needs a named trigger for a card to leave, and a placeholder names none. The match is on the whole value, so a real trigger whose first word is "None" still passes. Every published card already names a real trigger, so no card changes and an installed user loses nothing.
