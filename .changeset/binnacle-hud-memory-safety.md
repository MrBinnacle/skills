---
"mrbinnacle-skills": patch
---

Memory in the Binnacle HUD now closes three harms. Memory lines join Claude's system instructions, so each of these changes what Claude reads.

Hidden characters are removed from a Memory line and a Log thought before they are saved. These are control characters, zero-width and direction-changing characters, and the tag characters that can carry text a person cannot see to a model. Pasted text could bring them in. The 2000-character limit now counts only the characters that remain, and a field that holds only hidden characters adds nothing.

The Send question now says what a Send costs. Claude's next request rewrites the prompt cache once, so that request costs more and takes longer than a cached one.

When a Send has not reached Claude, the HUD now says so and gives a next step. If a main-loop turn starts after the Send and ends without Claude Code asking for the memory section, the status says the turn ran without the lines. Press `q` to put the approved lines in the prompt box as a request to keep to them. Nothing is sent until you send the prompt. A turn that started before the Send, and a subagent's turn, do not count.

This was tested with the Claude Code test kit on 2.1.326 and type-checked against its type file, with a mutation pass in which each of 13 changed conditions turns a test red. It was not tested in a live interactive session.
