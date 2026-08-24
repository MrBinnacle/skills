---
"mrbinnacle-skills": minor
---

The 200-character description bar is now a check, because three cards shipped over it the day it was left to a step.

`AGENTS.md` step 2a has required a published description of 200 characters or fewer since the collection began, and that step was the only thing enforcing it — the file said so in its own words: *the edit is the enforcement*. On 2026-08-24 six candidates were promoted and **three shipped over the bar, at 210, 226 and 235 characters**, because the promotion pass never ran the authoring skill whose job that is.

**This is the collection's own layer-placement rule failing on the collection.** A discipline that must fire cannot live only in a step a human or a model has to remember. The fix is not a better-worded step; it is a gate.

`validate_card_files.py` now refuses a published card whose description is absent or over the bar, and its `PASS` line says so. **Verified against the real tree at the commit where those three shipped: the check names all three cards and states each measured length.** That is a historical defect caught, not a fixture.

The three descriptions are rewritten to 192, 182 and 195 characters. Each keeps every distinct trigger branch it had; what came out was restatement, not coverage.

**Why 200 rather than the specification's 1024.** An installed card's `description` is loaded at startup whether or not the card ever fires, so its length is paid for by every session in every project that installs the collection. The specification bounds what a reader can parse. This bounds what a user pays. All three breaches were comfortably inside 1024, which is exactly why the spec gate adopted in the previous change did not catch them — the two checks answer different questions and both are needed.

**Surrounding quotes do not count against the budget.** Quoting is a YAML requirement — two published cards need it because their descriptions contain a colon — and a syntax obligation must not cost a card two characters of what it can say.

**The fixtures were not modelling the artifact they grade.** Every fixture card in the suite wrote a `SKILL.md` of `# name` with no frontmatter at all, so none of them resembled a published card and all eleven broke the moment a frontmatter check existed. They now carry real frontmatter. A fixture that cannot represent the failure being introduced is a fixture that was only ever testing the checks it already had.

Four cases pin the new bar: over is red and the report states the measured length; exactly 200 is green, because a check that cannot go green either way is as useless as one that cannot go red; quotes are not counted; an absent description is refused.

**What is still not checked, stated plainly so it is not mistaken for solved.** Nothing reads a description as a *router*. A well-formed 200-character description that names none of the words a user actually types passes every gate in this repository cleanly. Length is now deterministic; wording is not, and wording is what decides whether a model-invocable card is ever reached.

*Revisit if:* the startup cost of a description changes — the bar is derived from what a user pays per session, not from a style preference.
