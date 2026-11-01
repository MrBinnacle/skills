---
"mrbinnacle-skills": patch
---

The orchestration eval suite gains `subagent-handback-self-dispatch`, a should-fire case in which the agent under test dispatches the research sweep itself, with `Agent` allowed. It differs from `subagent-handback-dispatch` only in who dispatches. On `claude-opus-5-5`, the card was invoked in 4 of 5 runs of the new case and in 0 of 6 runs of the original. The eval manifest records both runs as observations, not measurements. `claude plugin eval` result directories under `skills/*/evals/results/` are now ignored by git. Installed users need do nothing.
