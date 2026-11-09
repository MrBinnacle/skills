---
"mrbinnacle-skills": minor
---

The collection ships a second Claude Code mod, `binnacle-hud`, at `mods/binnacle-hud/`. It draws a side panel beside the chat with a private Log: a thought typed in the panel's field, or sent with `/log` from the Claude app on a phone, is kept with its time and where it came from, and none of it is sent to Claude. `/log` asks for the thought in Claude Code's question dialog, because the phone draws that dialog but not a mod's panel, and it refuses text typed after the command, because the conversation records the command line. The panel's Memory and Watch sections are a design preview with sample data. Adding a mod is priced as admitting a card under ADR 0009, so this is minor. The new marketplace entry installs nothing until the release that carries this changeset is pinned.
