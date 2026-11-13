---
"mrbinnacle-skills": patch
---

The tips-anywhere mod no longer lets a heads-up close its own data block. When you hand a heads-up to Claude, the mod puts the note inside a `<heads-up>` block and tells Claude the block is information, not instructions. The mod removed each `heads-up` tag from the note once, so a note holding `</heads-</heads-up>up>` lost the inner tag and the pieces around it joined into a real `</heads-up>`. Text after that tag then sat outside the block. A tag split across the note's two fields, or left without its `>`, also survived. The mod now removes the start of every `heads-up` tag from the whole note, and repeats until none is left. Six new tests cover a tag inside a tag, a tag start inside a tag start, mixed case with spaces and an attribute, two ways to split a tag across the fields, and a tag left open. Four of them failed on the old code, and each of three weaker fixes fails at least one.
