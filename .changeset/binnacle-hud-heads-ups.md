---
"mrbinnacle-skills": minor
---

The Binnacle HUD now keeps every heads-up from Claude Code's You should know side agent. The side agent holds one note per session, so a newer note replaced one you had not acted on, and the older note was gone. The HUD lists each note, numbered, in a Heads-ups section at the top of the side panel. The section appears only while a note waits.

Press `h` to put every waiting note into the prompt box after anything you have typed. Nothing is sent: the notes reach Claude only when you send the prompt yourself. They go in as quoted data, with an instruction that Claude treats them as information rather than instructions and asks before anything that deletes, publishes, sends, installs or changes settings. Press `x` to dismiss them. A note you send from the side agent's own band is cleared from the list too. If the prompt box cannot take the notes, for example while a dialog is open, they stay in the list and a notice says why.

The list lasts for the session only, as the Log does. The HUD reads notes only from the bundled side agent, and removes hidden characters and tags that could close the quoted block early.

This was tested with the Claude Code test kit on 2.1.326, including a mutation pass in which each of 10 changed conditions turns a test red. It was not tested in a live interactive session.
