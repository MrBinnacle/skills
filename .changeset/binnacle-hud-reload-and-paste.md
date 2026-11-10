---
"mrbinnacle-skills": patch
---

The Binnacle HUD no longer lets a submit after a plugin reload drop a cleared draft stored before it; each cleared draft now records which load wrote it. Pasting a copied cleared draft back removes that draft's row, and only that one. When an unrecorded Send stands, a later refused Send reads "The later Send was refused:" rather than "Not sent."

A HUD button now acts only on the record it was drawn for, even when the pane has not redrawn since. Each Memory line and each failed keep gets an id when it is saved, so removing a line or dismissing failed keeps never removes another entry with the same text. A history, plugin or undo restore drops only the cleared draft it brought back, and Forget checks which load wrote the draft. The p key copies the Log thought that was on screen, not one kept after the pane was drawn. Lists saved by 4.1.0 as plain text still load, and the first write saves them in the new shape.
