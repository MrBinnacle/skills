---
name: parallel-review-disposition-schema
description: Use when dispatching parallel agents to verify/adjudicate findings — adversarial verify, security disposition, design triage, council fires. Shared disposition schema so seat outputs join cleanly.
---

# Parallel Review / Disposition Schema

## Problem

Five reviewers send back five good analyses that don't add up to one decision. That is the
default outcome when you dispatch isolated agents to review the same set of findings:
isolation is what keeps them from groupthinking each other, but it also means each one
answers in its own free-form prose, two of them use the same word for different concepts, and
you spend the synthesis pass reconciling formats instead of substance.

The fix is upstream, in the dispatch: isolated outputs are synthesizable only if you
pre-impose a shared output schema + a fixed decision vocabulary. You can't recover
comparability after the fact.

## Context / Trigger Conditions

- Dispatching 3+ parallel agents (subagents / council seats / a swarm) to ADJUDICATE a set of
  already-verified findings — i.e. the decision is "what to DO with each finding," not "are
  the findings real."
- For the upstream "are the findings real" stage — adversarial VERIFY seats on freshly-found
  findings — use [ADVERSARIAL-VERIFY-SEAT.md](ADVERSARIAL-VERIFY-SEAT.md)
  (refute posture, burden default, verbatim evidence; same joinability principle).
- Security-audit disposition (file a new ID / fold as sub-item / change severity / defer / WI),
  design or spec review triage, threat-model coverage passes, any "route this finding-set" fire.
- Symptom you're trying to avoid: a previous multi-agent fire returned good individual analyses
  that you then struggled to synthesize, or produced an "agreement" that was really a
  shared-word / divergent-concept collision.

## Solution

Put all five of these in EVERY seat's dispatch prompt:

1. **A fixed DECISION VOCABULARY (enum).** Every seat picks its disposition for each owned item
   from the same closed list. For a security audit, e.g.:
   `NEW-ID | sub-item-of-<existing> | severity-change | scope-change | <non-finding>-WI | evidence-record-only | defer`.
   A closed enum forces comparable decisions; free-form "recommendations" don't join.

2. **A shared per-item OUTPUT BLOCK.** One block per item, same fields, e.g.:
   `{Item · Verified?(cite) · Disposition(from enum) · Severity(if applicable) · Reasoning <=3 sentences · What-would-change-it}`.
   "What-would-change-it" is the highest-value field — it exposes the load-bearing assumption
   and is what the synthesizer uses to classify a disagreement as values/information/definition.

3. **Explicit ITEM-OWNERSHIP per seat.** Assign each seat the specific findings it owns (by its
   lens), with the evidence inline. Otherwise every seat re-derives the whole corpus, burning
   tokens and producing overlapping mush. Compress the SHARED context once (what the corpus is,
   the current state, the vocabulary) and state it identically in each prompt — isolated agents
   can't see it otherwise.

4. **A mandatory STATUS line** ending every output: `status: nominal | degraded [reason] | blocked [reason]`
   (or a confidence tag). A seat that couldn't do its job must say so structurally, so the
   synthesizer treats its divergence as a tooling artifact, not a real disagreement — and so a
   degraded seat's lone finding lands in "unaddressed," not silently dropped.

5. **NAMESPACED finding IDs, assigned at dispatch.** Each seat prefixes its findings with its
   own seat of origin (`E1-M1`, `E2-M1`, ...) and the consolidator pastes them through
   unchanged. Seats number locally by default, so their IDs collide, and a consolidator that
   renumbers turns a collision into a silently dropped finding — observed, with the count
   check that catches it, in gotchas.md. Namespacing makes the collision impossible; a rollup
   table or per-seat subsections make it visible instead. Choose one before consolidating.

When the panel is not flat — mixed provider kinds, one stage feeding the next, a seat
recruiting its own specialist, or a provider that can fail or abstain — wrap each return in
[PROVIDER-ENVELOPE.md](PROVIDER-ENVELOPE.md), whose `run_id` + `stage_id` + `provider_id`
supplies the namespace element 5 needs.

Two discipline notes that pair with the schema:
- **Don't let the schema substitute for verification.** Tell seats to spot-verify the specific
  claims they rely on (cite file:line), especially if prior passes on this corpus shipped errors.
- **Bounded cross-builds: the hub verifies inline; large ones re-dispatch.** When one seat's
  finding re-scopes another's premise (a cross-build), if confirming it is a bounded read
  (a few files) the hub/synthesizer should verify it DIRECTLY rather than deferring it to a
  follow-up ticket; only re-dispatch a seat when the corrected scope is large. (Deferring a
  cross-build to "a later ticket" is the common failure.)

## Verification

A personal production project's phase-2 security-audit lock (2026-05-29): a 12-seat fire (6 security postures + Architect + Planner
+ 4 domain SMEs) each given the same disposition enum + per-finding block + ownership + status
line returned outputs that synthesized into one clean 8-section document with five cleanly-classified
disagreements — because the decisions were directly comparable. Two cross-builds (a wrong entropy
claim; an un-verified injection-gap) were caught at synthesis and confirmed by bounded hub-reads
rather than deferred. A prior fire on the same corpus, run with looser prompts, had produced an
"agreement" that was a shared-word/different-scope collision and deferred a re-scope to a ticket —
the exact failures this schema removes.

## Example

Shared block injected into each seat (compressed): corpus summary + current-state + the enum.
Then per seat: `YOUR SEAT: <lens>. YOU OWN: <findings + evidence>. For each: {Finding · Verified?(file:line)
· Disposition(enum) · Severity · Reasoning <=3 · What-would-change-it}. End with: status: ...`.
Synthesis then groups by enum value, not by re-reading prose.

## Notes

- The synthesis is only ever as clean as the input schema. Spend the care in the dispatch prompts.
- Isolation stays the anti-cascade feature — the schema is what makes isolated outputs JOINABLE
  without letting agents see each other.
- Round-number agreement counts ("4 seats agree") are suspect until the synthesizer checks they
  mean the same thing — a single all-outputs lens (a Critic role) catches shared-word collisions
  that mechanical counting cannot.

