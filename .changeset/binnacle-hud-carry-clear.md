---
"mrbinnacle-skills": minor
---

The Binnacle HUD no longer loses what you handed it when you run `/clear` or `/resume`. Claude Code empties a session's state at `/clear` and starts no new session for the mod, so before this change every Log thought, unsent Memory line, half-typed field and waiting heads-up was gone after each clear. The mod now reads these lists as the old session ends and writes them back once the new one runs. Nothing is written to a file.

After `/clear` the HUD keeps the Log, the failed keeps, the unsent Memory lines, the field's text and the heads-ups. After `/resume` it keeps the same, except the heads-ups, which are about the conversation you left. The Memory you approved with Send is not kept after either, because you approved it for one conversation. Whether `/resume` empties state was not tested, so the mod drops the old Send and the old heads-ups itself and keeps anything the new session made. Anything you write in the new session before the lists come back is kept beside them, nothing is listed twice, and a second `/clear` before the first restore folds into it.

The README now also says that Memory reaches the main conversation only. In one headless run on Claude Code 2.1.326, a general-purpose subagent did not receive the memory section.

This was tested with the Claude Code test kit on 2.1.326, and a scratch mutation pass, not kept in the repository, in which each changed condition turned a test red. Headless probes showed the two engine steps it rests on. It was not tested with an interactive `/clear` or `/resume`.
