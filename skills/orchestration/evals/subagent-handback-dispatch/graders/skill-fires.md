---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?subagent-handback"'
arm: both
---

Asserts `subagent-handback` was invoked at least once.

`Agent` is deliberately absent from this case's `allowed_tools`. The situation
is the moment before a dispatch and the deliverable is the brief, so the agent
under test has no way to actually spawn anything. That keeps the case's cost
bounded to one run and stops a nested dispatch from billing outside the
suite's ceiling.

See `fix-ci-red-checks/graders/skill-fires.md` for why `arm: both` is set on
every skill grader in this suite.
