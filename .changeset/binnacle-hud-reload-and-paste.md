---
"mrbinnacle-skills": patch
---

The Binnacle HUD no longer lets a submit after a plugin reload drop a cleared draft stored before it; each cleared draft now records which load wrote it. Pasting a copied cleared draft back removes that draft's row, and only that one. When an unrecorded Send stands, a later refused Send reads "The later Send was refused:" rather than "Not sent."
