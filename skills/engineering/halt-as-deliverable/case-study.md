# Case study - HALT as deliverable

The dated instances behind [`SKILL.md`](SKILL.md). Each records what the gate refused, what the engineer reflex
would have shipped instead, and what was published.

**From the measurement harness upstream of this collection, T3 tracer round (2026-06-08):**

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

