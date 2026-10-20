---
name: disposition-schema
description: Use when dispatching parallel agents to verify or adjudicate findings (adversarial verify, security disposition, council fires), or before you consolidate their outputs and risk an ID collision.
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
- Security-audit disposition (file a new ID / fold as sub-item / change severity / defer / track as a work item),
  design or spec review triage, threat-model coverage passes, any "route this finding-set" fire.
- Symptom you're trying to avoid: a previous multi-agent fire returned good individual analyses
  that you then struggled to synthesize, or produced an "agreement" that was really a
  shared-word / divergent-concept collision.

## Solution

Put all five of these in EVERY seat's dispatch prompt:

1. **A fixed DECISION VOCABULARY (enum).** Every seat picks its disposition for each owned item
   from the same closed list. For a security audit, e.g.:
   `NEW-ID | sub-item-of-<existing> | severity-change | scope-change | track-as-work-item | evidence-record-only | defer`.
   A closed enum forces comparable decisions; free-form "recommendations" don't join.

2. **A shared per-item OUTPUT BLOCK.** One block per item, same fields, e.g.:
   `{Item · Verified?(cite) · Disposition(from enum) · Severity(if applicable) · Reasoning <=3 sentences · What-would-change-it}`.
   "What-would-change-it" is the highest-value field — it exposes the assumption the disposition rests on
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
  finding re-scopes another's premise (a cross-build), the hub reads the few files and confirms
  it directly; re-dispatch a seat only when the corrected scope is large. Deferring a
  cross-build to "a later ticket" is the common failure.

## Verification

- [ ] Every seat prompt carries all five elements above, with its own ID prefix.
- [ ] Every return ends with a status line, and synthesis lists each `degraded` or `blocked` seat.
- [ ] Count check: distinct findings in the consolidated brief equal the sum of per-seat counts,
      minus explicit reclassifications (EQUIVALENT, DEFER, discharged). A shortfall is a silent drop.
- [ ] Raw per-seat returns are kept, so the count check can be rerun.
- [ ] A Critic pass over all outputs checked each agreement ("4 seats agree") for one word with
      two meanings.
- [ ] Each cross-build was confirmed by a bounded hub read or re-dispatched, not deferred.

Origin fire, 2026-05-29: 12 seats given the same enum, block, ownership and status line
synthesized into one document with five classified disagreements, and two cross-builds were
confirmed by bounded hub reads. An earlier fire on the same corpus with loose prompts produced a
false agreement and a deferred re-scope. Later fires: [EVIDENCE.md](EVIDENCE.md).

## Example

Shared block, identical in every seat:

    Corpus: 9 verified findings from a login-service audit. Decide each one.
    Enum: NEW-ID | sub-item-of-<existing> | severity-change | scope-change | track-as-work-item
          | evidence-record-only | defer

One seat's prompt, then its return:

    YOUR SEAT: data layer. Prefix your IDs B-. YOU OWN: F-4 (session token stored unhashed,
    db/session.py:41), F-7 (no rate limit on the password-reset route).

    B-1 · F-4 · Verified: db/session.py:41 writes the raw token · NEW-ID · High ·
          A leaked table yields live sessions. · Changes if tokens expire within a minute.
    B-2 · F-7 · Verified: routes/reset.py:12 has no limiter · sub-item-of-AUTH-3 · Medium ·
          AUTH-3 already covers brute force on login. · Changes if AUTH-3 excludes reset.
    status: nominal

Synthesis groups B-1 with other seats' NEW-ID returns. The IDs pass through unchanged.

## Notes

Open [gotchas.md](gotchas.md) when consolidator renumbering drops a seat-local finding ID, or before choosing a namespace strategy. It records the observed ID collision with its mitigations, and the anticipated schema failures.

