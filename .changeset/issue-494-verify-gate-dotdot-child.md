---
"mrbinnacle-skills": patch
---

The verification gate in `mechanisms/verify-gate` now tracks a written file inside a child directory whose name starts with two dots, such as `..foo`. `underRoot` counted a path as outside the root when its relative form started with the two characters `..`, so `..foo\a.ts` counted as outside and the gate did not ask for a check. It now counts a path as outside only when the relative form is `..` itself or starts with `..` and a path separator. The plugin manifests do not ship `mechanisms/`, so installed users get nothing new.
