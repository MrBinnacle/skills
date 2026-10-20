---
"mrbinnacle-skills": major
---

Every published card's `EVIDENCE.md` gains an `| **Applicability scope** | ... |` row, written by the card's author in the form `For: <situations>. Not established for: <situations>.` Each row is written from the card's `description`, its gotchas and its origin, and names no situation the description does not route to. CI refuses a published card whose row is missing, does not open with `For:`, has no `Not established for:` part, or leaves either part empty. Both labels are case-sensitive, and the check reads only the form, never the wording. Quarantine cards and `scripts/fixtures/` are exempt. The promotion steps in `AGENTS.md` now name both scope rows, and promotion step 2 gains a review line: the `description` makes no claim wider than the evidence scope. Review checks that line, not a gate, because no validator reads description wording.

This is a major, under ADR 0002 (`docs/adr/0002-a-release-is-a-delivery-event.md`): "Changing the install path, or the on-disk shape of a card, is a major change." A new required row changes the on-disk shape of every card's `EVIDENCE.md`, which is the case skills#353 priced as major. ADR 0005 does not reprice it. Its text says it amends ADR 0002 "on one clause: what counts as a change to the install path", and it leaves the card-format clause untouched.

Action for installed users: None. Every card keeps its name, directory and files, and an installed user changes nothing to keep using them. A card author who adds a card or promotes one from quarantine must now write an `Applicability scope` row.
