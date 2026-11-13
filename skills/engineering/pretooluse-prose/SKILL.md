---
name: pretooluse-prose
description: A PreToolUse Bash guard reads the whole command, so a heredoc or commit message naming a banned command trips it. Use on BLOCKED by a guard, writing a Bash matcher, or a non-prose argument misread.
---

# PreToolUse Bash Guards Match Prose, Not Just Commands

## Problem

A pre-tool-call guard on the shell tool receives the **entire command string**. That string
routinely contains English: commit messages, `gh issue create` bodies, heredocs, comments.

A guard written as `re.search(r"\bgh\s+issue\s+create\b", cmd)` therefore fires on

```bash
git commit -F- <<'EOF'
Three issues were created with `gh issue create --body-file -`.
EOF
```

which invokes no such command. Worse, a guard that blocks a forbidden *phrase* will block the
document that quotes the phrase **to forbid it** — so the fix for the anti-pattern
cannot be committed.

Origin incident, 2026-08-17: a newly written guard blocked the very commit installing it.
The message described the CLI it policed and quoted the banned wording as an example. Two
independent defects, one commit.

## Context / Trigger Conditions

- A hook you just wrote blocks its own installation, its own tests, or its documentation.
- `BLOCKED by <your guard>` appears on a `git commit`, `cat`, or `echo` that contains prose.
- A guard fires on a heredoc body rather than on a command.
- You are writing a shell guard that matches its pattern against the whole command.
- **Non-prose branch:** a live command is blocked because an argument contains the banned word.
  `git fetch origin pull/292/head` names a pull-request ref, and a `git pull` guard reads `pull`
  in the path. Tighten the pattern so it names the whole command (`git\s+pull\b`), not one word.

## Solution

**When a guard blocks your prose, write the file with a file-write tool, not a heredoc.** Use
the agent's Write tool, then pass the path: `git commit -F msg.txt`, `gh pr create --body-file
body.md`. No guard reads the prose. Read the file back before you send it: a blocked call
writes nothing, so a same-named file from earlier work can be what gets posted.

**When you write the guard, keep these five rules.** They are the contract. The pattern, the
wording of the refusal and the wiring are yours to replace.

1. **Price the two errors.** A false block costs one re-issue. A false pass costs what the
   guard protects. Each rule below fails toward the block.
2. **Match the pattern anywhere in the command.** A list of places where a command can start
   is never complete. A subshell, a `{ }` group, backticks, `!` and `then` each start one, and
   every place the list lacks is a silent pass. A maintainer's guard tried such a list twice
   and removed it ([gotchas.md](gotchas.md), 2026-11-12).
3. **Accept the block on prose that only mentions the pattern.** That block is the price of
   rule 2, and the file route above clears it. Relaxing the match needs a reader that is
   certain which text the shell does not run. This card supplies no such reader. A
   relaxation that is unsure keeps the block.
4. **A fault in the guard never blocks.** Catch every internal error and pass.
5. **Put the remedy in the refusal text.** Name the text that matched, and say "write the text
   to a file and pass the path". The blocked agent reads the refusal, not this card.

Open [guard-recipes.md](guard-recipes.md) when you wire the guard into Claude Code. It supplies
the matcher, the exit codes and a test call, checked 2026-11-12.

## Verification

Run every row of the matrix below through the guard's real input channel, in both directions,
every time. A guard tested only on prose can pass real commands. A guard tested only on real
commands can block the file route too, and then the agent has no way through.

## Example

Minimum test matrix for any shell guard:

| Case | Expect |
| --- | --- |
| Real offending command | block |
| The command in a subshell, a `{ }` group or backticks, or after `!`, `then`, `do`, `else` or `elif` | block |
| The command behind a wrapper, a path or a nested shell (`env`, `/usr/bin/`, `bash -c`) | block |
| Offending command after a `<<-` heredoc | block |
| Prose that names the command: a quoted heredoc, `-m "$(cat <<'EOF' …)"`, a quoted string, a PowerShell here-string, a `;` inside quotes | block, and the refusal names the file route |
| The same prose in a file passed by path (`-F msg.txt`, `--body-file body.md`) | pass |
| A command the rule allows (`list`, `view`) | pass |
| Unrelated command | pass |
| Malformed stdin | pass |

## Notes

Open [gotchas.md](gotchas.md) when a Bash guard blocks its own install, a commit message, or a heredoc body. It records every observed block, including one where the input was not prose at all.

- **`git commit -F-` is the highest-risk input.** Commit messages describe commands and quote
  forbidden strings by design. If a guard is going to block prose, it will be here.
- **Duplicating regexes across two guards is deliberate when they enforce one discipline** —
  but they drift. Note the sibling in a comment so a change to one prompts a change to both.
- The same trap applies to `Edit|Write` guards on documentation paths (a matcher of letters
  and `|` is a list of exact tool names, so `Edit|Write` matches those two tools only; checked
  2026-10-06): a skill file *describing* an anti-pattern
  contains the anti-pattern verbatim.
- Prefer the file route over a suppression escape hatch. An `ACK=1` bypass gets
  used reflexively and the guard stops meaning anything.
