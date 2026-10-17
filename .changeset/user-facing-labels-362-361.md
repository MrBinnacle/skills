---
"mrbinnacle-skills": patch
---

Corrects two labels a reader can check. The `pull-rebase` evidence record called a receipt "harness 1.0.0". The receipt carries `sers_version 1.0.0` and no harness version, and skill-harness has never shipped 1.0.0, so the label now reads "SERS 1.0.0". The README's per-skill cost range now reads 44 to 63 tokens, the lowest and highest figures in the cards' own `skill-harness skill audit` rows, where it previously read 45 to 65. This is an interim fix for #361. The pre-registered `/context` measurement is still owed. Installed users need do nothing.
