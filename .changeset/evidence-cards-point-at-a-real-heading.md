---
"mrbinnacle-skills": patch
---

Every card's `EVIDENCE.md` now points at a heading that exists.

Each `EVIDENCE.md` opened with a provenance line directing the reader to the top-level README under the heading `"The receipts, explained"`. `README.md` has no such heading. The section that line describes is `## Evidence records`, at README.md:157, which defines the two evidence axes and their states.

Measured before the change: 15 tracked `EVIDENCE.md` files carried the dead pointer, 17 occurrences in total. That is all 14 published cards plus one quarantine card, `_quarantine/anti-slop-frontend-secure`. Two cards carry it twice — once in the header provenance line and once inline in an `Observed in use` row. After the change, zero occurrences remain.

The collection's bar for publication is that a visitor who opens a card and follows it finds something that supports what the card said. A pointer to a heading that does not exist fails that bar, and it failed on every published card at once. A reader checking what `UNMEASURED` or `OBSERVED IN USE` is supposed to mean arrived at the README and found no section by the name the card gave.

This change edits the quoted heading name and nothing else. No evidence field, verdict, count, date or claim is modified. `validate_card_files.py` continues to PASS across 14 published cards with its allowlisted breaches unchanged, and `validate_scoreboard.py` continues to derive 14 admitted, 1 measured, 2 retired.

The defect was found by following each card's evidence pointer to its destination, the way a stranger would, rather than by reading the cards alone. A cross-family review seat reading a separate description of the collection named the same repair independently.
