---
"mrbinnacle-skills": patch
---

`scripts/validate_eval_corpora.py` now refuses a plugin eval case whose `expected_outcome` names a card and quotes, in double quotes, words that card's description no longer carries. Two cases did: `subagent-handback-dispatch` quoted the description from before #572, and `decision-rights-issue-bodies` quoted an older description of `decision-rights`. Both cases now quote the current descriptions. `subagent-handback-dispatch` was run once against the current description, and the orchestration eval manifest records the result. The claims ledger no longer gives a single measurement date for every card's standing cost, because each card's row states its own date. Installed users need do nothing.
