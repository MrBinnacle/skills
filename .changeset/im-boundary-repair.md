---
"mrbinnacle-skills": patch
---

`im-down` and `im-up`: both cards now define `<skill-dir>`, including how to pick one path when several installed versions exist. `im-down` says to run the receiver checks before the close, so a red check does not cost a second close. `im-up` says to run its self-test directly rather than through pytest, and records a timing-bound check that rejected and then accepted the same packet (#389).
