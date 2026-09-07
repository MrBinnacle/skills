---
"mrbinnacle-skills": patch
---

One word list now binds every line of prose this repository publishes. `assets/tokens.json > copy.words_to_avoid_surfaces` gains a `markdown_prose` surface over every tracked `.md` except `_quarantine/**`, whose candidates are frozen, and `CHANGELOG.md`, whose entries record what shipped under the wording in force at the time. `scripts/validate_brand_kit.py` reads that surface, and the fixture that used to assert body prose passed with a listed word is inverted into a poison control that goes red when it does. Twenty-five lines were rewritten, each to name the thing the sentence was pointing at rather than the word standing in for it.

The token file also publishes the sha256 of the word list itself, under `copy.words_to_avoid_digest`. A repository that vendors the list compares against that value, which changes when the list changes and at no other time; a digest over the whole token file would move on every unrelated edit and get muted.
