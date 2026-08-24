---
name: halt-as-deliverable
description: When a pre-registration, pre-flight or sanity gate refuses to produce your deliverable, the catch is often worth more than the deliverable. Use when a discipline you built caught your own work.
---

# HALT as Deliverable

## Problem

A quality discipline (pre-registration, pre-flight check, sanity gate) refuses
to produce the intended result because it detected an inconsistency in the
surrounding state. The engineer reflex is to fix the inconsistency and re-run,
treating the HALT as a setback — which discards the most valuable artifact the
work produced. A discipline-gate catching its own author's accidental
falsification, before any contaminated result ships, is an uncopyable
credibility signal: it proves the discipline works on real, unrehearsed
material. Where the framework's credibility matters more than the specific
result, the HALT is the higher-value deliverable.

## Use when

- A pre-registered prediction is falsified by a known class of error before
  the experiment executes: registry drift, version mismatch, schema change,
  baseline/tag documentation inconsistency.
- A pre-flight verification refuses the run because operational state is
  inconsistent with the experiment's preconditions.
- A self-audit, linter or regression check catches a defect in the author's
  own shipped work — the defect the audit existed to demonstrate the absence
  of.
- Any "the discipline refused to produce X, and here is why" outcome where the
  why is structurally informative rather than transient infrastructure noise.

Deciding between the two paths:

| Apply HALT-as-deliverable | Apply fix-and-re-run |
|---|---|
| The HALT reveals a structural inconsistency the audience would care about | The HALT reveals transient infrastructure (rate limit, flaky network) |
| The discipline's credibility is itself a load-bearing claim | The experiment's specific result is the load-bearing claim |
| The catching is uncopyable / hard to fake | The catching is generic / commodity |
| The audience is field-skeptical (impressed by the discipline) | The audience is result-focused (would not engage with meta) |
| The author's own work was caught | Someone else's work was caught |

## Solution

The worked record behind every step is in [`case-study.md`](case-study.md).

### 1. Commit the audit trail publicly before deciding the path forward

The HALT findings, the failed pre-registration, the pre-flight log — commit
them to public history immediately, before deciding whether to re-run. This
locks the catching in place; it cannot be retroactively papered over.

### 2. Make the catching the headline, not a quiet fix

The reflex — fix, re-run, ship the corrected number, mention the re-baseline
in passing — is correct for routine engineering and WRONG when the
discipline-catching IS the demonstration. Name the HALT in the title, document
the audit trail explicitly, narrate the discipline-catching-itself moment as
the lead. The corrected result is a number; the HALT is a story, and a story
is a character claim about the work. In fields where the dominant pattern is
"produce a confident number even when you shouldn't," publicly halting before
fabricating is itself the artifact — loudness is substance here, not
marketing.

### 3. Reframe the deliverable around the catching

If the original deliverable was "experiment produces result X showing claim
Y," the reframed deliverable is: "the discipline pre-registered claim Y,
attempted the experiment, refused to proceed because Z was inconsistent, and
here is the audit trail." Same evidence, sharper story — the catching of Z is
the demonstration of claim Y.

### 4. Multiple HALTs compound

A series of HALTs catching different classes of inconsistency (documentation
drift, operational state, environment configuration) is dramatically more
credible than one HALT plus several silent fixes. The compounded trail
triangulates what doing this honestly looks like.

## Verification

The reframe is correctly applied when:

1. The audit trail was committed to public history BEFORE the reframe. Order
   matters; backdating breaks audit integrity.
2. The headline names the HALT explicitly — "we caught X" is the lead.
3. A reader who came for the original deliverable would accept the substitute
   on its merits, not because they were told to.
4. The discipline is recoverable from the trail: someone implementing it would
   have caught the same class of error.

The reframe FAILS when the HALT reads as marketing spin; when the original
claim was specific (a number, a comparison) and the substitute is vague — the
reframe does not work for narrow factual claims; or when the audience
explicitly came for the result, where meta reads as evasion.

## Notes

- The pattern requires the discipline to be REAL — falsifiable, recoverable
  from the audit trail, applied uniformly, catching real things including the
  author's own mistakes. Decorative pre-registrations produce HALTs that do
  not generalize.
- Identity match amplifies it: "the framework I built refused to validate my
  own shipped work" is uncopyable; "the framework caught someone else's work"
  is much weaker.
- The whole pattern collapses if the framing is perceived as motivated
  reasoning. Mitigations: commit the trail first, make every input to the
  catching publicly verifiable, and report HALTs unselectively.
