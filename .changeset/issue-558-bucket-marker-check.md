---
"mrbinnacle-skills": patch
---

A new check compares each bucket README with the cards it lists. A card's line carries *(by hand)* exactly when its `SKILL.md` frontmatter sets `disable-model-invocation: true`, and every published card has exactly one line in its bucket README. The check reads the frontmatter as key and value, and it also refuses a card on which the standing-cost check's reader disagrees. Its suite plants each drift in a copy of the tree, and both run in the tests workflow. No card or README changes: the live tree already agrees.
