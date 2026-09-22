---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?decision-rights"'
arm: both
---

Asserts `decision-rights` was invoked at least once.

Pre-registered before any run: description coverage for this case is partial.
The card's description names handoffs, plans, ADRs and subagent prompts. It
does not name an issue body. The prompt supplies the conditions the card exists
for, namely a downstream reader who gets only this text, one decision that is
settled and must not be reopened, and one that is open and that new evidence
should reopen. If the skill does not fire, the finding is about the card's
description rather than about the model's judgement, and the remedy is a
description edit rather than a rate to push up.

See `fix-ci-red-checks/graders/skill-fires.md` for why `arm: both` is set on
every skill grader in this suite.
