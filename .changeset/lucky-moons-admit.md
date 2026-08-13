---
"mrbinnacle-skills": patch
---

Swap the front-page inventory line to what the repository can support: `9 admitted / 0 measured /
1 retired / 4 solutions looking for a problem`. `kept` asserted a retention decision that survived
an evaluation, and no evaluation has happened — so the page that refuses to state numbers its
evidence will not carry was carrying one.

`0 measured` is a new derived field. `scripts/validate_scoreboard.py` reads it from each card's
own `EVIDENCE.md` controlled fields rather than hard-coding a zero, so it goes red the day a card
is first screened instead of quietly staying wrong. A card with no record, or with a controlled
field missing, is refused rather than counted as unmeasured. A third poison control proves the
field can fail.
