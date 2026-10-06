# gotchas — dead-predicate (append-only)

- [OBSERVED 2026-08-18] Origin incident, recorded in `SKILL.md` → Example. A rule file marked
  `decision-rights` as router-enforced and MANDATORY before any handoff, plan,
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

  The general rule now lives on `vacuous-check` → rule 4, which is the card
  whose subject this is; § 1 here points at it rather than restating it. Recorded on both
  because the occurrence belongs to both: this card's procedure caused it, that card's
  mechanism explains it.

- [OBSERVED 2026-09-01] Occurrence, branch 3 (shadowing). A session added a router rule whose
  patterns overlapped an existing rule earlier in the file. That router's match loop stops at
  the first hit, so every prompt the new rule was written for went to the earlier rule, and
  the new rule would have been inert from the day it shipped. The router's self-test caught
  it before commit, together with `\b` escapes that had become literal backspace characters.
  The next session's brief then carried the rule as a constraint: scope new patterns clear of
  every earlier rule, because an overlapping pattern is dead on arrival.

- [OBSERVED 2026-09-13] Occurrence, branch 5 (wrong claim, complete predicate). An advisory
  hook rule warned that passing `name` to the Agent tool defers the agent's report, and that
  a foreground setting does not override it. Its pattern was `"name"\s*:`. Measured that day,
  twice: a named foreground agent returned its report inline. The deferral comes from
  backgrounding, which is the default. The rule fired on every dispatch that named an agent,
  so it was complete against its own pattern, and it never fired on the case that refutes it:
  an unnamed dispatch that is backgrounded anyway. It stood for eleven sessions with a green
  self-test, because the fixture was written from the pattern. The repair widened the pattern
  to `"(name|run_in_background)"\s*:`; narrowing it back reddened exactly the new assertion.
  Predicate completeness is measured against usage; claim alignment is measured against the
  counter-example. A rule can hold one and not the other.

- [OBSERVED 2026-09-20] Occurrence, branch 4 (stale name). A sweep of one install's router
  found four rules whose skill names no longer resolved. Three skills had been renamed when
  they were promoted into published plugins, and the router kept the old names. The sharpest
  was the rule marked MANDATORY before any handoff, plan, ADR or subagent prompt: its skill
  had been invoked 144 times under the old name and was unreachable under it after the
  rename. A session six days earlier had already seen that the old name was not installed
  while its router entry stayed live. The fourth was an uninstall: a maintenance command
  disabled a skill as unused and left its router rule behind. The fix added a check that
  fails on any rule naming a skill that cannot resolve.

- [OBSERVED 2026-10-05] Fold-in for branch 2, recorded so the count stays honest. The
  maintainer's research repo records the JSON `\b` defect in six sessions, S312 to S487,
  across several surfaces: router patterns, signature generators and other JSON writers.
  Each fix was scoped to the one surface where it was caught. The last control written
  against it scanned bytes, and reported clean on a file that held the defect, because a
  JSON writer stores the backspace as the two characters `\b`. The working control decodes
  the JSON and inspects the values; `probes.md` step 2 does that. Not counted again for this
  card: most of the six were not router rules, and the two that were are already counted
  above, in the 2026-08-23 and 2026-09-01 entries.

- [NOTE 2026-10-06] The 2026-08-23 entry says `SKILL.md` § 2 carries the control-character
  check. That script now lives in `probes.md` step 2, reached from `SKILL.md` § Solution.
