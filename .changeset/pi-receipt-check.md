---
"mrbinnacle-skills": patch
---

The public release check now fails when the README sends Pi users to a pin that the newest Pi install receipt did not test, and names the fix: run the receipt at the new pin. Until now, re-running the receipt on each release was a written rule that nothing checked, and v4.2.0 shipped with a Pi pin that only a v4.1.1 receipt backed.
