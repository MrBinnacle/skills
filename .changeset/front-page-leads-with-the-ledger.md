---
"mrbinnacle-skills": patch
---

The front page leads with the admission method, and a check holds its per-card census to the
cards.

A visitor now reads three things before anything else: what governs membership (`ADMISSION.md`,
with its three-instrument table — policy / gate card / screen — cited rather than restated), a
card map by type, and a per-card table stating each card's evidence posture and its counted
occasions. The 2026-08-15 S295 disposition record is linked at the top, where a reader can see
the triage's verdicts: two cards stand, six carry thin recurrence records, one is ceiling-likely.
`ADMISSION.md` is unchanged.

`scripts/test_readme_admission_lead.py` is the check behind that table. It runs in the
`validator` job on every pull request — a table nothing checks is a table that drifts, and this
one restates nine cards' records on the page furthest from them.

The census is **derived through the existing validators, not restated**:
`validate_scoreboard.evidence_fields` parses the rows, its closed verdict vocabulary decides
`measured`, `validate_card_files.COUNT_RE` reads the occasions integer, and
`validate_scoreboard.iter_skill_dirs` decides which cards are published. The first draft of this
suite carried its own parser and its own open "anything that is not UNMEASURED" test, and all
four rules disagreed with the validators on real trees: an `UNMEASURED` field that merely
mentions `SKILL.md` read as a measured result, a `KEEP` verdict written without a trailing period
read as no result, fenced example rows became a card's values, and parking unshipped work in
`in-progress/` — which `AGENTS.md` sanctions — demanded a front-page row for a card that was
never admitted. Two of those four errors put a measurement on the page that never happened, which
is the direction that flatters it.

Two claims elsewhere were left contradicting the new table and are corrected here rather than
left standing:

- `README.md`'s controlled-results bullet still said every controlled field reads `UNMEASURED`.
  That went false on 2026-07-21, when `git-pull-rebase-trap`'s screen returned `CANT_TELL_YET`.
  The bullet now states the one screen that ran and the eight cards that read `UNMEASURED`, which
  is what the banner's `1 measured` has said since the record was corrected. An identical
  universal claim was removed from a neighbouring paragraph in #42 and this site was missed.
- `BRAND.md` quoted "the README's own words" for a sentence this restructure deletes. The quote
  now points at a sentence the page still carries. `BRAND.md` states that the shipped files
  outrank it, so it follows the front page rather than pinning it.
