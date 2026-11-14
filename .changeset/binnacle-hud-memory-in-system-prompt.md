---
"mrbinnacle-skills": minor
---

The Binnacle HUD now gives Claude your Memory lines as part of its system instructions on every request, instead of as one row in the chat. Before this change, a confirmed Send added a row to the conversation, and a compaction could summarize that row away. Now a confirmed Send adds the lines to Claude Code's own memory section of the system prompt. Claude reads them from its next turn onward. The system prompt is not part of the chat that Claude Code compacts, so the lines stay through a compaction. A Send rewrites the prompt cache once, so the next request costs more than a cached one and Claude Code shows a dim line naming the mod.

The Memory status now reports what the mod saw. After a Send it says "Sent at HH:MM. Not yet in Claude's instructions." It says "In Claude's instructions since HH:MM." only once the mod's hook has added that Send's lines to the memory section, and HH:MM is when it did. If the lines change after a Send, it says "Changed since Send." and whether Claude has the earlier version yet. If Claude Code stops asking for the memory section, the status stays at "Not yet in Claude's instructions." instead of claiming the lines arrived. The notice "The HUD could not record that Send." is gone, because the Send is now saved in one step. The Watch preview, which showed one sample finding and was never connected to anything, is removed; the collapsed strip's keys are now `m` for Memory and `l` for Log. Session state written by 4.1.1 still loads.

This was tested with the Claude Code test kit and with a headless probe of the same mechanism on Claude Code 2.1.325. It was not tested in a live interactive session or across a real compaction.

Action for installed users: None.
