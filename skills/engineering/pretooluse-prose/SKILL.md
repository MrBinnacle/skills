---
name: pretooluse-prose
description: A PreToolUse Bash guard reads the whole command, so a heredoc or commit message naming a banned command trips it. Use on BLOCKED by a guard, writing a Bash matcher, or a non-prose argument misread.
---

# PreToolUse Bash Guards Match Prose, Not Just Commands

## Problem

A `PreToolUse` hook on the `Bash` matcher receives the **entire command string**. That string
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

Measured instance, 2026-08-17: a newly written guard blocked the very commit installing it.
The message described the CLI it policed and quoted the banned wording as an example. Two
independent defects, one commit.

## Context / Trigger Conditions

- A hook you just wrote blocks its own installation, its own tests, or its documentation.
- `BLOCKED by <your guard>` appears on a `git commit`, `cat`, or `echo` that contains prose.
- A guard fires on a heredoc body rather than on a command.
- You are writing a `PreToolUse` matcher on `Bash` and your detection regex has no anchor.
- **Non-prose branch:** a live command is blocked because an argument contains the banned word.
  `git fetch origin pull/292/head` names a pull-request ref, and a `git pull` guard reads `pull`
  in the path. Same defect, no prose: the predicate read text instead of command position.

## Solution

**When a guard blocks your prose, write the file with a file-write tool, not a heredoc.** Use
the agent's Write tool, then pass the path: `git commit -F msg.txt`, `gh pr create --body-file
body.md`. No guard reads the prose. Read the file back before you send it: a blocked call
writes nothing, so a same-named file from earlier work can be what gets posted.

**1. Anchor detection to a command position outside quotes.** A command starts at the beginning
of the string, after an unquoted shell separator, or inside `$(`, optionally after `VAR=value`
assignments. A `;` inside quotes is data, and a regex cannot see quotes, so scan for them:

```python
def command_starts(cmd):
    starts, quote, i = [0], None, 0
    while i < len(cmd):
        c = cmd[i]
        if quote == "'":
            quote = None if c == "'" else quote
        elif c == "\\":
            i += 1
        elif c == "$" and cmd[i + 1:i + 2] == "(":
            starts.append(i + 2)
        elif quote == '"':
            quote = None if c == '"' else quote
        elif c in "'\"":
            quote = c
        elif c in ";&|\n":
            starts.append(i + 1)
        i += 1
    return starts

_PREFIX = re.compile(r"[\s;&|]*(?:[A-Za-z_]\w*=\S*\s+)*")
CREATE_RE = re.compile(r"gh\s+(?:issue|pr)\s+create\b", re.IGNORECASE)

def runs(shell, pattern):
    return any(pattern.match(shell, _PREFIX.match(shell, s).end())
               for s in command_starts(shell))
```

**2. Split the heredoc body from the shell before deciding anything.** The body is the
artifact; the shell is the invocation. Detect commands in the shell part, inspect content in
the body part.

```python
HEREDOC_RE = re.compile(
    r"<<(-)?\s*(['\"]?)(\w+)\2\s*\n(.*?)(?:^(?(1)\t*)\3$|\Z)",
    re.DOTALL | re.MULTILINE)

def split_shell_and_body(cmd):
    bodies = []
    shell = HEREDOC_RE.sub(lambda m: (bodies.append(m.group(4)), "<<HEREDOC>>")[1], cmd)
    for m in re.finditer(r"--body(?:-file)?[= ]\s*(['\"])(.*?)\1", shell, re.DOTALL):
        bodies.append(m.group(2))
    return shell, "\n".join(bodies) if bodies else shell
```

`<<-` lets the terminator carry leading tabs; plain `<<` does not. `(-)?` captures only a real
dash, so `(?(1)\t*)` accepts tabs for `<<-` alone. Without that branch a `<<-` match runs to the
end of the string and swallows every later command into the body.

**3. Fail open on every internal error.** A guard must never be the reason work stops.

```python
except Exception:
    return 0
```

**4. Exit codes** (Claude Code hooks docs, checked 2026-10-05). `2` blocks the tool call and
feeds stderr to the model; `0` raises no objection, so the normal permission flow applies. To
warn without blocking, exit `0` and print `{"hookSpecificOutput": {"hookEventName": "PreToolUse",
"additionalContext": "..."}}` on stdout.

## Verification

Test the regression case explicitly — a command that *mentions* the target and *quotes* the
banned content must pass:

```bash
python guard.py <<'IN'
{"tool_name":"Bash","tool_input":{"command":"git commit -F- <<'EOF'\nUse `gh issue create`. Blocks \"do not revisit\" framing.\nEOF"}}
IN
# expect exit 0
```

Then confirm a genuine offender still exits `2`. Both directions, every time — a guard tested
only on true positives will over-block, and over-blocking gets the guard deleted.

## Example

Minimum test matrix for any Bash guard:

| Case | Expect |
| --- | --- |
| Real offending command | block (2) |
| Prose mentioning the command | pass (0) |
| Prose quoting the banned phrase | pass (0) |
| Compliant real command | pass (0) |
| Unrelated command | pass (0) |
| Read-only subcommand (`list`, `view`) | pass (0) |
| Banned phrase after a `;` inside quotes | pass (0) |
| Offending command after a `<<-` heredoc | block (2) |
| Malformed stdin | pass (0) |

## Notes

Open [gotchas.md](gotchas.md) when a Bash guard blocks its own install, a commit message, or a heredoc body. It records every observed block, including one where the input was not prose at all.

- **`git commit -F-` is the highest-risk input.** Commit messages describe commands and quote
  forbidden strings by design. If a guard is going to false-positive, it will be here.
- **Duplicating regexes across two guards is deliberate when they enforce one discipline** —
  but they drift. Note the sibling in a comment so a change to one prompts a change to both.
- The same trap applies to `Edit|Write` guards on documentation paths (the matcher is a
  regex on the tool name; checked 2026-10-05): a skill file *describing* an anti-pattern
  contains the anti-pattern verbatim.
- Prefer prose-tolerant detection over a suppression escape hatch. An `ACK=1` bypass gets
  used reflexively and the guard stops meaning anything.
