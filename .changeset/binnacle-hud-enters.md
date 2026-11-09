---
"mrbinnacle-skills": minor
---

The collection ships a second Claude Code mod, `binnacle-hud`, at `mods/binnacle-hud/`. The mod draws a side panel beside the chat with a Log. It keeps each thought typed in the panel's field, or sent with `/log` from the Claude app on a phone, with its time and where it came from. The mod does not send the Log to Claude. Absence from a later model request has not been verified; other plugins can read the Log and intercept or change state writes.

`/log` asks for the thought in Claude Code's question dialog, because the phone draws that dialog but not a mod's panel. It refuses text typed after the command, because the conversation records the command line. The panel also holds Memory lines the mod sends only after confirmation, and a Watch preview with sample data.

ADR 0009 prices adding a mod as admitting a card, so this changeset is minor. The new marketplace entry installs nothing until the release that carries this changeset is pinned.
