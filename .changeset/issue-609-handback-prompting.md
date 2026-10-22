---
"mrbinnacle-skills": patch
---

`subagent-handback` now fires when an agent writes the prompt for a research subagent that the user will dispatch, not only when the agent dispatches one itself. Its description opens "Use when prompting or dispatching a research subagent" in place of "Use before dispatching a subagent for research". In `claude plugin eval` runs on `claude-opus-5-5`, the card fired in 0 of 6 runs of the user-dispatch case under the old description and in 5 of 5 under the new one. Its `EVIDENCE.md` Applicability scope row and the orchestration bucket README line now say the same. The orchestration eval manifest records every run. Installed users need do nothing.
