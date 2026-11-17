---
"mrbinnacle-skills": patch
---

The Binnacle HUD now starts even when Claude Code refuses one of its commands. Before this change, a refused `/hud` or `/log` stopped the session-start step, so the panel never opened and nothing told you why. Now the panel opens first, and a notice names the command that could not be added. A panel that fails to open also shows a notice instead of failing silently.

The HUD's lists now have limits. The Log keeps the newest 100 thoughts and the list of failed keeps the newest 100 entries; the oldest is dropped. Memory holds at most 20 lines. When it is full, the keys that add a line are gone and the HUD says to remove one first, so no line you chose is dropped without you. One thought or line keeps its first 2000 characters, and `/log` says when it cut one.

On Claude Code 2.1.326 or later, a long thought or Memory line in the side panel stops at three lines, so the field stays in view. An older Claude Code refuses that setting and would draw an empty panel, so the HUD uses it only after reading the version. The README now names the command that writes the type files `tsconfig.json` extends, and says what the dialog's "Chat about this" choice does.

This was tested with the Claude Code test kit on 2.1.326 and 2.1.325. It was not tested in a live interactive session.
