---
"mrbinnacle-skills": minor
---

The Binnacle HUD keeps your Memory lines with Claude after Claude Code compacts the chat. When the main chat compacts, the mod adds the lines of your last recorded Send after the summary, once, and never the lines you changed since. The Memory status line then says "Re-attached after the compaction at HH:MM." when the HUD saw that row stored, "Not checked after the compaction" when it did not see the boundary, and "Not in Claude's context after the compaction at HH:MM. Send again to restore it." when the chat went on without the row; Send is offered again in that case. Subagent compactions and precomputed summaries are left alone.
