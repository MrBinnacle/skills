---
"mrbinnacle-skills": patch
---

The rotation-and-harvest procedure now describes the gates that actually run.

`AGENTS.md` § "The rotation and harvest pass" is written so a cold session can execute the whole pass from this repository. Between 2026-08-23 and 2026-08-24 the repository grew three validators, a third contract row on every published `EVIDENCE.md`, a second direction on the occasions check, and an eight-file parity contract on the session-boundary pair. The procedure recorded none of them. It still said "four validators", still named two contract rows, still listed a five-item gate set, and still described the occasions check in one direction. Nothing in CI reads prose, so all four drifts were invisible and none was self-detected.

The consequence was specific, not cosmetic. A cold session running the pass as written would have shipped a pull request that CI reds on three gates the procedure never told it to run, and a promotion authored against the procedure would have been missing the `Dispatches recorded` row that `validate_card_files.py` requires.

Four corrections, each verified against the code rather than against the prose it replaces:

- **Contract rows: two to three.** `Dispatches recorded` is in `REQUIRED_EVIDENCE_ROWS`. Its checked form is stated — a positive integer or the exact phrase `No recorded dispatch`, plus a `measured <date>` clause — together with why a numeral zero is refused: two cards fire through hook mechanisms the platform counter cannot observe, and a figure the counter cannot see must not be published as "unused". The section now also states plainly that a dispatch is not an occasion.
- **The occasions check runs in both directions.** "Recording a new occurrence" described only the rule that stops a count rising without a record. It now also states the rule that stops a record sitting uncounted, the term-of-art trigger that scopes it, the `co-occurrences` exclusion, and the instruction to reword a non-occurrence line rather than cite its date to silence the check.
- **The gate set is a table of all seven validators and all seven suites**, each with the change a pass most often breaks in it, and it carries the command that re-derives the list from the workflow files. The instruction is to run all seven rather than the ones the pass believes it touched, on the same reasoning the reconciliation step already gives for walking the consequence chain. The parity contract is stated with its failure mode: the suite reports parity NOT VERIFIED and still exits 0, so CI greps the roster for `, no-drift` and a reader must do the same.
- **Step 2's validator count is corrected, and its load-bearing claim is sharpened rather than dropped.** One validator now parses frontmatter, but only the `name` key, and only to catch a corpus whose `skill_name` drifted. No validator reads a card's `description`. The count rising from four to seven is exactly the change that invites a reader to assume the gates have grown to cover retrieval; the text now says they have not.

Step 7 no longer fixes who presses merge, which is the maintainer's to hold or delegate and was stated as neither. It fixes the gates, which hold either way: CI green, and the PR head SHA matching the branch ref — with the incident that makes the second gate load-bearing, where a PR merged mid-push froze its head while `gh pr checks` reported green for the older SHA. Publication is named as a separate authority that does not move: release tags, published assets, the social preview, the About settings.

*Revisit if:* a validator is added or removed. The table dates itself the moment the roster changes, which is why the command that re-derives it sits beside it.
