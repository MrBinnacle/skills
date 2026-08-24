---
"mrbinnacle-skills": patch
---

Every published card now ships a structural eval corpus, and CI refuses a card that does not (#124).

A card states behavioural claims and records evidence for them. Nothing stated what a run against a card should ASSERT, so there was nothing to run a card against later and nothing that went red when a card's frontmatter `name` drifted from what its evidence refers to. Verified 2026-08-24 at `73a779c`: `git ls-files | grep -i evals` returned nothing.

Each card now carries exactly one `evals/evals.json`: a `skill_name` equal to the card's live frontmatter `name`, at least three cases, unique integer ids, unique realistic prompts, non-empty expected outputs, and at least two falsifiable assertions per case. Thirty cases across nine cards.

**These files are contracts, not measurements.** A corpus describes what a run should assert. It records no run, no score and no verdict, and its presence is not evidence of anything about a card's worth. Every card's `Screen result` and `Paired verdict` are unchanged and still `UNMEASURED`; the diff touches no `EVIDENCE.md`. `scripts/validate_eval_corpora.py` never reads or writes an evidence record, because a checker that could touch a verdict is a checker that could manufacture one. Executing a corpus, and anything that would move a verdict, belongs to the measurement instrument and is not in this change.

The corpus semantics live in a new script rather than in `scripts/validate_skill_formats.py`. That gate has one subject — the closed readable-format vocabulary `SECURITY.md` commits to — and `.json` was already in it, so a corpus is admissible there as-is (confirmed by running the gate: 114 guarded files across 41 skill folders, all declared formats). Widening a security check to carry a second, unrelated meaning is how a security check stops being readable in one sitting.

Discovery is `validate_card_files.find_cards`, imported rather than restated, so the checker's "N published card(s)" and the card-file gate's are one number. That keeps the fixture trees under `scripts/fixtures/` out of scope: they are inputs to other validators, they sit outside `<root>/skills/`, and requiring a corpus of them would turn every one of them red for a file they do not owe. A tree with zero published cards is refused rather than reported green.

`scripts/test_validate_eval_corpora.py` runs the real entrypoint against fourteen temporary trees plus the live one. Each rejection tree is a single mutation of one conforming baseline, and each rejection asserts both a substring of its own failure message and a breach count of exactly one — a fixture that is red for two reasons would stay red if the check under test were deleted. Covered: missing corpus, invalid JSON, frontmatter-name mismatch, fewer than three cases, duplicate identifier, duplicate prompt, empty prompt, prompt under the length floor, empty expected output, too few assertions, empty assertion, a second file beside the corpus, and a tree with no cards. Going green is proven by the baseline and by the live tree, whose corpus count is asserted equal to its card count rather than to a number written in the suite.

The suite, the checker and one poison control — a published card that ships no corpus — run in the existing `tests` workflow on both operating-system cells. No second workflow. Output is ASCII-only, and corpus text is quoted through `ascii()` rather than `repr()`, so a non-ASCII byte inside a corpus is reported rather than raised at a cp1252 console.
