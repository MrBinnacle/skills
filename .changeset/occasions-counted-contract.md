---
"mrbinnacle-skills": patch
---

The recurrence rows are contract, and CI refuses a card that does not state them.

Every published card's `EVIDENCE.md` now carries `Occasions counted` — an integer plus the dated references behind it — alongside the `Re-screen trigger` row it already had, and `scripts/validate_card_files.py` refuses a published card missing either. The row answers `ADMISSION.md` criterion 2 in the card's own file: the S295 admission triage found that the systemic gap was never a shortage of incidents but that recurrence is recorded once and never counted.

The count cannot certify itself. The opening integer must equal the number of dated references in the row, and every one of those dates must appear elsewhere in the card's own files — a gotchas entry, a case study, a SKILL.md verification section. A count checked only against the dates sitting beside it would pass any number a card cared to write next to any dates it cared to invent.

Seven cards state `RECURRENCE-THIN` in their own record, and the checker requires the label below two counted occasions and refuses it at or above two, in both directions: an absent label understates what the evidence is worth, and a stale one understates a card that earned its way out. `parallel-review-disposition-schema` (2 counted) and `subagent-research-reliability` (4) carry no label. `git-pull-rebase-trap` carries the label and keeps the triage's own `CEILING-LIKELY` verdict beside it — that verdict is the measurement axis and does not dispute the count.

`AGENTS.md` states how a new occurrence is recorded — dated entry first, then the count — so recurrence accrues without a special counting session, and states that dated disposition records are snapshots rather than files to be rewritten later.

The row checks live in `validate_card_files.py`, not in `validate_conformance.py`'s O4, and the earlier note saying otherwise is corrected in place. O4's subject is the CONTROLLED fields the front-page scoreboard is derived from, under `conformance v1`, whose own bump rule makes a material change to what counts as meeting an obligation a version bump — with a pre-registered payload for the first one. These rows are the admission contract, not the scoreboard's. The row table itself is parsed by `validate_scoreboard.evidence_fields`, imported rather than restated, so the fenced-block and first-occurrence-wins rules are not implemented twice with different answers.

`scripts/test_validate_card_files.py` runs the real entrypoint against real trees: a committed `card-missing-evidence-row` fixture that ships all three files and states one row too few — the case that would silently stop being checked if the checker only looked at file presence — plus an inflated count, a dated reference nothing corroborates, a missing label, a stale label, and each of them corrected so the check is shown to go green as well as red. The committed `card-missing-gotchas` fixture now states both rows, so it stays red for exactly one reason, and both fixtures assert that breach count.
