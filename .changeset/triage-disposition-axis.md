---
"mrbinnacle-skills": patch
---

The triage vocabulary in `docs/agents/triage-labels.md` now declares two axes instead of one flat list. The role axis says who acts next and is unchanged in content. The disposition axis says what was decided and holds `declined`, `subsumed`, `cant-tell-yet` and `wontfix`. An issue carrying a disposition carries no role, because a decided issue has no next actor.

`wontfix` moved from the role table to the disposition table. The label is unchanged and every issue carrying it keeps it. What changed is which question it answers: it was always a decision wearing a role's clothes, and four of the five values around it answered a different question.

`declined`, `subsumed` and `cant-tell-yet` are non-terminal and each requires a row in the revisit-conditions registry naming what would reverse the decision. `wontfix` is terminal, is watched by nothing, and requires no row. That difference is the reason the axis exists: without it, `declined` becomes a second `wontfix` and the reversal condition goes unwritten.

The disposition values are borrowed from the measurement instrument's ratified verdict enum rather than invented, so the board reads in the same terms as the instrument that judges the work.
