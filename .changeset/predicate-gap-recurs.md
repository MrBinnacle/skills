---
"mrbinnacle-skills": patch
---

Record a second occurrence of the router predicate gap, and correct the candidate card that a per-rule test suite is enough to catch one.

`_quarantine/router-skill-predicate-gap` gains a `gotchas.md` and two corrections to `SKILL.md`.

On 2026-08-23 a router rule shipped the previous day stayed silent on the maintainer's plain-language request. Probing the live hook found two defects. The pattern list covered the phrase "could use" and not "needs" — this card's original failure mode, reproduced. And `patterns[0]`, the broadest of the rule's four, held a literal backspace character where a regex word boundary was meant: in a JSON string, `\b` is the backspace escape and a word boundary must be written `\\b`. That pattern compiled cleanly and matched nothing from the moment it shipped.

The rule had a test suite, and that suite was stricter than this card asks for — it refuses any rule carrying no asserting fixture, and it rejected the rule on first commit until fixtures existed. It certified the inert pattern anyway, because its coverage check is per-rule: all three fixtures were matched by the three narrower patterns, so the rule passed green while its broadest pattern was dead. Measured on that install the same day: 33 of 72 patterns across 10 rules were reachable by no fixture at all.

The card's Notes claimed a test suite is what catches a predicate gap. That is still necessary and it is not sufficient. The Notes now say so, and name the two additions that close the gap: count coverage per pattern rather than per rule, and give every deliberately-broad pattern a fixture only that pattern can satisfy.

`SKILL.md` § "Test the negative first" also carried an unsafe instruction — "Empty output means it did not fire. Record that, verbatim, as the finding." Empty output is equally what a crashed interpreter prints. A probe run that invoked a wrong filename reported SILENT for six prompts, two of them known-good fixtures, and was one step from being recorded as total predicate failure. The procedure now requires a known-good fixture as a positive control in the same run, and adds a check for control characters in the pattern list, which `re.compile()` cannot detect.

This is quarantine evidence. The card is not promoted here; admission stays default-refuse and is the maintainer's call.
