---
"mrbinnacle-skills": patch
---

The Binnacle HUD no longer keeps a cleared prompt draft, so it never reads the prompt box or puts prompt text in session state. Claude Code brings a cleared draft back itself: after Ctrl+C, press Up on the empty prompt.

Each Memory line and each failed keep gets an id when it is saved, so a remove key or `d` acts only on the entry it was drawn for, never on another with the same text. Lists saved by 4.1.0 as plain text still load: session start gives each line an id. The `0` key is gone; removing one of the first nine lines brings the next into reach. `a` adds the text the pane showed, and `p` the Log thought on screen.

A refused Send is shown only while the lines differ from what Claude has. When an unrecorded Send stands, a later refused Send reads "The later Send was refused:" rather than "Not sent."
