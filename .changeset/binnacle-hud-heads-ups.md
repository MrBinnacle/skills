---
"mrbinnacle-skills": minor
---

The Binnacle HUD now keeps every heads-up from Claude Code's You should know side agent. The side agent holds one note per session, so a newer note replaced one you had not acted on, and the older note was gone. The HUD lists each note, numbered, in a Heads-ups section at the top of the side panel. The section appears only while a note waits.

Press `h` to put every waiting note into the prompt box after anything you have typed. Nothing is sent: the notes reach Claude only when you send the prompt yourself. A note leaves the list when the prompt you send holds it, so clearing the box without sending loses nothing, and `h` never puts the same note in twice. They go in as quoted data, with an instruction that Claude treats them as information rather than instructions and asks before anything that deletes, publishes, sends, installs or changes settings. Press `x` to dismiss them. A note you send from the side agent's own band is cleared from the list too. If the prompt box cannot take the notes, for example while a dialog is open, they stay in the list and a notice says why.

The list lasts for the session only, as the Log does. The HUD reads notes only from the bundled side agent, through that agent's own store writes and its store file, and, in the copy it puts in the prompt box, removes characters that draw as nothing and any tag that could open or close the quoted block early, including spaced, full-width, underscore, and Unicode hyphen and minus forms. A tag spelled with look-alike letters from another alphabet is not removed. Each block's opening tag carries an id made from the note's line. A note leaves the list only when a prompt that holds its own block, tips-anywhere's block for it, or the side agent's band form actually enters; its words inside another note's block do not count.

This was tested with the Claude Code test kit on 2.1.326, including a store write from a stand-in side agent in the built-in tier and a scratch mutation pass, not kept in the repository, in which each changed condition turned a test red. It was not tested in a live interactive session.
