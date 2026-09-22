---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?subagent-handback"'
min: 0
max: 0
arm: both
---

This grader passes when the subagent-handback skill was NOT invoked. The prompt describes standard Celery worker configuration with no subagent dispatch or research verification, so the skill should not fire.
