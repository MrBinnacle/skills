---
"mrbinnacle-skills": patch
---

Two cards read the same in every harness. `pull-rebase` no longer says "Claude Code can block the Bash tool call with `PreToolUse`" in its body; it says a harness can refuse the shell tool call from a pre-tool-call guard, and `preventive-recipes.md` now carries a Pi `tool_call` section beside the Claude Code `PreToolUse` one, each dated against the docs it was checked on. `decision-rights` says "guard catch" where it said "hook catch". A new gate, `scripts/validate_harness_neutrality.py`, refuses a published `SKILL.md` that names one harness's tool, hook event or config path; the rule is recorded in AGENTS.md under Authoring conventions, ADMISSION.md points at it without a version bump, and the fourteen (card, pattern) pairs that already breached on 2026-10-10 — forty-nine lines — sit on a shrink-only allowlist keyed per card and pattern.
