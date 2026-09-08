---
"mrbinnacle-skills": patch
---

`README.md` now states what an install actually writes. Three claims on the page were false, and a cold-install run measured each one.

**"Both install routes copy Markdown files onto your machine. There is nothing to import and no framework to run."** A clean-environment run of `npx skills add MrBinnacle/skills` installs 88 files under `.claude/skills/`, of which 23 are not Markdown and 7 are Python: `close_session.py`, `snapshot_state.py`, `validate_packet.py` and `test_validate_packet.py` under `im-down`, and `open_session.py`, `validate_packet.py` and `test_validate_packet.py` under `im-up`. Those scripts are the ones the two session-boundary cards instruct a reader to run. The sentence told a stranger the install was inert Markdown. The page now names the `evals/evals.json` every card carries and the scripts those two cards carry, and says plainly that nothing runs until the reader runs it.

**"`npx skills add` copies cards into `.claude/skills/` under the directory you run it in."** The same run wrote three things, not one: `.claude/skills/`, a second full copy of every card in `.agents/skills/`, and a `skills-lock.json` recording each card's source path and a hash. Two of the three were undocumented. The page now names all three and states that the two card directories are the installer's convention rather than this collection's choice.

**"Each card directory contains: SKILL.md, gotchas.md, EVIDENCE.md."** All 14 cards carry a fourth tracked file, `evals/evals.json`, and 46 tracked files across the collection sit outside the documented three. `im-down` carries 15 files and `im-up` 14. The page now lists four required files and says cards may carry more.

The `--global` claim is unchanged and remains unmeasured here. Replaying it would write into the operator's own home directory, so the run recorded it as refused by the destructive-action gate rather than executing it.

The measurement is repeatable. `scripts/stranger_test.py` in the private steering repository builds a scrubbed environment with no API keys, runs every command the README documents, and checks what the install left on disk against what the page promises. It refuses before running anything if a documented command has no step covering it, so a command added to the page later cannot escape the test in silence. Its install-footprint check now pins the corrected sentences: a card that ships an undocumented executable, an installer that writes a fourth artifact, or a card missing one of the four required files each turn it red. Four negative controls were run against seeded violations, and each produced the failure it was written to produce.
