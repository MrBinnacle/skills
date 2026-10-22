---
"mrbinnacle-skills": patch
---

Release gate G10 now prices a card change that no changeset bump covers. A branch whose added changesets are all empty, or that adds none, is refused when its diff renames, admits, retires or changes the load mode of a card, or changes the install route, because each of those is priced above patch by ADR 0003, ADR 0005 or ADR 0008. An empty changeset for a change priced at patch, or for work that reaches no card, still passes. At release, a rename, admission, retirement, load-mode change or route change inside the release pull request raises the required version bump to its ADR price, and an unreadable ADR 0008 refuses the release instead of pricing it as patch. Installed users need do nothing.
