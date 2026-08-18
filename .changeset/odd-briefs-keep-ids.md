---
"mrbinnacle-skills": patch
---

Fold the consolidation-ID-hygiene finding into `parallel-review-disposition-schema` as an OBSERVED gotcha.

The S305 quarantine Gate-0 run (2026-08-17) routed the private candidate card `fix-brief-consolidation-id-hygiene` here as a layer finding: its content is a consolidation-layer discipline for the output contract this card already owns, not a standalone skill. The appended gotcha records the observed incident — two parallel reviewers' local M1–M5 numbering collided at consolidation, one reviewer's M3 was silently dropped under a kept same-numbered finding, and the dropped bug persisted across 4 commits — plus the three mitigation options (source-prefixed IDs, a rollup table, or per-seat subsections) and the falsifying count check that detects a silent drop. The card's `Occasions counted` row is unchanged: the incident is the folded card's evidence, not a recurrence of this card's own failure mode.
