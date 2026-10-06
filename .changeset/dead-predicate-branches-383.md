---
"mrbinnacle-skills": patch
---

`dead-predicate` now loads when a hook didn't fire or a reminder never arrived, and it diagnoses three more ways a live router rule matches nothing: a rule shadowed by an earlier one in a first-match router, a rule naming a skill that was renamed or uninstalled, and a rule whose pattern never reaches the case that would refute its claim. Its probe scripts moved to a new `probes.md`, take the rule file from `RULES` instead of a hard-coded name, and decode the JSON before scanning for `\b`.
