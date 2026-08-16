---
"mrbinnacle-skills": patch
---

CI refuses a published card that is missing one of the three card contract files.

`AGENTS.md` states the contract — a card ships `SKILL.md`, `gotchas.md` and `EVIDENCE.md` — and until now nothing checked the first two. `scripts/validate_card_files.py` is the check behind that sentence, run in the `linkcheck` lane on every PR. It reports the bucket-qualified card and the missing filename, not a bare directory name, so the line names a file a maintainer can open. Presence only: what an `EVIDENCE.md` must say row by row stays `validate_conformance.py`'s O4.

A checker that inspects nothing must not print a pass, so a tree with no cards under `skills/` is refused rather than reported green — the path-bug failure that would otherwise read as conformance.

Cards are discovered by directory rather than by the `SKILL.md` marker, deliberately wider than `validate_conformance.py`'s glob: a checker that finds cards *by* `SKILL.md` can never report the one card whose missing file is `SKILL.md`. What the wider walk costs is that every directory two levels under `skills/` gets claimed as published, so the unshipped buckets `AGENTS.md` sanctions for parking work in progress, and dot-directories, are excluded using `validate_scoreboard.py`'s own frozenset rather than a second copy of the rule. Without that, parking a half-built card in `in-progress/` — the repo's own instruction — turned the lane red for three files a card that is not published does not owe, and the run claimed three published cards where the front page states one.

`scripts/test_validate_card_files.py` runs the real entrypoint against real trees: the committed `card-missing-gotchas` poison fixture, which must fail and must name the card and the file; a tree with zero cards; a tree whose only unfinished work sits in `in-progress/` and a dot-bucket, which must pass and must count neither; and the live nine cards, which must pass. It also asserts the workflow lane still invokes both scripts, since a checker no job runs is a checker that never fails.
