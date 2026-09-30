# Why a mixed-EOL guard does not catch a uniform conversion

Read this when designing or auditing a line-ending guard, not when repairing a write.

A PostToolUse guard for line endings typically asks whether a file carries **both** separators:

```python
def is_mixed(crlf: int, lone_lf: int) -> bool:
    return crlf > 0 and lone_lf > 0
```

That is a sound test for a *stray* separator landing in a file — a single CRLF line pasted into an LF file, or the reverse. It is symmetric and needs no prior knowledge of the file's convention, which is why it gets written this way.

It cannot see a **uniform** conversion. After `write_text` rewrites an LF file, the counts are `crlf = 789, lone_lf = 0`. Not mixed. Not a finding. The guard passes the exact case where the diff damage is greatest.

Two independent gaps, and both need closing:

1. **Uniformity.** Add a comparison against what git has, not just an internal consistency check. `git show HEAD:<path>` gives the committed bytes; if the working file's dominant separator differs from the committed file's, that is a whole-file conversion whether or not it is mixed.
2. **Scope.** A hook rooted at the session's project directory — for example `REPO_ROOT = Path(__file__).resolve().parent.parent.parent` — returns nothing for a path outside it. If the session's real work lands in sibling repositories reached by absolute path, the guard is structurally blind to most of what the session writes. Measured 2026-09-06: a guard wired `PostToolUse` on `Write|Edit|Bash` saw none of a session's writes into two sibling repos.
