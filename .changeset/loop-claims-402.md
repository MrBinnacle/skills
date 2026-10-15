---
"mrbinnacle-skills": patch
---

Corrects a claim about `/loop` in AGENTS.md and three cards (`pull-rebase`, `decision-rights`, `closure-mode`). The old text said a prompt-triggered hook cannot fire in a `/loop` turn. Claude Code's hooks docs, read 2026-10-15, say `UserPromptSubmit` runs on each `/loop` iteration. The corrected text says such a hook fires on the prompt, not on the tool call, so only a `PreToolUse` hook can block an action. The claim that a `disable-model-invocation` skill arrives as plain text in a scheduled turn is unchanged, and now cites `scheduled-tasks.md`. Installed users need do nothing.
