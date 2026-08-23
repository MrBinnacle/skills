---
"mrbinnacle-skills": patch
---

The front page is replaced with the owner's greenfield draft, and the checked structure is
carried across rather than dropped.

The page now reads: banner, the ruled line, a two-sentence statement of what the collection is,
then the checked admission lead (admission method, card map, per-card evidence census), then the
owner's account — where the cards came from, the four problem areas they address, the provenance
and evidence vocabularies, how a skill leaves, what the collection is not, the evaluation work,
and why a skill score is not a skill effect. It drops from 28,584 bytes to 11,221.

Four checks constrain the front page, and all four still hold. `scripts/validate_scoreboard.py`
requires the ruled banner line inside the `<img alt>` and requires the origin tiering — 6
`OBSERVED`, 2 `DESIGNED`, 1 `DISTILLED` — stated on a single line in two sections; the draft
carried the tiering as a three-item bullet list, which matches on neither line, so it is restated
as one line in "Where these came from" and once more under "Provenance".
`scripts/test_readme_admission_lead.py` requires admission method, card map, and card evidence to
be the first three `##` sections and requires the per-card table to project each card's own
`EVIDENCE.md`; those three sections are copied from the previous page unchanged rather than
rewritten, so no new prose enters the page in the owner's voice.

The draft linked `docs/why-skill-scores-mislead.md`, which does not exist in this repository. The
link now points at
[`why-naive-skill-benchmarks-mislead.md`](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/why-naive-skill-benchmarks-mislead.md)
in `skill-harness`, which is the target the previous page used for the same claim. `RETIRED.md`
is named in the draft without a path and is now a link.

`BRAND.md` quoted the front page's own words for a sentence this rewrite deletes — *"It is not
proof that these nine work."* It now quotes *"Publication is not validation."*, which the page
still carries. `BRAND.md` states that the shipped files outrank it, so it follows the front page
rather than pinning it.

**What this rewrite removes, stated plainly because a reader loses it.** The page no longer
carries the install instructions (`npx skills add MrBinnacle/skills` and the by-hand `git clone`
recipe), the "Is it safe to install these?" section, the nine per-card descriptions, the
contributing summary, the author attribution, or the licence line. Issue #64 user stories 18 and
19 protect the install instructions, the safety section, and the per-card descriptions. The draft
does not contain them and they were not re-added, because adding them back would widen the draft
the owner wrote. Restoring any of them is a one-commit follow-up.
