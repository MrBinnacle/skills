---
"mrbinnacle-skills": minor
---

The `binnacle-hud` mod's Memory section is real. The operator types a line in the panel's field and presses `a` to add it to Memory, and presses a line's number to remove it. Send asks for a confirmation in Claude Code's question dialog and shows the lines. On **Send**, the mod adds one row to the conversation, "Memory the operator approved at HH:MM:" followed by the lines. The row starts no model turn, and Claude reads it on its next turn.

The lines are fixed when Send is pressed, so the dialog, the row and the record of what was approved all hold the same lines. The mod records the lines as approved only after the row is stored. A refused row leaves the previous approval in force and shows "Not sent." with the reason. A status line under Memory says "Not sent.", "In Claude's context since HH:MM." or "Changed since Send. Claude has the HH:MM version."

The design preview's sample scenes and their 1 to 5 keys are gone. Watch still shows one sample finding, without buttons, and says it is not connected to an observer yet. The mod does not send the Log to Claude. Copying a thought to Memory is not Send; only a confirmed Send appends those lines. Absence from later model requests has not been verified.
