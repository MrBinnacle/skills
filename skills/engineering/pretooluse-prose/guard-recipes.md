# Guard recipes

Harness wiring for the rules in [SKILL.md](SKILL.md) → Solution. One section per harness. The rules are stable. The wiring, the pattern and the words of the refusal are yours to replace. Only Claude Code is covered below. Another harness needs its own name for the shell tool, its input channel, and its way to refuse a call.

## Claude Code `PreToolUse`

Checked 2026-11-12 against the live [hooks reference](https://code.claude.com/docs/en/hooks) and [tools reference](https://code.claude.com/docs/en/tools-reference).

- **Matcher: `Bash|PowerShell`.** The PowerShell tool passes its command in the same `tool_input.command` field as the Bash tool. The tools reference says: "Match `Bash|PowerShell` in hooks that inspect shell commands". A hook that matches only `Bash` never sees a PowerShell command.
- **Monitor commands arrive as Bash calls.** From v2.1.314, a hook with a `Bash` matcher also runs on shell commands that Claude starts with the Monitor tool. Its `allow` and `updatedInput` have no effect on them.
- **Exit codes.** `2` blocks the call, and stderr is the message the model reads. `0` raises no objection, so the normal permission flow applies. To warn without blocking, exit `0` and print `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "..."}}` on stdout.
- **Refusal text** (rule 5), written to stderr with exit `2`. For example: ``BLOCKED: this command contains `gh pr create`. If it only mentions it, write that text to a file with the file-write tool and pass the path, for example `git commit -F msg.txt`.``

Test the guard through its real input channel. This command only mentions the banned program, so under rule 3 it blocks, and the refusal must name the file route:

```bash
python guard.py <<'IN'
{"tool_name":"Bash","tool_input":{"command":"git commit -F- <<'EOF'\nUse `gh issue create`.\nEOF"}}
IN
# expect exit 2, and stderr names the file route
```

The file route must pass. Send `{"tool_name":"Bash","tool_input":{"command":"git commit -F msg.txt"}}` the same way and expect exit `0`. Then run every row of the matrix in SKILL.md → Example.
