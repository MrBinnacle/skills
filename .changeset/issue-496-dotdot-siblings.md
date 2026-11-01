---
"mrbinnacle-skills": patch
---

The `eol-guard` and `session-packet` mechanisms now count a child directory whose name starts with two dots, such as `..foo`, as inside the repository. Each tested a relative path with `startsWith("..")`, so `..foo/a.ts` counted as outside. For `eol-guard`, that meant a line-ending conversion in such a file went unchecked. For `session-packet`, it meant a packet directory or branch-store worktree there was not excluded from `git status`. Each now counts a path as outside only when its relative form is `..` itself or starts with `..` and a separator, the same rule #495 gave `verify-gate`. The plugin manifests do not ship `mechanisms/`, so installed users get nothing new.
