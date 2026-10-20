---
"mrbinnacle-skills": patch
---

Every published card's `EVIDENCE.md` gains an `| **Applicability scope** | ... |` row, written by the card's author in the form `For: <situations>. Not established for: <situations>.` Each row is written from the card's `description`, its gotchas and its origin, and names no situation the description does not route to. CI refuses a published card whose row is missing, does not open with `For:`, has no `Not established for:` part, or leaves either part empty. Both labels are case-sensitive, and the check reads only the form, never the wording. Quarantine cards and `scripts/fixtures/` are exempt. The promotion steps in `AGENTS.md` now name both scope rows, and promotion step 2 gains a review line: the `description` makes no claim wider than the evidence scope. Review checks that line, not a gate, because no validator reads description wording.

This is a patch. ADR 0005 (`docs/adr/0005-the-install-route-is-what-a-consumer-resolves.md`) states the rule: "A change is major only when an installed user who takes no action loses something they had, or must act to keep it." An installed user takes no action and loses nothing, and merged #354 shipped an equivalent required `EVIDENCE.md` row as a patch.

Action for installed users: None. Every card keeps its name, directory and files, and an installed user changes nothing to keep using them. A card author who adds a card or promotes one from quarantine must now write an `Applicability scope` row.
