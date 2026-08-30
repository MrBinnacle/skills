# Retired skills

Most collections only ever grow. This one also turns skills away — including its own.

Before a skill gets in here, it has to prove the current model still needs it: the same task,
run with the skill and without it, scored by a deterministic check
([skill-harness](https://github.com/MrBinnacle/skill-harness)). If the model passes without the
skill, there's nothing left for the skill to improve, and it stays out. The same test
retires skills already in the collection when a newer model outgrows them — removed, but recorded
here with the evidence intact.

A skill can also leave a second way. Some carry a **pre-registered retirement trigger** in their
evidence record — a specific platform change that would make the underlying failure impossible,
named in advance so the call can't be rationalized after the fact. When that change ships, the
skill retires against its own stated criterion, no screen required: the problem is gone, not
merely outgrown. The first retirement below is one of these.

Turning away your own work costs something: it makes the collection look smaller. That cost is the
point. A list that shrinks when the models improve is the one telling you the truth about which
skills the model still needs. Model progress becomes collection history, not silent rot.

## Retired from the collection

| Skill | Retired | What made it unnecessary | Evidence |
|---|---|---|---|
| `claude-code-stop-hook-envelope` | 2026-07 | Claude Code now delivers the assistant's final turn inline as `last_assistant_message` on `Stop`/`SubagentStop`, and the docs recommend it *instead of* reading the transcript — the exact "response text delivered inline" trigger the skill pre-registered | [receipt (at `v1.0`)](https://github.com/MrBinnacle/skills/blob/v1.0/skills/engineering/claude-code-stop-hook-envelope/EVIDENCE.md) |

### Retired — July 2026

`claude-code-stop-hook-envelope` taught how to recover the assistant's final response text inside
a Claude Code `Stop` hook. At the time that meant resolving `transcript_path` and reading the last
message out of the transcript file — because the hook's stdin envelope did not carry the reply.
Claude Code has since added a `last_assistant_message` field that delivers that text inline, and
its [hooks documentation](https://code.claude.com/docs/en/hooks) now recommends using it *instead
of* reading the transcript (which "is written asynchronously and may lag"). That is precisely the
"response text delivered inline" condition the skill's
[evidence record](https://github.com/MrBinnacle/skills/blob/v1.0/skills/engineering/claude-code-stop-hook-envelope/EVIDENCE.md)
had pre-registered as its retirement trigger — so it retires, platform-fixed, record intact.

One general lesson outlives it, as ordinary hook hygiene rather than a skill: a `Stop` hook's stdin
is a JSON envelope, so a hook that greps it blindly can sit green and never fire. Worth a one-line
test when you write one — no longer worth a dedicated card.

## Screened out at the gate — July 2026

The same test that will someday retire skills also decides what gets in. It has already fired.

In July 2026, four of the author's own candidate skills were screened before admission. The
test is simple to describe: give a current model (claude-sonnet-5) a task from exactly the
situation the skill was written for — but **without** the skill — three separate times. If the
model needs the skill, it should fail at least once.

It never did. All four returned three passes out of three with no skill present. Three read
as ceiling — nothing left for a skill to improve on those tasks. One
(`append-only-evidence-design`) was later reclassified on its own receipt to `CANT_TELL_YET` /
`wrong_instrument`: a calibration-class skill the transformative-lift screen cannot measure, so
the above-bar bare arm is not a ceiling reading. None of the four entered the collection —
including skills the author was personally convinced were valuable. The measurement plan was
published *before* the runs, so the verdicts couldn't be bent afterward:
[the pre-registration, with each screen's registered result](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md).

| Candidate | What it taught | Verdict (2026-07) |
|---|---|---|
| sqlite-tie-break-red-test-trap | How to write a regression test for a database row-ordering bug so the test can't pass by coincidence | Ceiling — model passed 3/3 unaided¹ |
| bayesian-eval-discipline | Statistical discipline for A/B-testing AI systems: when to stop, minimum sample sizes, correcting for many simultaneous comparisons | Ceiling — model passed 3/3 unaided |
| append-only-evidence-design | How to build a database that provably never rewrites its own history (audit logs, evidence stores) | CANT_TELL_YET. [Receipt](https://github.com/MrBinnacle/skill-harness/blob/f75429c57c33e1191fa4b65632fce5d668a78312/docs/sers/receipts/reclass-append-only-evidence-design.json): wrong_instrument (calibration), p0 = 1.00 at 3/3 |
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
