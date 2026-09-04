---
"mrbinnacle-skills": patch
---

`git-pull-rebase-trap`: the receipt its `Paired verdict` row cites returned 404 to any reader who clicked it. The three receipt links in the record are now pinned to a harness commit instead of tracking `main`.

The row cited `blob/main/docs/sers/receipts/gitpull-paired-k8-2026-09-01-detector-v2.json`. That file moved into `docs/sers/receipts/superseded/` on the harness when a later run landed, and a `main`-tracking URL follows the branch rather than the file. The link broke silently and the repository's own link check caught it on the next pull request, which is the gate working.

`AGENTS.md` already required this. Its record step specifies a receipt clause carrying a "harness blob URL pinned to a commit, never main". Three links in this file predated that rule or missed it. All three now name `0af2f99`, and every path was verified present at that commit before the edit.

Nothing about the card's evidence changes here. The verdict stays `CANT_TELL_YET (underpowered)`, the measurements are untouched, and no controlled row is rewritten. This is a repair to a pointer, not a disposition.

One substantive question is left open rather than answered in passing: the harness now carries a later receipt for this card, `gitpull-paired-n32-2026-09-03-sized.json`, and whether it supersedes the row this file states is a disposition that runs through the currency gate. It is filed separately.
