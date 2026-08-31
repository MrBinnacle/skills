---
name: pretooluse-bash-guard-prose-false-positive
description: A PreToolUse Bash guard reads the whole command string, so it blocks prose that only mentions what it forbids. Use when a hook blocks its own install, or when writing a Bash matcher.
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

## Solution

**1. Anchor detection to a command position.** A command starts at the beginning of the
string, or after a shell separator, optionally preceded by `VAR=value` assignments.

```python
_CMD_POS = r"(?:^|[;&|]{1,2}|\n|\$\()\s*(?:[A-Za-z_]\w*=\S*\s+)*"
CREATE_RE = re.compile(_CMD_POS + r"gh\s+(?:issue|pr)\s+create\b", re.IGNORECASE)
```

**2. Split the heredoc body from the shell before deciding anything.** The body is the
artifact; the shell is the invocation. Detect commands in the shell part, inspect content in
the body part.

```python
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)(\w+)\1\s*\n(.*?)(?:^\2$|\Z)",
                        re.DOTALL | re.MULTILINE)

def split_shell_and_body(cmd):
    bodies = []
    shell = HEREDOC_RE.sub(lambda m: (bodies.append(m.group(3)), "<<HEREDOC>>")[1], cmd)
    for m in re.finditer(r"--body(?:-file)?[= ]\s*(['\"])(.*?)\1", shell, re.DOTALL):
        bodies.append(m.group(2))
    return shell, "\n".join(bodies) if bodies else shell
```

**3. Fail open on every internal error.** A guard must never be the reason work stops.

```python
except Exception:
    return 0
```

**4. Exit codes.** `2` blocks with stderr shown to the model; `0` proceeds. To warn without
blocking, exit `0` and print `{"hookSpecificOutput": {"hookEventName": "PreToolUse",
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
| Malformed stdin | pass (0) |

## Notes

- **`git commit -F-` is the highest-risk input.** Commit messages describe commands and quote
  forbidden strings by design. If a guard is going to false-positive, it will be here.
- **Duplicating regexes across two guards is deliberate when they enforce one discipline** —
  but they drift. Note the sibling in a comment so a change to one prompts a change to both.
- The same trap applies to `Edit|Write` guards on documentation paths: a skill file
  *describing* an anti-pattern contains the anti-pattern verbatim.
- Prefer prose-tolerant detection over a suppression escape hatch. An `ACK=1` bypass gets
  used reflexively and the guard stops meaning anything.
