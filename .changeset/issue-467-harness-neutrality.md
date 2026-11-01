---
"mrbinnacle-skills": patch
---

Two cards now read the same in every harness. `pull-rebase` no longer tells the reader to block "the Bash tool call with `PreToolUse`" or cites the Claude Code hooks docs in its body. It says a harness can refuse the shell tool call from a pre-tool-call guard, and `preventive-recipes.md` carries a Pi `tool_call` section beside the Claude Code `PreToolUse` one. The Pi recipe is written against pi-coding-agent 1.1.0 and has not been executed. `decision-rights` says "guard catch" where it said "hook catch". A new gate, `scripts/validate_harness_neutrality.py`, refuses a published `SKILL.md` that names one harness's tool, hook event or config path. The rule is recorded in `AGENTS.md` under Authoring conventions. The fourteen (card, pattern) pairs that already breached on 2026-10-10 sit on a shrink-only allowlist keyed per card and pattern; they cover 51 lines on the current tree. Installed users need do nothing.
