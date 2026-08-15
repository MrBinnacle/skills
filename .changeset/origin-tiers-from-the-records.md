---
"mrbinnacle-skills": patch
---

State the true origin tiering on the front page, and derive it from the cards.

`README.md` said seven of the nine cards exist because something went wrong, twice. Read on 2026-08-13, the nine `EVIDENCE.md` `Origin` fields say six. The ninth card is not in either bucket the page offered: `skill-necessity-gate`'s record calls it a codified research answer, stated plainly, not a scar. `7 + 2 = 9` closed the arithmetic while mis-describing that card — in the sentence explaining why evidence tiers are kept distinct.

Both passages now state the measured split, 6 `OBSERVED` / 2 `DESIGNED` / 1 `DISTILLED`, and name the third class rather than folding it into one of the other two. The `DESIGNED` vs `OBSERVED` distinction is unchanged; it was the count and the missing tier that were wrong.

`scripts/validate_scoreboard.py` now derives that tiering from the cards' own `Origin` fields and asserts both README sites, so adding, retiring or re-tiering a card turns the build red instead of leaving the page quietly stale. The vocabulary is closed — an Origin opening with an unrecognised word is refused, not guessed at — and a new poison-control fixture proves the check can fail for its own reason.
