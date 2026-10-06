---
"mrbinnacle-skills": patch
---

Each card's `Dispatches recorded` row now counts the card under every name it has been invoked by (its name before the v2.0.0 rename and its plugin-prefixed form) and no longer counts the usage log's repeated lifetime baseline twice, so `decision-rights` reads 173 where it read 2 and `im-up` reads 260 where it read 361. The two hook-fired cards keep their note that the counter cannot see hook firings once their count is above zero.
