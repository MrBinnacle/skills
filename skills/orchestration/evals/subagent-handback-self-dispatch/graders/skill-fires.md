---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?subagent-handback"'
arm: both
---

Asserts `subagent-handback` was invoked at least once.

This case differs from `subagent-handback-dispatch` in one variable. There, the
user dispatches and the agent under test writes the brief, with no `Agent` tool.
Here, the agent under test dispatches, so `Agent` is allowed. The sweep it
describes is the same; only the closing request changes, from "write me the
prompt" to "dispatch it now". Issue 609 needs that single difference: if this case fires and the
original does not, the original case is miscalibrated; if neither fires, the
card's description is the cause.

Allowing `Agent` lets a run spawn a real subagent on the runner's credential.
The scaffold directory is empty, so the subagent finds no `payments/` package
and returns early. Run this case with `--max-cost-usd` set.
