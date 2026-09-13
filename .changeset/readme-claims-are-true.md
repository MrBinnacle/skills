---
"mrbinnacle-skills": patch
---

The front page states four things about itself that were not true, and they are corrected against the source in each case.

Three of them turned on one verb. `README.md` said CI "rebuilds" the card evidence table from the cards, and later that CI "derives" it from the records on every run. No generator exists. `scripts/validate_scoreboard.py` says so in its own docstring: "A test, not a generator: banners and the README alt stay hand-edited; this script only refuses drift." Hand-written and machine-checked is a real guarantee and the page is entitled to claim it. Rebuilt-by-CI is a stronger one and nothing implements it. All three sites now say the table is checked against the records and that the check fails on any disagreement, and the paragraph names the script and states that it never writes the file.

The fourth was the install description, which is the one instruction on the page a visitor executes. It promised "a copy of every card in `.claude/skills/`, a second copy in `.agents/skills/`". Running `npx skills add MrBinnacle/skills` in a clean directory produces one real copy of each card in `.agents/skills/` and a symbolic link to each of those in `.claude/skills/`, with absolute targets. Both halves of the sentence were wrong. The page now describes what the installer does, attributes the behaviour to the installer rather than to this collection, and states the Windows consequence: the links need Developer Mode or an elevated shell, and tooling that does not follow symbolic links should read `.agents/skills/` directly.

One further correction is about impression rather than fact. The page said the 2026-08-15 admission triage "retired none of them", which is true and leaves the reverse impression on a page whose whole argument is that it does not do that. The record's own text says retirement was never that pass's job, and reports the finding the earlier sentence omitted: of 57 cards surveyed, 7 passed all four admission criteria on recorded evidence, and the systemic gap was criterion 2, recurrence counted independently. The page now carries the finding.

Found by a cold-reader pass and an independent slop audit of the shipped page, both of which flagged the "rebuilds" verb as the most serious defect on a page whose pitch is that its numbers are derived rather than asserted.
