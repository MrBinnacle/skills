---
"mrbinnacle-skills": minor
---

The collection ships a second Claude Code mod, `binnacle-hud`, at `mods/binnacle-hud/`. The mod draws a side panel beside the chat with a private Log. It keeps each thought typed in the panel's field, or sent with `/log` from the Claude app on a phone, with its time and where it came from. None of the Log is sent to Claude.

`/log` asks for the thought in Claude Code's question dialog, because the phone draws that dialog but not a mod's panel. It refuses text typed after the command, because the conversation records the command line. The panel's Memory and Watch sections are a design preview with sample data.

ADR 0009 prices a new mod as a new card, so this changeset is minor. The new marketplace entry installs nothing until the release that carries this changeset is pinned.
