---
"mrbinnacle-skills": patch
---

`subagent-handback` now cites current Claude Code docs that a subagent's or named teammate's final text reaches the agent that spawned it, and keeps the field failures where it did not. It adds three checks (load deferred web tools before dispatch, re-check a background agent's file length before trusting it, widen the search set before trusting a negative), and its description routes on "idle", "no report" and `SendMessage` (#384).
