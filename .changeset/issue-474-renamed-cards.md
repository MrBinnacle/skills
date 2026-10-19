---
"mrbinnacle-skills": patch
---

`RETIRED.md` gains a `Renamed in 2.0.0` section. It maps each of the eleven names the v2.0.0 rename replaced to its current card, with a link to that card. skills.sh still lists the old names, and an install command that uses one finds no skill, so a reader who searches the repository for an old name now finds the current card. The release procedure in `AGENTS.md` gains a manual step: after a release merges, compare the skills.sh listing with the card directory names and record any stale name. `scripts/test_renamed_cards.py` reads the rename table from the v2.0.0 entry in `CHANGELOG.md`, requires `RETIRED.md` to map every old name to the same current name, requires each current name to be a published card directory, and requires the release step to name the listing URL. It makes no network call. This is a patch: no card, name, file or install route changes.
