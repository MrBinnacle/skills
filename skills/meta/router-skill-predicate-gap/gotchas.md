# gotchas — router-skill-predicate-gap (append-only)

- [OBSERVED 2026-08-18] Origin incident, recorded in `SKILL.md` → Example. A rule file marked
  `downstream-instruction-framing` as router-enforced and MANDATORY before any handoff, plan,
  ADR, or subagent prompt. The bare word `plan` was absent from the pattern list. The skill had
  fired earlier in that session only because the work also involved an ADR, so `\bADR\b`
  matched and the correct behaviour was coincidence relative to the rule's stated purpose.
  Found by piping a prompt into the live hook, not by reading the rule file.

- [OBSERVED 2026-08-23] Second occurrence, and it refutes this card's own stated remedy.

  **What happened.** A router rule shipped 2026-08-22 for a maintenance-pass skill, with four
  patterns and three asserting fixtures. The next day the maintainer typed
  `"Skills needs some TLC"`. The router stayed silent. Two independent defects, found by
  probing the live hook:

  1. The pattern list covered `could use some tlc` and did not cover `needs`. That is this
     card's original failure mode, reproduced exactly: the predicate matched specialist
     phrasing and missed the ordinary request.
  2. `patterns[0]` — the broadest of the four, and the only one written to catch general
     hygiene phrasings — held a literal backspace character where a regex word boundary was
     intended. **In JSON, `\b` IS the backspace escape.** A word boundary inside a JSON string
     literal must be written `\\b`. The damaged pattern compiled without error and matched
     nothing, from the moment it shipped.

  **The finding, and why it matters more than the tally.** This card's Notes say: *"A router
  rule deserves a test suite. A test suite is what catches a predicate gap; a reading is
  not."* This rule **had** a test suite. That suite is stricter than this card asks for — it
  refuses to accept any rule that carries no asserting fixture, and it rejected the rule on
  first commit until fixtures existed. It still certified an inert primary predicate, because
  its coverage check is **per-rule, not per-pattern**: all three fixtures happened to be
  matched by the three narrower patterns, so the rule passed while its broadest pattern was
  dead. A per-rule green is compatible with any number of dead patterns.

  Measured on that install the same day: **33 of 72 patterns across 10 rules were reachable by
  no fixture at all.** Any of the other 38 could be inert in the same way, and nothing would
  report it.

  The remedy in Notes is necessary and not sufficient. `SKILL.md` § 2 and § Notes carry the
  three additions this produced; they are stated there once and not repeated here.

- [OBSERVED 2026-08-23] The procedure in `SKILL.md` § "Test the negative first" was unsafe as
  written, and it misled a session within minutes of being followed. It said: *"Empty output
  means it did not fire. Record that, verbatim, as the finding."* Empty output also means the
  interpreter errored. A probe run against a wrong filename printed nothing for six prompts,
  including two known-good fixtures, and was read as total router failure.

  The general rule now lives on `success-test-accepts-any-output` → rule 4, which is the card
  whose subject this is; § 1 here points at it rather than restating it. Recorded on both
  because the occurrence belongs to both: this card's procedure caused it, that card's
  mechanism explains it.
