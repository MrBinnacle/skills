---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?decision-rights"'
min: 0
max: 0
arm: both
---

This grader passes when the decision-rights skill was NOT invoked. The prompt describes personal working notes with no downstream reader, so the skill should not fire.
