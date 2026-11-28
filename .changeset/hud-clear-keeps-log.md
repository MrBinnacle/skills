---
"mrbinnacle-skills": patch
---

Binnacle HUD (Claude Code): `/clear` no longer empties the Log and the Memory draft. Claude Code resets a mod's session state on `/clear`, so every kept thought and every draft line was lost without a message. The mod now puts both back. It does not put back the Send record: the new conversation was given nothing, so the panel says "Not sent." until you send the lines again. The mod still writes no file.
