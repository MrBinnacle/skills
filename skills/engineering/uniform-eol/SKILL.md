---
name: uniform-eol
description: Use when a small edit produces a diffstat near the file's whole line count, or before writing a file with write_text on Windows. A uniform EOL conversion is invisible to a mixed-endings guard.
author: Claude Code
version: 1.1.0
date: 2026-09-07
---

# A uniform EOL rewrite hides the change and passes the mixed-EOL guard

## Problem

A script makes five targeted edits to a document. The commit reports 810 insertions and 788 deletions on a 788-line file. Nothing is wrong with the edits. The write converted every line ending from LF to CRLF, so git sees every line as changed.

Two costs, and the second is worse than the first. The file's line endings are now wrong. And the five real edits are invisible — no reviewer can find them inside a whole-file diff, so the change ships unreviewed while looking reviewed.

## Context / Trigger conditions

- A diffstat's insertions and deletions are each near the file's total line count, after an edit you know touched a handful of lines.
- A Python script wrote the file with `pathlib.Path.write_text(s)` or `open(path, "w").write(s)`. Both default to `newline=None`, which on write translates every `\n` to `os.linesep` — `\r\n` on Windows. Reading with `read_text()` does the reverse, so a read-modify-write round trip converts a whole file with no error and no warning.
- The repository stores LF, which is the common case, so the conversion is total rather than partial.
- A mixed-EOL guard is installed and did not fire.
- The write went into a sibling repository by absolute path, and the hook is scoped to the session's own project directory.

## Solution

**Write bytes, not text, whenever you are rewriting an existing file.**

```python
# Wrong on Windows: read_text/write_text round trip converts LF -> CRLF
t = path.read_text(encoding="utf-8")
path.write_text(t, encoding="utf-8")

# Right: read_text is fine (universal newlines gives you \n),
# but write the bytes verbatim so nothing is translated.
t = path.read_text(encoding="utf-8")
path.write_bytes(t.encode("utf-8"))

# Also right, if you want to stay in text mode:
path.write_text(t, encoding="utf-8", newline="")
```

`newline=""` disables translation on write. `write_bytes` never had it.

**Then check the diffstat before you trust the commit.** The commit succeeds either way; only the diffstat tells you what happened.

```bash
git diff --stat origin/main...HEAD
```

If the number is wrong, repair with the same `write_bytes` form above, then `git add` and
`git commit --amend`.

## The installed guard probably will not catch this

A line-ending guard usually asks whether a file carries **both** separators — `crlf > 0 and lone_lf > 0`. That is a sound test for a *stray* separator and it is blind to a *uniform* conversion, where the counts are `crlf = 789, lone_lf = 0`. Not mixed, not a finding, and it is the case where the diff damage is greatest.

A repo-scoped hook adds a second blind spot: rooted at the session's project directory, it returns nothing for a write into a sibling repository reached by absolute path.

Both gaps, and how to close them, are in [`guard-design.md`](guard-design.md). Read it before trusting a guard to cover this.

## Verification

Confirm the file, not the intention. Count both separators in the working file and in what the repository holds, and check they agree on which one dominates:

```bash
eol() { python -c "
import sys; b=open(sys.argv[1],'rb').read() if len(sys.argv)>1 else sys.stdin.buffer.read()
crlf=b.count(b'\r\n'); print('CRLF:',crlf,' bare LF:',b.count(b'\n')-crlf)" "$@"; }

eol path/to/file                       # working tree
git show origin/main:path/to/file | eol   # what git holds
```

Then confirm the diffstat matches the size of the edit you intended.

## Example

Observed 2026-09-06. A script applied six exact-string replacements to a 788-line `AGENTS.md`, each guarded by an assertion that the pattern occurred exactly once. Every assertion passed. The edits were correct.

The commit reported `2 files changed, 810 insertions(+), 788 deletions(-)`.

Measurement:

```
working file : CRLF 789, bare LF 0
origin/main  : CRLF 0,   bare LF 788
```

The script ended with `p.write_text(t, encoding="utf-8")`. Fixed with `p.write_bytes(t.encode("utf-8"))` and `git commit --amend`. The diffstat became `AGENTS.md | 11 ++++++-----`, which is the real change: five replacements and one insertion.

The installed mixed-EOL guard did not fire, for both reasons above: the conversion was uniform, and the file was in a sibling repository outside the guard's root.

## The other mechanism with this signature

Re-serializing a JSON, YAML or TOML file to change one string reformats the whole document
under the serializer's own defaults. Same unreviewable diff, different cause, and the
diffstat separates them: an EOL conversion gives insertions == deletions == the line count,
while a round-trip moves the line count itself. Read
[`serializer-round-trip.md`](serializer-round-trip.md) when the two numbers differ.

## Notes

- **The diffstat is the detector, and it is free.** One command after every scripted edit catches this class. A commit that succeeds tells you nothing about what it contains.
- **`.gitattributes` with `* text=auto eol=lf` normalises on commit.** Worth having, and not a substitute for the check: it fixes what lands in git while leaving the working tree converted, and not every repository has it.
- **Do not "fix" this by telling git to ignore whitespace in diffs.** That hides the symptom and leaves the next reviewer the same unreadable diff.
- A write-side sibling of the read-side trap where a bounded read establishes a confident absence: both trust an operation's success instead of measuring its effect.
- See also: `write-site` for the general habit of putting the check where the write happens.

## References

- Python `open()` and the `newline` parameter, which governs translation in both directions: https://docs.python.org/3/library/functions.html#open
- `pathlib.Path.write_text` / `read_text`, which pass `newline` through to `open()`: https://docs.python.org/3/library/pathlib.html#pathlib.Path.write_text
- `gitattributes`, `text` and `eol` for commit-time normalisation: https://git-scm.com/docs/gitattributes
