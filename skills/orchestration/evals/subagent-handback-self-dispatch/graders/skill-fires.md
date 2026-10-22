---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?subagent-handback"'
arm: both
---

Asserts `subagent-handback` was invoked at least once.

This case is the self-dispatch variant of `subagent-handback-dispatch`, added
for #609. The sweep it describes is the same. What differs, and the result of
running both cases, is recorded once, in the Runs section of `../MANIFEST.md`.

Allowing `Agent` lets a run spawn a real subagent on the runner's credential.
The scaffold directory is empty, so the subagent finds no `payments/` package
and returns early. Run this case with `--max-cost-usd` set.
