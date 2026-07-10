# Template — Adversarial-Verify Seat (upstream stage: "are the findings real?")

Extracted 2026-07-04 from 22 mined dispatch instances (the author's research-project dispatch miner;
two live variants: Workflow refute-pattern, teammate verifier-seat). SKILL.md's
disposition schema assumes findings are already verified — this template is how they
get verified. Same joinability principle, applied one stage earlier.

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
