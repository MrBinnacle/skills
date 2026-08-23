---
name: fix-brief-consolidation-id-hygiene
description: |
  Use when synthesizing findings from N parallel reviewers/seats/SMEs into a single
  fix-brief, disposition doc, or punch list. Prevents the "reviewer-local M-ID
  collision drops a finding" failure mode where each reviewer's local M1/M2/M3
  numbering collides at the consolidation layer and one reviewer's finding gets
  silently dropped while another reviewer's same-numbered finding is kept under
  the consolidated label. Specifically: (1) N-seat parallel council fires
  producing per-seat findings, (2) multi-reviewer ai-slop / code-review /
  security-audit dispatches, (3) any synthesis step that flattens
  per-reviewer-local IDs into a global brief.
author: Claude Code
version: 1.0.0
date: 2026-06-07
---

# Fix-Brief Consolidation ID Hygiene

## Problem

When the orchestrator consolidates findings from N parallel reviewers into a single
fix-brief, each reviewer's output uses local IDs (M1, M2, M3 …) within their own
output. The consolidator's natural move — re-numbering globally as M1, M2, M3 …
in the fix-brief — produces silent drops when two reviewers each had a "M3" and
the consolidator keeps one under the name "M3" while dropping the other.

This is not theoretical. It happened in the Skill Harness project Track E ai-slop
fix-brief: Track E.1 reviewer's M3 (`(BootstrapError, Exception)` redundant tuple
at `cli/main.py:573, 1442`) was silently dropped because the consolidator kept
E.1's M4 (`import sqlite3 as _sqlite3` alias rename) under the consolidated name
"M3". The bug persisted across 4 commits and was caught by an independent
fresh-context Phase 3.4 reviewer who re-surfaced it. The orchestrator had to
publicly disclose the drafting error in the next fix-brief.

## Context / Trigger Conditions

- N parallel reviewers each producing findings labeled M1, M2, M3 …
- A consolidation step that flattens per-reviewer IDs into one shared list
- A subsequent fix-loop dispatch that reads only the consolidated brief
- Symptom: a fresh-context reviewer (later) flags a finding the prior consolidation
  appeared to address but actually dropped
- Symptom: hub-verification of the supposedly-addressed finding shows the code
  pattern is still present

Applies to:
- Multi-seat council fires (dev-team-council, parallel-review-disposition-schema)
- Multi-track ai-slop sentinel reviews (one per code surface)
- Multi-domain security audits (one per lens — injection, authz, secrets, etc.)
- Any disposition document that aggregates N → 1

## Solution

**Three discipline options. Pick one BEFORE consolidating.**

### Option A · Globally-unique IDs at the source

Instruct each dispatched reviewer to prefix their IDs with a reviewer-of-origin
tag in their dispatch prompt. E.g.:

- E.1 reviewer outputs: `E1-C1`, `E1-I1`, `E1-M1`, `E1-M2`, `E1-M3`, …
- E.2 reviewer outputs: `E2-C1`, `E2-T1`, `E2-M1`, …
- E.3 reviewer outputs: `E3-C1`, `E3-M1`, …

Consolidator pastes the prefixed IDs as-is into the fix-brief. No re-numbering
step. No collision. The drawback is fix-brief IDs become wordier; the
load-bearing benefit is collision-impossible.

### Option B · Explicit cross-reviewer rollup table

At the top of the consolidated fix-brief, include a table mapping every
per-reviewer ID to its consolidated counterpart:

```
| Reviewer | Local ID | Consolidated ID | Status |
|---|---|---|---|
| E.1 | M1 | M1 | FIX-NOW |
| E.1 | M2 | M2 | FIX-NOW |
| E.1 | M3 | M3 | FIX-NOW |
| E.1 | M4 | M4 | FIX-NOW |
| E.1 | M5 | M5 | NO-ACTION |
| E.2 | M1 | M5 | … |  ← collision visible
```

The collision becomes a typo a future reviewer can spot. Without the rollup
table, the collision is invisible.

### Option C · Per-reviewer subsections in the fix-brief

Don't flatten. Structure the fix-brief as:

```
## E.1 findings
- M1 · …
- M2 · …
- M3 · …  ← the BootstrapError tuple, intact
- M4 · …

## E.2 findings
- M1 · …
- M2 · …
- M3 · …  ← no collision; this is E.2's M3
```

The fix-loop dispatch reads both sections. No flattening, no collision.

## Verification

A consolidation step is hygienic when this falsifying procedure succeeds:

1. Open each per-reviewer raw output.
2. Count distinct findings per reviewer (let counts be `n1, n2, …, nk`).
3. Count distinct findings in the consolidated fix-brief that cite a
   reviewer-specific anchor (file:line + invariant).
4. The consolidated count MUST equal `sum(n1..nk)` minus any explicit
   "discharged as discharged" / "EQUIVALENT" / "DEFER" reclassifications.
5. Any reduction beyond explicit reclassifications is a silent drop.

If you can't run this procedure (because per-reviewer outputs aren't preserved),
the consolidation lacks audit-trail integrity — that itself is a finding.

## Example

**Failure mode (what happened in Skill Harness Track E ai-slop fix-brief):**

E.1 reviewer surfaced 5 minors:
- M1 (dead defensive code) · `storage/recovery.py:63,100`
- M2 (unreachable early-return) · `storage/recovery.py:66-67`
- M3 (`(BootstrapError, Exception)` redundant tuple) · `cli/main.py:573, 1442`
- M4 (`import sqlite3 as _sqlite3` aliased re-import) · `cli/main.py:1431`
- M5 (`evidence_conn_ro` name [uncertain]) · NO-ACTION

E.2 reviewer surfaced 5 minors with their own local IDs M1-M5.

When the orchestrator consolidated, the fix-brief listed:
- M1 (E.1's M1) · dead defensive code
- M2 (E.1's M2) · unreachable early-return
- M3 (**E.1's M4**, the alias re-import) · ← E.1's M3 silently dropped here
- M4 (E.2's M2, bare except Exception) · …
- M5 (E.2's M3, type degradation) · …

The fix-loop agent dutifully addressed everything in the consolidated brief.
The `(BootstrapError, Exception)` tuple persisted at `cli/main.py:573` and
`:1452` across 4 commits. Phase 3.4 reviewer (fresh context, independent)
caught it months later as a "new" finding (M5 in their output) — when actually
it was an old reviewer's finding that the orchestrator had silently dropped.

**Successful mode (what should have happened with Option B):**

Same E.1 findings + a rollup table at the top of the consolidated brief showing
E.1-M1, E.1-M2, E.1-M3 (`BootstrapError tuple`), E.1-M4 (`sqlite3 alias`),
E.1-M5 mapped to consolidated M1-M5. The map makes it visually obvious that
E.1-M3 and E.1-M4 cannot both occupy consolidated M3 — forcing the orchestrator
to renumber or split.

## Notes

- This pattern is independent of which review skill produced the findings
  (`ai-slop-sentinel`, `code-review-sentinel`, `security-audit`, etc.). It's a
  consolidation-layer discipline, not a review-layer discipline.
- The hazard is highest when reviewers are dispatched in PARALLEL (each unaware
  of the others' findings). Sequential dispatch can mitigate by having each
  reviewer see the prior reviewer's IDs, but parallelism is the default for
  most council fire patterns.
- The hazard is ALSO present when re-using the same reviewer in a different
  role — e.g., one Opus 4.7 reviewer for code-review, then a separate
  re-dispatch for security-audit. Each role produces its own M-ID sequence;
  the consolidator must not collide them.
- Companion skills: `parallel-review-disposition-schema` (output contract for
  parallel reviewers), `cross-talk-council-dispatch` (dispatch mechanics),
  `verbatim-content-subagent-dispatch` (input contract for the reviewers).
- Disclosure pattern: when a drop is detected post-hoc, the consolidator should
  disclose the drafting error in the next fix-brief (not silently fix it).
  Maintaining the audit trail is a load-bearing project memory pattern.

## See also

- `parallel-review-disposition-schema` — the output contract this discipline
  augments
- `verbatim-content-subagent-dispatch` — input-side discipline for dispatching
  reviewers
- `cross-talk-council-dispatch` — when reviewers should predict each other's
  findings (which itself helps surface collisions when one reviewer correctly
  predicts another reviewer's finding that ends up dropped)
