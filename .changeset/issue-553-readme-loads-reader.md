---
"mrbinnacle-skills": patch
---

CI only. The README's Loads column check now reads each card's `disable-model-invocation` flag through the same frontmatter reader as the bucket README check, so the two pages are held to one reading of one fact. A failure now names each card that drifted and how, one line per card. Six planted controls show it going red: a cell flipped in either direction, a flag removed or added without the README, a row deleted, and a row repeated.
