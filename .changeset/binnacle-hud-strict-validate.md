---
"mrbinnacle-skills": patch
---

binnacle-hud now passes `claude plugin validate --strict`. Before this change, Claude Code 2.1.325 reported 10 type errors. In the mod, the HUD's focus ring was computed as a plain number where the view state allows only 0, 1 or 2; it is now typed as that state's ring. In two test files, two leftover `console.log` lines were removed and a test helper's `placement` argument is typed as `'dock' | 'inline'`. The README now gives the one-step install, `/plugin install binnacle-hud --marketplace MrBinnacle/skills`, for Claude Code 2.1.275 or later. The mod's behaviour does not change.

Action for installed users: None.
