# Template — Adversarial-Verify Seat (upstream stage: "are the findings real?")

SKILL.md's disposition schema assumes findings are already verified. This template is how they
get verified: the same joinability principle, applied one stage earlier.

## Six invariants — every verify-seat dispatch carries all six

1. **FRESH CONTEXT** — the verifier shares no context with the finder (anti-confirmation).
2. **REFUTE POSTURE** — "your job is to try to REFUTE this finding, not confirm it."
3. **BURDEN DEFAULT** — "default to confirmed=false if you cannot independently reproduce
   it from the cited location." Uncertainty kills a finding, never sustains it.
4. **GROUND CONTACT** — name the exact artifact to read (file:line, workbook cells,
   memory dir) plus the read mechanics (tools, encodings, read-only constraints). The
   verifier reads the actual location, never the finder's summary.
5. **VERBATIM EVIDENCE** — "return the verbatim text you read as evidence." A verdict
   without quoted evidence is not a verdict.
6. **STRUCTURED VERDICT** — closed fields (`confirmed=true|false` + evidence +
   what-would-change-it), so verify outputs join mechanically.

## Skeleton

    Adversarially verify this finding is REAL, not a false positive. Read the ACTUAL
    cited location and confirm the claimed <X> exists right now. Default to
    confirmed=false if you cannot reproduce it from the cited location.

    Context: <repo root / artifact path / read mechanics / read-only constraints>
    Finding to verify: <claim + cited location + reported severity, verbatim>

    Read the cited location (and the counter-surface it is compared against). Confirm
    or refute. Return confirmed=true ONLY if you independently reproduced it. Provide
    the verbatim text you read as evidence.
    End with: status: nominal | degraded [reason] | blocked [reason]

## Notes

- In Workflow scripts the harness guidance already pushes the refute-pattern (N skeptics,
  default-refuted, majority vote); this template adds invariants 4–6, which the harness
  does not spell out. In non-Workflow dispatches (Agent tool, teammates), all six are on you.
- Verify (this template) and adjudicate (SKILL.md schema) are separate stages — do not
  collapse them into one seat. A seat that both verifies and disposes inherits the
  finder's framing, which is the bias the fresh-context invariant exists to break.

## What a fresh verifier's first verdict looked like, measured once

One private measurement, window 2026-09-28 to 2026-10-04, recorded what a verify seat built on
these invariants returns after the earlier checks have passed. Agent-built pull requests went
through an implement step, a same-family self-review, an acceptance gate and CI. A non-author
verifier then ran each change in a clean checkout. On pull requests whose head had green CI, the
verifier's first verdict was FAIL on 22 of 34 (65%). Remove the FAILs whose only findings were a
false or stale PR body, and the findings the verifier located in the ticket itself, and the
behavioural figure is 19 of 34 (56%). The pull requests named in a gate-green log give 21 of 27
(78%). That population is more selected, not cleaner.

This is a first-verdict disagreement rate. It is not a catch rate and not an escaped-defect rate.
Four caveats travel with it:

1. **Unadjudicated.** A FAIL is the verifier's call, not ground truth. Nobody has checked how
   many of the FAILs were wrong.
2. **Small n, one week.** 40 pull requests, 35 tickets, 22 pull requests in the key population.
3. **Model family unseparated.** Most verifiers and builders were Claude. The independence
   measured is a fresh seat that executes the change, not a different model family.
4. **Selection.** Only pull requests that someone chose to verify have a verdict. If suspicion
   triggered verification, every rate is an upper bound. The size of that effect is UNMEASURED.

What the figure shows: in that window a fresh verify seat blocked changes that a green gate and
green CI had passed, on most pull requests. What it does not show: that those FAILs were right,
or that the seat is worth its cost.
