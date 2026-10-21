---
"mrbinnacle-skills": patch
---

The README now gives the per-skill session cost as `/context` counts it: about 70 to 80 tokens for each model-invocable skill, measured on Claude Code 2.1.305 on 2026-10-20, with under 20 where a host lists a skill by name only. It said 44 to 63 tokens, the figure `skill-harness skill audit` reports. The pre-registered `/context` measurement in [#361](https://github.com/MrBinnacle/skills/issues/361) found nine of eleven cards at about 80 and none of the harness figures within 10% of `/context`. The three run by hand still cost nothing. The standing-cost validator no longer expects the README to carry the harness date; the claims ledger still does. Installed users need do nothing.
