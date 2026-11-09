---
"mrbinnacle-skills": minor
---

The Binnacle HUD keeps the text of a Claude prompt that was emptied by accident, such as by Ctrl+C or a misclick, rather than submitted. Claude Code's own Ctrl+S stash remains the way to set a draft aside on purpose. The Log shows "Last cleared draft" with the time, the length and the text. `r` puts the text back into an empty prompt box and never submits it, and `x` forgets it. The mod holds the draft being typed only in its own memory, and a cleared draft in session state until it is restored, forgotten or the session ends. It writes no draft to disk, so a crash still loses the prompt.
