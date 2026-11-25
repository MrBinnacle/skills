---
"mrbinnacle-skills": patch
---

The Binnacle HUD now starts even when Claude Code refuses one of its commands. Before this change, a refused `/hud` or `/log` stopped the session-start step, so the panel never opened and nothing told you why. Now the panel opens first, and a notice names the command that could not be added. A panel that fails to open also shows a notice instead of failing silently.

The HUD's lists now have limits. The Log keeps the newest 100 thoughts, and the list of thoughts that failed to save keeps its newest 100. The oldest is dropped. Memory holds at most 20 lines. When it is full, the keys that add a line are gone and the HUD says to remove one first, so no line you chose is dropped without you. One thought or line keeps its first 2000 characters. When the mod cuts a thought it kept, `/log` says so in its reply, and the HUD says so in a notice. A thought that failed to save is cut the same way, without a notice.

On Claude Code 2.1.326 or later, a long thought, a Memory line, or the details of an opened heads-up in the side panel stops at three lines, so the field stays in view. An older Claude Code refuses that setting and would draw an empty panel, so the HUD uses it only after reading the version. The README now names the command that writes the type files. The mod's `tsconfig.json` extends them. The README also says what the dialog's "Chat about this" choice does.

This was tested with the Claude Code test kit on 2.1.326, where every test passes, and on 2.1.325, where only the test of the three-line rows fails, as expected. It was not tested in a live interactive session.
