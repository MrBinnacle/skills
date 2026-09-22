---
type: regex
target: last_message
pattern: '(?:@\w*\.?task|shared_task|app\.task|celery)'
flags: i
---

# An inertia check, not a correctness check

This grader requires the final message to contain Celery task code or to name
Celery. An answer that engages with "write me the task definition" does that.
An agent that refuses, answers with a remark about delegation, or produces
nothing does not.

It does **not** check that the task is correct. Grading that needs an `llm`
grader, and this suite uses free graders only.

## What it is here for

The negative control passes when `subagent-handback` does not fire. An agent
that does nothing at all also satisfies that. This grader removes that reading:
with both graders passing, the agent answered the question and did not reach
for the dispatch card.

An agent that answers in prose without code or the word Celery fails this
grader while the control itself holds. Read the per-grader verdicts, not the
case score.
