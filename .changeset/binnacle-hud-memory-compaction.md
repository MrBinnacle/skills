---
"mrbinnacle-skills": minor
---

The Binnacle HUD gives Claude your Memory lines again after Claude Code compacts the chat. When the main chat compacts, the mod adds the lines of your last recorded Send after the summary, never the lines you changed since. The Memory status line then follows what the session stores after the compaction. It says "Re-attached after the compaction at HH:MM." once your lines are stored, "Approved HH:MM. Not checked after the compaction at HH:MM." until then, and "Not in Claude's context after the compaction at HH:MM. Send again to give Claude these lines." when a prompt or a reply is stored first; Send is offered again in that case. Subagent compactions and precomputed summaries are left alone. The status words, their colour and the Send key now come from one answer, so only a status that says Claude has the lines is drawn in the success colour. This was tested with the Claude Code test kit, not yet in a live compaction.
