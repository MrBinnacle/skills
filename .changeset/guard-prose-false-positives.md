---
"mrbinnacle-skills": patch
---

Record three guard prose false-positives from a single rotation pass on `pretooluse-bash-guard-prose-false-positive`.

The card gains a `gotchas.md`. All three reproductions happened on 2026-08-23, across two different guards, and none was a defect in the guarded behaviour.

A corpus-search guard refuses a bare `find` over a symlinked skills tree, because an unfollowed symlink silently undercounts it. It blocked a `gh pr create` whose heredoc body was English prose containing that verb in an ordinary sentence. No filesystem search was being run. The guard scans the whole command string, the heredoc body is part of that string, and a common English word is its trigger token. A rebase guard fired twice the previous session on the same principle, once on a verification `grep` whose argument named the trap and once on a commit message whose body explained it.

The pattern is worth naming: writing about a trap is how you trip its guard. The commit message, the pull-request body, and the card documenting a failure mode are the artifacts most likely to name that failure mode, and a substring match cannot distinguish them from an attempt to commit the failure. A collection whose product is trap documentation will hit this more than most projects, and the cost lands on whoever is doing the recording.

The disposition is to keep the block rather than loosen the predicate. A false positive costs one reword; a false negative costs the incident the guard exists to prevent. What makes the trade tolerable is that the block message names the token that matched, which all three did, so each reword took seconds. The narrower fix — anchoring the predicate to command position so a token inside a quoted heredoc body cannot match — is a change to the hook rather than to the card, and is not made here.

Version 1.1.0. Not promoted.
