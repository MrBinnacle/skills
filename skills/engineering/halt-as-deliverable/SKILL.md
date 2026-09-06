---
name: halt-as-deliverable
description: When a pre-registration, pre-flight or sanity gate refuses to produce your deliverable, the catch is often worth more than the deliverable. Use when a discipline you built caught your own work.
---

# HALT as Deliverable

Decide what to publish after one of your own gates has refused to produce a result. You get a ruling — publish the refusal, or fix and re-run — plus the order the audit trail has to be committed in for the published version to hold up.

A recorded case, 2026-06-08. A pre-flight check refused a pre-registered cross-vendor run: the scorer registry had grown between the baseline and the tag the case study cited, so the study's own headline figure was not reproducible at the tag it named. A second check then refused the re-baseline over three environment mismatches. Zero subject calls, zero spend. The catching was done by the harness's pre-flight gates, not by this card — this card decides what happens next. The run in full is in [`case-study.md`](case-study.md); its provenance and the other recorded occurrences are in [`EVIDENCE.md`](EVIDENCE.md).

## Use when

- A pre-registered prediction is falsified before the experiment runs: registry drift, version mismatch, schema change, baseline or tag inconsistency.
- A pre-flight check refuses a run because operational state does not match the experiment's preconditions.
- A self-audit, linter or regression check finds a defect in the author's own shipped work — the defect the audit existed to show was absent.
- Any "the discipline refused to produce X, and here is why" outcome where the why is structural rather than transient noise.

## Choose the path

| Publish the HALT | Fix and re-run |
|---|---|
| The HALT shows a structural problem the audience would care about | The HALT shows transient infrastructure: a rate limit, a flaky network |
| The discipline's credibility is itself a claim you are making | The experiment's specific result is the claim you are making |
| The catch is hard to fake | The catch is generic |
| The audience is skeptical of the field | The audience came for the result and will read meta as evasion |
| Your own work was caught | Someone else's work was caught |

Identity match is what makes it strong. "The gate I built refused my own shipped work" is hard to copy. "The gate caught someone else's work" is much weaker.

## Procedure

Do these in order. The order is the part that fails audit if you get it wrong.

### 1. Commit the audit trail publicly, before you decide the path

Commit the HALT findings, the failed pre-registration and the pre-flight log to public history first. Decide afterward. This locks the catch in place so it cannot be papered over later.

### 2. Make the catch the headline

The reflex is to fix, re-run, ship the corrected number and mention the re-baseline in passing. That is right for routine work and wrong when the gate catching you IS the demonstration. Name the HALT in the title. Lead with it.

### 3. Reframe the deliverable around the catch

If the original was "the experiment produces X, which shows Y", the reframe is: "we pre-registered Y, ran the experiment, refused to proceed because Z was inconsistent, and here is the trail." Same evidence. The catching of Z is the demonstration of Y.

### 4. Report every HALT, not the flattering ones

A series of HALTs across different classes — documentation drift, operational state, environment configuration — is far more credible than one published HALT beside a run of quiet fixes. Selective reporting is what turns this into spin.

## Verification

All four must hold:

1. The audit trail reached public history BEFORE the reframe. Backdating breaks it.
2. The headline names the HALT.
3. A reader who came for the original deliverable accepts the substitute on its merits, not because you told them to.
4. Someone implementing the discipline from your trail would catch the same class of error.

It has failed when the reframe reads as spin, when the original claim was a specific number or comparison and the substitute is vague, or when the audience came for the result. [`gotchas.md`](gotchas.md) logs the failure modes seen so far.

## The precondition

The discipline has to be real: falsifiable, recoverable from the trail, applied uniformly, and catching your own mistakes as readily as anyone's. A decorative pre-registration produces a HALT that generalizes to nothing.

The whole thing collapses if a reader reads the framing as motivated. Commit the trail first, make every input to the catch publicly checkable, and report HALTs unselectively.
