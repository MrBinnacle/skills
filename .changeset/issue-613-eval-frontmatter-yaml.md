---
"mrbinnacle-skills": patch
---

`scripts/validate_eval_corpora.py` now refuses a plugin eval case whose frontmatter is outside a small YAML subset that loads as written. Before, a `: ` inside a plain value passed the check, and `claude plugin eval` then skipped the case with one log line (#613). The check also refuses three lines that load but change the value: a ` #` that YAML reads as a comment, an indented line that folds into the value above, and a key stated twice. It refuses any other line it does not recognise, rather than skipping it. All seven current eval cases pass unchanged. Installed users need do nothing.
