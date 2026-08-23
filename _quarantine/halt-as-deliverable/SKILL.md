---
name: halt-as-deliverable
description: |
  Use when a quality-discipline (pre-registration check, pre-flight verification,
  sanity gate, audit-trail check) catches an inconsistency in your own work
  BEFORE the intended deliverable is produced. The catch itself is often more
  credible than the deliverable would have been. Reframe the HALT as the
  deliverable; document the audit trail publicly; make the catching loud.
  Specifically triggers when: (1) a pre-registered prediction is falsified by
  a known-class-of-error (registry drift, version mismatch, schema change)
  before the experiment runs, (2) a pre-flight check refuses to proceed because
  the operational state is inconsistent with the experiment's preconditions,
  (3) any discipline-gate produces a "refused to run because X" outcome where
  X is itself informative. The temptation is to quietly fix X and re-run; the
  high-leverage move is often the opposite — publish X as the demonstration.
author: Claude Code
version: 1.1.0
date: 2026-06-09
---

# HALT as Deliverable

## Problem

A quality discipline (pre-registration, pre-flight check, sanity gate) refuses
to produce the intended experiment result because it detected an inconsistency
in the surrounding state. The natural engineer response is to fix the
inconsistency and re-run, treating the HALT as a setback. This often discards
the most valuable artifact the work produced.

A discipline-gate catching its own author's accidental falsification — before
any contaminated result is shipped — is an uncopyable credibility signal. It
proves the discipline works on real, unrehearsed material. The fix-and-re-run
path produces the original intended deliverable; the HALT-as-deliverable path
produces a meta-deliverable that demonstrates the discipline catching itself.
In contexts where credibility of the framework matters more than the specific
experimental result, the meta-deliverable is the higher-value artifact.

## Context / Trigger Conditions

- A pre-registered prediction is falsified by a known-class-of-error before
  the experiment is executed: registry drift, version mismatch, schema change,
  documentation inconsistency between baseline and tag.
- A pre-flight verification (env-var check, scorer registry check, persistence-
  state check) refuses the run because operational state is inconsistent with
  the experiment's preconditions.
- A self-audit / linter / regression check catches a defect in the author's own
  shipped work that the audit was supposed to demonstrate the absence of.
- Any "the discipline refused to produce X, here's why" outcome where the why
  is structurally informative (not just transient infrastructure noise).

Distinguishing the case where HALT-as-deliverable applies vs. where the
straightforward fix-and-re-run is correct:

| Apply HALT-as-deliverable | Apply fix-and-re-run |
|---|---|
| The HALT reveals a structural inconsistency the audience would care about | The HALT reveals transient infrastructure (rate limit, flaky network) |
| The discipline's credibility is itself a load-bearing claim | The experiment's specific result is the load-bearing claim |
| The discipline catching the inconsistency is uncopyable / hard to fake | The catching is generic / commodity |
| The audience is field-skeptical (would be impressed by the discipline) | The audience is result-focused (would not engage with discipline meta) |
| Author has skin-in-the-game (their own work was caught) | Catching applies to someone else's work |

## Solution

When the HALT criteria match:

### 1. Commit the audit trail publicly before deciding the path forward

The HALT findings doc, the failed pre-registration, the pre-flight log — commit
all of these to public history immediately, before deciding whether to re-run.
This locks the catching in place; it cannot be retroactively papered over.

### 2. Resist the engineer reflex to quietly re-run

The engineer reflex is: "fix the inconsistency, re-run, ship the corrected
result." This is correct for routine engineering. It's WRONG when the
discipline-catching IS the demonstration. The corrected result is a number
or table; the HALT is a story.

### 3. Reframe the deliverable around the catching

If the original deliverable was "experiment produces result X showing claim
Y," the reframed deliverable is "the discipline pre-registered claim Y,
attempted the experiment, refused to proceed because Z was inconsistent,
caught Z, and here's the audit trail. The discipline of catching Z is the
demonstration of claim Y." Same evidence, sharper story.

### 4. Make the catching loud, not modest

The engineer reflex around HALTs is also to be quiet about them ("we had to
re-baseline; here's the corrected number; moving on"). The HALT-as-deliverable
move is the opposite: name the HALT in the title, document the audit trail
explicitly, narrate the discipline-catching-itself moment as the headline.
Modesty around HALTs hides the strongest available credibility signal.

### 5. Multiple HALTs compound

If a series of HALTs catches a series of different classes of inconsistency
(documentation drift, operational state, environment configuration), the
combined audit trail is dramatically more credible than a single HALT plus
multiple silent fixes. The compounded HALT pattern triangulates "what doing
this honestly looks like" — multiple failure-classes caught publicly.

### 6. The Sutherland angle (when applicable)

Behavioral-economics frame: numbers feel like product claims; stories feel
like character claims. Discipline-catching-itself is a character claim about
the work. In fields where the dominant pattern is "produce a confident number
even when you shouldn't," willingness to publicly halt before fabricating is
itself a status signal. Make it loud not because it's marketing but because
loudness IS the artifact at this point.

## Verification

A HALT-as-deliverable reframe is correctly applied when:

1. The HALT audit trail is committed to public history BEFORE the catching is
   reframed as a deliverable. Order matters; backdating breaks the audit
   integrity.
2. The reframed deliverable's headline names the HALT explicitly. "We caught
   X" is the lead, not buried.
3. A reader who comes for the original deliverable should be willing to
   substitute the HALT-as-deliverable shape on its own merits — not because
   they were told to.
4. The discipline that caught the HALT is itself recoverable from the audit
   trail (someone could implement the same discipline and would have caught
   the same class of error).

A reframe FAILS when:

1. The HALT is treated as marketing spin rather than substance — readers will
   notice and credibility loss is severe.
2. The original deliverable's claim was specific (a number, a comparison) and
   the substitute is vague (a vibes about discipline). The reframe doesn't
   work for narrow factual claims.
3. The audience explicitly came for the result, not the meta. Reframing to
   meta in front of result-focused audience reads as evasion.

## Example

**From Skill Harness project, T3 tracer round (2026-06-08):**

Original deliverable: an experiment showing that ai-slop-sentinel's
UNMEASURED result is subject-invariant — same result under Claude as under
GPT-5. Pre-registered byte-stable expected vector.

HALT 1 (PHASE B): pre-flight scorer-registry-drift check refused the GPT-5
run. The harness scorer registry had expanded between the dogfooding baseline
(committed in a session prior) and the v0.1.0 tag the case study cited. The
case study's "17 UNMEASURED at v0.1.0" claim was not reproducible at v0.1.0
because clause 0's axis now matched a new scorer added between baseline and
tag. Zero subject calls. $0.00 spent.

Engineer reflex: re-baseline at HEAD, quietly correct the case study, re-run
the experiment. Ship the corrected number.

HALT-as-deliverable reframe: the discipline caught the case study's own
author drifting between dogfooding and tag. The audit trail (pre-registration
commit + pre-flight HALT commit, both pushed to public history before any
subject call) IS the demonstration of "this is what honest evaluation looks
like." Same evidence, sharper story.

HALT 2 (PHASE B'): pre-flight environment check refused the re-baseline
run. Three compounding mismatches: ANTHROPIC_API_KEY absent (Claude Code
uses subscription auth), `--subject-model` CLI flag doesn't exist (the
adapter shipped at PHASE A.5 is unreachable from the CLI), pre-existing
evidence.db has incomplete runs that block aggregate. Zero subject calls.
$0.00 spent.

Two HALTs in a row caught two different classes of accidental falsification
(documentation drift + operational state inconsistency). The compound
story is dramatically more credible than either alone.

Disposition: HALT-as-deliverable reframe adopted. Both HALTs committed to
public history. Case study rewrite scope shifted from "report cross-vendor
result" to "narrate the discipline catching itself across multiple
failure classes." Three classes of accidental falsification surfaced (the
original Anthropic-key assumption that triggered the SOP precondition-check
gap counts as the third).

### Variant: micro-HALT on a stale planning document (2026-06-09)

The same pattern applies at much smaller scale. A handoff doc said "Workstream 1
is PENDING; propose a draft." Reading the doc against actual repo state surfaced
that the rewrite was already DONE at commit `a2c9fd9` — the handoff had been
authored BEFORE the commit landed and never updated.

The temptation: silently proceed to draft (the doc said to), accidentally
duplicate ~30 minutes of work already shipped, and produce a "rewrite" that's
just the existing content with minor variations.

The HALT-as-deliverable move: surface the catch explicitly ("the work you're
asking me to propose is already done at SHA X; the handoff doc is stale relative
to git"). Then offer the genuinely available forward paths (critique what's
there; propose further revisions; pivot to other workstreams; update the stale
doc).

The pattern generalizes from experimental HALTs (multi-hour pre-flight gates) to
documentation HALTs (sub-second state-drift catches). The trigger is the same:
the verification step found an inconsistency the casual reader would have missed.
The discipline of surfacing it (vs. silently working around it) is the
demonstration of "the verification step is doing real work, even on small things."

Author identity matters less for the micro case — but the discipline still
applies. A handoff doc claiming "DONE" when reality is "PENDING" gets the same
explicit-surface treatment as the inverse case here.

## Notes

- The pattern requires the discipline to be REAL — falsifiable, recoverable
  from audit trail, applied uniformly. Decorative pre-registrations or
  rubber-stamp pre-flight checks produce HALTs that don't generalize to
  "what doing this honestly looks like." The discipline has to actually
  catch real things, including the author's own mistakes.
- Author-of-discipline + author-of-deliverable identity match amplifies the
  pattern significantly. "The framework I built refused to validate my own
  shipped work" is uncopyable. "The framework caught someone else's work"
  is much weaker.
- This pattern is structurally adversarial to the engineer reflex of "fix
  problems quietly and ship the corrected result." It requires deliberate
  resistance to that reflex.
- The pattern fails fast if anyone perceives the HALT-as-deliverable framing
  as motivated reasoning. Mitigations: commit audit trail BEFORE making the
  reframe; make all the inputs to the catching publicly verifiable; resist
  the temptation to selectively report HALTs.

## See also

- `bayesian-eval-discipline` — pre-registration / peeking-immunization is the
  most common upstream discipline that produces HALT-as-deliverable opportunities
- `ai-slop-sentinel` — the self-review pattern that catches author's own slop;
  related upstream
- `fix-brief-consolidation-id-hygiene` (quarantine) — sibling discipline:
  catching orchestrator-level inconsistency in fix-brief consolidation; same
  failure-mode-becomes-feature pattern
- `mutation-equivalent-in-architecture` (quarantine) — sibling: honest
  re-classification (not silent re-classification) when discipline catches
  inconsistency in your own test architecture
