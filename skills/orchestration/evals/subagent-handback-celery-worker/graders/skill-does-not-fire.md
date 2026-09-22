---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?subagent-handback"'
min: 0
max: 0
arm: both
---

# The negative control for the mrbinnacle-orchestration plugin, and why it is valid

This grader fails if `subagent-handback` is invoked. It is the only thing in
the `mrbinnacle-orchestration` cases that can fail in the should-not-fire
direction, which is the defect `skill-harness#507` tracks.

The pattern is the one the positive half uses in
`subagent-handback-dispatch/graders/skill-fires.md`, unchanged, so the pair
asserts one event in opposite directions and cannot drift apart silently.

## Why the card genuinely does not apply

The card's description is "Pre-dispatch, name the return channel — a subagent
handback can be empty. Verify tool grants match the task. Post-return, verify
every claim, negatives first." Every step is about handing work to a model and
reading what the model hands back.

1. Name the return channel. A Celery task returns nothing to a conversation;
   its result goes to the broker's result backend and the logs.
2. Verify tool grants. The worker holds no model tools. It holds a database
   connection and a payment client.
3. Verify every claim on return. The worker makes no claims. It retries charges.

The skill has no work to do. That is a property of the situation, not a
probability.

## Why the situation is a near miss on purpose

A negative case on an unrelated topic passes because nothing fires, which
proves the grader runs and not that the model discriminates. This case keeps the
positive half's vocabulary sentence for sentence: a background worker, the
`payments/` package, "it runs while I do something else and I will not be
watching it", and "write me" the thing to launch. The one fact the card's
trigger turns on, whether the worker is a model receiving a brief, is the one
thing that differs, and the prompt states it in its last paragraph.

## Reading the pair

`subagent-handback-dispatch` holds the plugin, the tool grant and the wording
constant and flips applicability. **If `subagent-handback-dispatch` does not
fire, a pass here is uninformative**, because a model that never invokes the
card passes this case for the wrong reason. Report the two together or report
neither.

The case declares the same installed `mrbinnacle-orchestration` 3.0.0 as its
positive half, so the card is loaded and available in the run. The assertion is
about a loaded, topically invited skill, not an absent one.

`arm: both` keeps this grader in the score. Without it the default
`with-without` ablation reports a `Skill` grader as a with-only indicator that
decides nothing.
