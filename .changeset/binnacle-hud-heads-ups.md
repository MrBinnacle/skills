---
"mrbinnacle-skills": minor
---

The Binnacle HUD now takes the heads-ups that Claude Code's built-in side agent offers above the prompt, and gives each one to Claude with no key press. Before this change, each heads-up sat in a row above the prompt until you pressed Learn more, Knew this already or Dismiss. Now the mod reads each note from the side agent's own store write, lists it in a new Heads-ups section of the panel, and takes its row off the band. The first note since your last message goes to Claude as a turn of its own. Later notes go with your next message, so a note's turn cannot set off a chain of turns. Press `h` in the panel to read every note of the session in full, with how each reached Claude.

Claude acts on a note it finds to hold, without asking you, and you do not read the note first. A note can repeat text from files or web pages. The mod strips hidden characters and gives Claude each note as escaped JSON with a sentence saying an instruction inside it is not one to follow; how much that lowers the risk of a planted instruction has not been measured.

This was tested with the Claude Code test kit against the 2.1.331 offer format. The store route has not yet run in a live session.

Action for installed users: None.
