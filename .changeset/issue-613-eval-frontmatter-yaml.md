---
"mrbinnacle-skills": patch
---

`scripts/validate_eval_corpora.py` now refuses a plugin eval case whose frontmatter is outside a small YAML subset that loads as written. Before, a `: ` inside a plain value passed the check, and `claude plugin eval` then skipped the case with one log line (#613). The check also refuses three lines that load but change the value: a ` #` that YAML reads as a comment, an indented line that folds into the value above, and a key stated twice. A double-quoted value may hold no backslash, because YAML refuses an unknown escape such as `\q` and the check does not model YAML's escape table; single quotes need no escapes. The check refuses any other line it does not recognise, rather than skipping it. Every current eval case passes unchanged. Installed users need do nothing.
