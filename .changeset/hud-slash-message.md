---
"mrbinnacle-skills": patch
---

Binnacle HUD (Claude Code): a message that begins with `/` but is not a command, such as a file path, now carries a waiting heads-up note and frees the next note's turn, like any other message. A skill command does the same, because it starts a model turn. Before, the mod skipped every message that began with `/`, so the note stayed waiting while Claude answered.
