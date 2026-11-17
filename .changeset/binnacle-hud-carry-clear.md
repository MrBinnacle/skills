---
"mrbinnacle-skills": minor
---

The Binnacle HUD no longer loses what you handed it when you run `/clear` or `/resume`. Claude Code empties a session's state at both, and it starts no new session for the mod, so before this change every Log thought, unsent Memory line, half-typed field and waiting heads-up was gone after each clear. The mod now reads these lists as the old session ends and writes them back once the new one runs. Nothing is written to a file.

After `/clear` the HUD keeps the Log, the failed keeps, the unsent Memory lines, the field's text and the heads-ups. After `/resume` it keeps the same, except the heads-ups, which are about the conversation you left. The Memory you approved with Send is not kept after either, because you approved it for one conversation. Anything you write in the new session before the lists come back is kept beside them, nothing is listed twice, and a second `/clear` before the first restore folds into it.

The README now also says that Memory reaches the main conversation only. In one headless run on Claude Code 2.1.326, a general-purpose subagent did not receive the memory section.

This was tested with the Claude Code test kit on 2.1.326, with a mutation pass in which each of 9 changed conditions turns a test red. Headless probes showed the two engine steps it rests on. It was not tested with an interactive `/clear` or `/resume`.
