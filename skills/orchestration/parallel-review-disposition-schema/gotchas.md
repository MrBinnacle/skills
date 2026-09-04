# parallel-review-disposition-schema — gotchas

Append-only convention — gotchas are stress-test signal, not failure
evidence. Never delete; observed supersedes anticipated by addition.

## [ANTICIPATED] Decision-vocabulary too coarse for the actual decision space

A generic enum can collapse two genuinely-different dispositions into one bucket,
forcing seats to pick a wrong-but-closest member. Synthesis then surfaces a
"DEFINITION_AXIS disagreement" that's really "seats were forced into the wrong slot."

**Mitigation:** derive the enum from the corpus's actual decision space before dispatching,
not from a template. For a fresh corpus, draft the enum + sanity-check it against 3–4
representative findings to confirm each lands cleanly.

**Trigger to replace with [OBSERVED]:** a fire where the synthesizer classifies a
disagreement as DEFINITION_AXIS and the resolution turns out to be "we need a new enum
member," not a glossary-pass.

## [ANTICIPATED] Per-item output block drifts into free-form prose

A seat that has more to say abandons the per-item block and writes paragraphs. Now its
output isn't joinable with the others' on the same finding.

**Mitigation:** keep the block tight (≤5 fields; "Reasoning ≤3 sentences"; "What-would-change-it"
≤1 sentence). Painless blocks get filled. State the format explicitly + give a one-line
worked example in the prompt so the seat sees the shape, not just the field names.

**Trigger to replace with [OBSERVED]:** a seat returns prose for a finding it owns instead
of the block.

## [ANTICIPATED] Bounded-verification carve-out used as an escape from a large re-dispatch

A companion council-orchestration gotcha names two tiers of scope-correction: bounded (≤3-file
hub-read, do it inline) and large (re-dispatch the affected seats via SendMessage). "I'll
just read a few more files" is the failure mode — silently expands into 8+ reads + missing
peer context.

**Mitigation:** name the read-budget upfront in the synthesizer's scope-correction step
(≤3 reads). If a hub verification exceeds it, stop and re-dispatch the seat; do not push
through.

**Trigger to replace with [OBSERVED]:** a hub "bounded" verification that took >3 reads
and missed a peer-level finding that a re-dispatched seat would have caught.

## [ANTICIPATED] Uneven item-ownership distorts depth

One seat owns 10 items, another owns 1. The overloaded seat skims; the lightly-loaded
seat over-elaborates. Synthesis sees inconsistent depth that reads as "the overloaded
seat dropped balls" — which is structural, not a quality flag.

**Mitigation:** when assigning ownership, target ≤4 items per seat for the disposition
pass. If a single lens genuinely owns most items, split it into sub-lenses (e.g. "Security:
operator-boundary" + "Security: data-layer") rather than dispatching one overloaded seat.

**Trigger to replace with [OBSERVED]:** a fire where the per-item depth of an overloaded
seat is visibly shallower than peers'.

## [ANTICIPATED] Status line treated as decorative

`status: nominal | degraded | blocked` is mandatory for a reason — the synthesizer treats
a `degraded` divergence as INFORMATION_AXIS-prone (tooling artifact, not real disagreement).
If seats omit the line or always return `nominal`, the signal is lost and a degraded seat's
lone finding silently drops into "agreements" or "unaddressed" wrongly.

**Mitigation:** state in the prompt that the line is mandatory; absence halts synthesis.
If a seat had a real degradation (missing tool, blocked read, refused to do part of the
job), it MUST say so structurally. Worked example in the prompt.

**Trigger to replace with [OBSERVED]:** a fire where post-hoc analysis finds a seat was
degraded but reported `nominal`, and a finding was misclassified as a result.

## [ANTICIPATED] Synthesizer rubber-stamps the enum without checking same-enum-different-concept

Two seats both choose `sub-item-of-SEC-N` for the same finding — looks like agreement.
But seat A meant "sub-item under SEC-N's existing scope" and seat B meant "new sub-item
that EXPANDS SEC-N's scope." Same enum member, different semantic.

**Mitigation:** the Critic / post-synthesis pass must explicitly check enum convergences
for shared-word/different-concept (the role-council bias-7/8 lens applies). The shared
enum reduces but does not eliminate false-agreement; it just relocates it from "same word
in prose" to "same enum member."

**Trigger to replace with [OBSERVED]:** a fire where the post-synthesis Critic catches an
enum-level false agreement that the mechanical synthesizer missed.

## [OBSERVED] Reviewer-local ID collision silently drops a finding at consolidation

Folded 2026-08-17 (S306) from the quarantine card `fix-brief-consolidation-id-hygiene`,
per the S305 Gate-0 routing (layer finding: this card's content belongs here, not as a
standalone skill). The incident is real, not anticipated: in the Skill Harness Track E
ai-slop fix-brief, two reviewers each numbered their findings M1–M5 locally; the
consolidator flattened them into one global M1–M5 list, kept reviewer E.1's M4 under the
consolidated name "M3", and silently dropped E.1's actual M3 (`(BootstrapError, Exception)`
redundant tuple, `cli/main.py:573, 1442`). The dropped bug persisted across 4 commits and
was re-surfaced months later by a fresh-context reviewer as a "new" finding.

**Mitigation — pick ONE before consolidating, never after:**

- **A. Globally-unique IDs at source:** each seat's dispatch prompt requires a
  seat-of-origin prefix (`E1-M1`, `E2-M1`, …); the consolidator pastes IDs as-is with no
  re-numbering step. Collision-impossible; the only cost is wordier IDs.
- **B. Rollup table:** the consolidated brief opens with a
  `| Reviewer | Local ID | Consolidated ID | Status |` table covering EVERY per-seat
  finding — a collision then reads as a visible duplicate row, not an invisible drop.
- **C. Don't flatten:** per-seat subsections in the brief; the fix-loop dispatch reads all
  sections.

**Falsifying count check (run it on any consolidation):** distinct findings in the
consolidated brief must equal the sum of per-seat finding counts minus EXPLICIT
reclassifications (EQUIVALENT / DEFER / discharged). Any further reduction is a silent
drop. If per-seat raw outputs were not preserved, the consolidation lacks audit-trail
integrity — that itself is a finding. When a drop is detected post-hoc, disclose it in the
next brief; never silently fix it.

## [ANTICIPATED] The envelope is filled in and the namespace still is not

A panel adopts PROVIDER-ENVELOPE.md, every return carries `run_id`, `stage_id` and
`provider_id`, and the finding IDs inside `findings` are still seat-local `M1`-`M5`.
The envelope then identifies the provider while the findings it carries stay collidable,
which is the 2026-08-17 drop with more metadata around it.

**Mitigation:** the namespace is a property of the finding ID, not of the wrapper. State the
prefix each seat must use in its own dispatch prompt, and run the falsifying count check
above over the consolidated brief regardless of how the returns were wrapped.

**Trigger to replace with [OBSERVED]:** a consolidation where every envelope validated and
two findings still shared an ID.
