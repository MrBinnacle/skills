# Retired skills

When a major AI model release makes a skill unnecessary (the model just does the thing now),
the skill gets re-tested with [skill-harness](https://github.com/MrBinnacle/skill-harness).
If the model no longer needs it, the skill is retired: removed from the collection, recorded
here with its evidence intact. Model progress becomes collection history, not silent rot.

Most collections only ever grow. This log is what shrinking honestly looks like.

## Retired from the collection

| Skill | Retired | Model release that made it unnecessary | Evidence |
|---|---|---|---|
| *(none yet)* | | | |

## Screened out at the gate — July 2026

The same test that will someday retire skills also decides what gets in. It has already fired.

In July 2026, four of the author's own candidate skills were screened before admission. The
test is simple to describe: give a current model (claude-sonnet-5) a task from exactly the
situation the skill was written for — but **without** the skill — three separate times. If the
model needs the skill, it should fail at least once.

It never did. All four candidates hit the ceiling: three passes out of three with no skill
present. On those tasks there was nothing left for a skill to improve, so none of the four
entered the collection — including skills the author was personally convinced were valuable.
The measurement plan was published *before* the runs, so the verdicts couldn't be bent
afterward: [the pre-registration, with each screen's registered result](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md).

| Candidate | What it taught | Verdict (2026-07) |
|---|---|---|
| sqlite-tie-break-red-test-trap | How to write a regression test for a database row-ordering bug so the test can't pass by coincidence | Ceiling — model passed 3/3 unaided¹ |
| bayesian-eval-discipline | Statistical discipline for A/B-testing AI systems: when to stop, minimum sample sizes, correcting for many simultaneous comparisons | Ceiling — model passed 3/3 unaided |
| append-only-evidence-design | How to build a database that provably never rewrites its own history (audit logs, evidence stores) | Ceiling — model passed 3/3 unaided |
| llm-judge-calibration | How to use one AI to grade another AI's work without the grader's known biases distorting the scores | Ceiling — model passed 3/3 unaided |

¹ This one stays in the author's private library anyway: it has two documented saves in a
different setting (catching a broken test during code review) than the one the screen measures
(writing the test from scratch). The screen result stands; the case for keeping it privately
comes through a different door. It is still not in this collection.

Two honest caveats, because receipts cut both ways:

- A ceiling means "this model didn't need the skill **on this kind of task**" — well-specified,
  self-contained tasks with a clear pass/fail. It is not proof the skill's content is wrong,
  and it says nothing about messier, longer-horizon work.
- The finding generalized: across six independently written tasks, the model passed 26 out of
  26 runs with no skill present. That says as much about how capable current models already are
  as it does about these four candidates — and it is exactly why this collection measures
  instead of assuming. The full story:
  [the double-ceiling case study](https://github.com/MrBinnacle/skill-harness/blob/main/docs/case-studies/double-ceiling-structurally-unmeasured.md).
