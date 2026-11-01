---
"mrbinnacle-skills": patch
---

Release gate G10 now refuses a minor or major bump on a branch whose diff changes only the `EVIDENCE.md` files of cards and no install-route name. ADR 0002 prices a correction within a card as a patch, so such a bump overprices the release. An edit to any other card file is not capped, because a change to a card's shape can be major. Installed users need do nothing.
