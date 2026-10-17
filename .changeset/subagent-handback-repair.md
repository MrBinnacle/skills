---
"mrbinnacle-skills": patch
---

`subagent-handback` now states what current Claude Code docs promise about a subagent's final text, and separately what has failed in the field. Before dispatch it tells you to load deferred web tools; after an idle agent it tells you to check that its file is complete; and it tells you to widen the search set before trusting a reported negative. Its description now routes on "idle", "no report" and `SendMessage` (#384).
