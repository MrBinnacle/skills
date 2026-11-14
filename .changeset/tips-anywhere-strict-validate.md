---
"mrbinnacle-skills": patch
---

tips-anywhere now passes `claude plugin validate --strict`. One test read the second entry of a list without proving it exists, which the type checker of Claude Code 2.1.325 reports as an error; the test now marks it as present, and a missing entry still fails the test. The README now gives the one-step install, `/plugin install tips-anywhere --marketplace MrBinnacle/skills`, for Claude Code 2.1.275 or later. The mod's behaviour does not change.

Action for installed users: None.
