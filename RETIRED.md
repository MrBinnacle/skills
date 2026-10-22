# Retired skills

Most collections only ever grow. This one also turns skills away — including its own.

A skill gets in here only when it clears the [admission policy](ADMISSION.md). The policy asks
four questions, and all four must be true. Does a current frontier model fail the job without the
skill, in a failure that was observed rather than predicted? Does that failure recur
independently? Is a skill the right control surface for it? Is the case written down so that a
later reader can see why the card entered, and retire it? Each card's `EVIDENCE.md` holds its
answers, and the evidence most cards carry is a dated record of the failure that produced them.

A screen is a different kind of evidence: the same task run with the skill and without it, scored
by a deterministic check ([skill-harness](https://github.com/MrBinnacle/skill-harness)). One
published card, `pull-rebase`, carries such runs. Its verdict and the state of each receipt live
in [its record](skills/engineering/pull-rebase/EVIDENCE.md). No other published card and no
candidate in [`_quarantine/`](_quarantine/README.md) carries a run with and without the skill.

Admission does not decide whether a card loads in every session. That is a second bar, set by
[ADR 0008](docs/adr/0008-always-on-needs-two-occasions-or-a-controlled-result.md): two counted
occasions or a controlled result. A card below it still ships, but on Claude Code it runs only
when you invoke it by name.

A screen is also the first way a skill can leave. If a newer model passes the task without the
skill, the skill can retire, removed but recorded here with the evidence intact. No skill has left
this way yet.

A skill can also leave a second way. Some carry a **pre-registered retirement trigger** in their
evidence record — a specific platform change that would make the underlying failure impossible,
named in advance so the call can't be rationalized after the fact. When that change ships, the
skill retires against its own stated criterion, no screen required: the problem is gone, not
merely outgrown. The first retirement below is one of these.

A skill can leave a third way, and it is the narrowest of the three. A card is **withdrawn on
the policy** when it cannot satisfy the admission policy it is measured against, and its own
evidence record is the proof. No screen is required, because the failing criterion counts
observed occurrences rather than measuring lift, and a screen cannot supply an occurrence that
never happened. This route fires on a criterion the card's own record demonstrably fails. An
owner who has cooled on a card has not met that bar. The second retirement below is the first
use of it.

Turning away your own work costs something: it makes the collection look smaller. That cost is the
point. A list that shrinks when the models improve is the one telling you the truth about which
skills the model still needs. Model progress becomes collection history, not silent rot.

## On watch

A card on a staged exit leaves the served set at once and is watched here before the removal is final. The rules are in [`AGENTS.md`](AGENTS.md) under "Staged retirement" and in [ADR 0007](docs/adr/0007-retirement-is-staged-for-three-exits.md). The retiring changeset opens a row. Only the rotation pass edits it afterwards.

| Card | Removed (release, install SHA, clock start) | Route | Signal (quoted predicate) | Watch closes | Sessions observed | Events (dated) | Status |
|---|---|---|---|---|---|---|---|

## Retired from the collection

| Skill | Retired | What made it unnecessary | Evidence |
|---|---|---|---|
| `claude-code-stop-hook-envelope` | 2026-07 | Claude Code now delivers the assistant's final turn inline as `last_assistant_message` on `Stop`/`SubagentStop`, and the docs recommend it *instead of* reading the transcript — the exact "response text delivered inline" trigger the skill pre-registered | [receipt (at `v1.0`)](https://github.com/MrBinnacle/skills/blob/v1.0/skills/engineering/claude-code-stop-hook-envelope/EVIDENCE.md) |
| `skill-necessity-gate` | 2026-08 | Withdrawn on the policy. It was the reference method for `ADMISSION.md`, and it could not satisfy that policy's criterion 1, which requires a failure that was observed rather than predicted. Its own record counted zero occurrences across the card's whole life | [receipt (at `v1.3.0`)](https://github.com/MrBinnacle/skills/blob/v1.3.0/skills/meta/skill-necessity-gate/EVIDENCE.md) |

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

### Retired — August 2026

The collection removed its own gate card because the gate card could not pass its own gate.

`skill-necessity-gate` was the six-gate procedure for deciding whether a capability should
become a skill, and `ADMISSION.md` named it the reference method for the collection's four
admission questions. That policy's criterion 1 asks for an unaided failure that was **observed,
not predicted**. The card's own evidence record answered, verbatim:

> **Occasions counted** | 0 — no triggering occurrence; intake exercises and audits validate use
> of the rubric but do not establish recurrence of one observed problem. **RECURRENCE-THIN**

The defect was not repairable by rewriting. An occurrence can only be found, and none appeared
across the card's whole life. This was not a new reading either: the
[S295 admission triage](dispositions/2026-08-15-S295-admission-triage.md) recorded the card as
`RECURRENCE-THIN` on 2026-08-15 and declined to act, and an evaluation-chain pass on 2026-08-28
found this card broke its evidence chain at the first link while four others reached at least
the third.

One further reading is worth stating, because it is the argument against the card that the card
itself could not answer. Its stated outcome evidence was that four candidates in this file "were
processed under this gate and none were admitted". Those candidates were processed *under* the
gate, so the gate agreeing with an outcome it produced is not independent evidence that the gate
works. That is this collection's own "don't grade your own homework" doctrine, applied to a card.

Two things outlive it, and both moved into [`AGENTS.md`](AGENTS.md) in the same change that
removed the directory, as ordinary hygiene rather than a resurrected card:

- **The topology rule** (the card's Gate 3): decide model-invocable against procedure by asking
  who does the strategic thinking, treat side effects as procedure, and surface the standing-cost
  maths so the human makes the close calls rather than the model auto-deciding them.
- **No self-authority**: a card's name, its role in this repository, its prior use, and the
  decisions it produced are not evidence for a verdict it reaches.

One reduction in assurance is accepted and recorded rather than slipped in. `ADMISSION.md` and
the gate card each declared a policy edition, and `scripts/validate_scoreboard.py` asserted the
two agreed. That lockstep is gone with the card. What survives is the stronger half: the policy
file must still carry exactly one canonical version declaration, so a partial bump cannot be
expressed in the file that binds.

## Renamed in 2.0.0

These eleven cards were renamed, not retired. Each one still ships under its current name. The
2.0.0 release replaced names that stated a whole finding with the word a reader reaches for. The
[v2.0.0 changelog entry](CHANGELOG.md#v200---2026-09-13) records the reason for each name.

Third-party directories such as [skills.sh](https://www.skills.sh/MrBinnacle/skills) can still
list an old name. An install command that uses an old name finds no skill. Use the current name
in its place.

| Old name | Current card |
|---|---|
| `click-clirunner-env-none-deletes` | [`clirunner-env`](skills/engineering/clirunner-env/SKILL.md) |
| `closure-mode-at-boundaries` | [`closure-mode`](skills/engineering/closure-mode/SKILL.md) |
| `git-pull-rebase-trap` | [`pull-rebase`](skills/engineering/pull-rebase/SKILL.md) |
| `github-pages-deploy-verification` | [`stale-deploy`](skills/engineering/stale-deploy/SKILL.md) |
| `mock-masked-stub-trap` | [`mocked-stub`](skills/engineering/mocked-stub/SKILL.md) |
| `pretooluse-bash-guard-prose-false-positive` | [`pretooluse-prose`](skills/engineering/pretooluse-prose/SKILL.md) |
| `success-test-accepts-any-output` | [`vacuous-check`](skills/engineering/vacuous-check/SKILL.md) |
| `router-skill-predicate-gap` | [`dead-predicate`](skills/meta/dead-predicate/SKILL.md) |
| `downstream-instruction-framing` | [`decision-rights`](skills/orchestration/decision-rights/SKILL.md) |
| `parallel-review-disposition-schema` | [`disposition-schema`](skills/orchestration/disposition-schema/SKILL.md) |
| `subagent-research-reliability` | [`subagent-handback`](skills/orchestration/subagent-handback/SKILL.md) |

## Screened out at the gate — July 2026

A screen can also keep a candidate out, and it can do so before its with-skill arm runs. The
registered screen has two stages. The first runs the task without the skill. The second, the
paired run with the skill and without it, starts only when the model fails at least once in the
first stage.

In July 2026, four of the author's own candidate skills went through the first stage before
admission. Only the without-skill arm ran. The test is simple to describe: give a current model
(claude-sonnet-5) a task from exactly the situation the skill was written for, but **without**
the skill, three separate times. If the model needs the skill, it should fail at least once.

It never did. All four returned three passes out of three with no skill present, so the paired
run never started for any of them. These results show that the model passed unaided. They do
not measure what the skill would have added. Three read as ceiling — nothing left for a skill
to improve on those tasks. One (`append-only-evidence-design`) was later reclassified on its
own receipt to `CANT_TELL_YET` / `wrong_instrument`: a calibration-class skill the
transformative-lift screen cannot measure, so the above-bar bare arm is not a ceiling reading.
None of the four entered the collection — including skills the author was personally convinced
were valuable. The measurement plan was published *before* the runs, so the verdicts couldn't
be bent afterward:
[the pre-registration, with each unaided run's registered result](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md).

| Candidate | What it taught | Verdict (2026-07) |
|---|---|---|
| sqlite-tie-break-red-test-trap | How to write a regression test for a database row-ordering bug so the test can't pass by coincidence | Ceiling — model passed 3/3 unaided¹ |
| bayesian-eval-discipline | Statistical discipline for A/B-testing AI systems: when to stop, minimum sample sizes, correcting for many simultaneous comparisons | Ceiling — model passed 3/3 unaided |
| append-only-evidence-design | How to build a database that provably never rewrites its own history (audit logs, evidence stores) | CANT_TELL_YET. [Receipt](https://github.com/MrBinnacle/skill-harness/blob/f75429c57c33e1191fa4b65632fce5d668a78312/docs/sers/receipts/reclass-append-only-evidence-design.json): wrong_instrument (calibration), p0 = 1.00 at 3/3 |
| llm-judge-calibration | How to use one AI to grade another AI's work without the grader's known biases distorting the scores | Ceiling — model passed 3/3 unaided |

¹ This one stays in the author's private library anyway: it has two documented saves in a
different setting (catching a broken test during code review) than the one the unaided run
measured (writing the test from scratch). The unaided result stands; the case for keeping it
privately comes through a different door. It is still not in this collection.

Two honest caveats, because receipts cut both ways:

- A ceiling means "this model didn't need the skill **on this kind of task**" — well-specified,
  self-contained tasks with a clear pass/fail. It is not proof the skill's content is wrong,
  and it says nothing about messier, longer-horizon work.
- The finding generalized: across six independently written tasks, the model passed 26 out of
  26 runs with no skill present. That says as much about how capable current models already are
  as it does about these four candidates — and it is exactly why this collection measures
  instead of assuming. The full story:
  [the double-ceiling case study](https://github.com/MrBinnacle/skill-harness/blob/main/docs/case-studies/double-ceiling-structurally-unmeasured.md).
