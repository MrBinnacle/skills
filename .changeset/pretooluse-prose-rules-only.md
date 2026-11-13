---
"mrbinnacle-skills": patch
---

The `pretooluse-prose` card no longer ships detector code. Its sample defined "command position" as the start of the string, a point after a shell separator, or the inside of `$(`. That list left out a subshell, a `{ }` group, backticks, `!`, and the words `then`, `do`, `else` and `elif`, so a guard built from the sample let a banned command through in each of those places with no message. The card now gives five rules instead: price the two errors, match the pattern anywhere in the command, accept the block on prose that only mentions the pattern, never block on a fault in the guard, and name the remedy in the refusal text. The remedy is to write the prose to a file with the agent's file-write tool and pass the path. The card's test matrix now expects prose in a heredoc or a quoted string to block with that remedy. The Claude Code wiring, including the matcher `Bash|PowerShell` so a guard also sees the PowerShell tool, moved to `guard-recipes.md`.
