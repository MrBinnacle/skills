---
name: uniform-eol
description: Use before a script rewrites a file on Windows, when a small edit's diffstat is near the file's line count, or when every item of a batch read from a written file fails.
---

# uniform-eol: a text-mode write converts every line ending and reports success

## Problem

On Windows, Python's text-mode write turns every `\n` into `\r\n`. A script that reads a file, changes five lines and writes it back converts the whole file. Nothing errors. The assertions pass, the hooks pass, the commit succeeds.

Two things then go wrong. In a repository, git sees every line as changed, so the five real edits hide inside a whole-file diff and ship unreviewed while looking reviewed. In data another program parses, each line now carries a trailing `\r`, and the consumer fails for a reason it cannot name: a URL that never resolves, a token that never matches.

## Trigger conditions

- A script is about to write a file with `pathlib.Path.write_text(s)` or `open(path, "w")` on Windows. Both default to `newline=None`, which translates `\n` to `os.linesep` on write. `read_text()` does the reverse, so the read-modify-write round trip converts the file under the documented contract.
- A diffstat's insertions and deletions each sit near the file's line count after an edit that touched a handful of lines.
- Every item of a batch fails the same way, and the batch was read from a file a script wrote: `curl` returning `000` on every URL, a lookup missing on every key.
- A line-ending guard is installed and did not fire. See [`guard-design.md`](guard-design.md) for why it usually cannot.

## Solution

**The rule is the write.** When a script rewrites an existing file, or writes a file another program will parse, keep the file's line ending by construction:

```python
# Converts LF to CRLF on Windows:
path.write_text(text, encoding="utf-8")

# Keeps whatever ending the file had:
with open(path, encoding="utf-8", newline="") as f:
    text = f.read()
path.write_text(text, encoding="utf-8", newline="")  # newline= needs Python 3.10+

# Or stay in bytes throughout:
data = path.read_bytes()
path.write_bytes(data.replace(old, new))
```

`newline=""` turns translation off in both directions. Reading with `newline=""` matters too: a regex anchored with `$` then sees `\r` before each `\n`, so allow `\r?` in patterns that match at line end.

**The diffstat is the backstop, for the file that reaches git:**

```bash
git diff --stat
```

If the numbers are wrong, rewrite the file in its original ending with the byte form above. Before a push, amend. After a push, commit the repair on top.

**For data that never reaches git, run one control.** Take one item out of the failing batch and use it directly, typed into the command. If it works there, the fault is in the file your script wrote, not in the items.

## Verification

Count both separators in the working file and in what git holds, and check they agree:

```bash
eol() { python -c "
import sys; b=open(sys.argv[1],'rb').read() if len(sys.argv)>1 else sys.stdin.buffer.read()
crlf=b.count(b'\r\n'); print('CRLF:',crlf,' bare LF:',b.count(b'\n')-crlf)" "$@"; }

eol path/to/file
git show HEAD:path/to/file | eol
```

Then confirm the diffstat matches the size of the edit you intended.

## Related mechanism

Re-serializing a JSON, YAML or TOML file to change one string reformats the whole document. The diffstat separates the two causes: an EOL conversion gives insertions equal to deletions equal to the line count, while a re-serialization moves the line count itself. Read [`serializer-round-trip.md`](serializer-round-trip.md) when the two numbers differ.

## Notes

- `.gitattributes` with `* text=auto eol=lf` normalises what git stores. It leaves the working tree converted and does nothing for data outside git, so the write rule still applies.
- Keep the diff readable. Telling git to ignore whitespace hides the symptom and leaves the next reviewer the same unreadable diff.
- Dated occurrences, including one where a repair script caused the failure it was guarding against, are in [`gotchas.md`](gotchas.md); the count and the retirement trigger are in [`EVIDENCE.md`](EVIDENCE.md).

## References

- Python `open()` and its `newline` parameter: https://docs.python.org/3/library/functions.html#open
- `pathlib.Path.write_text` and `read_text`, which pass `newline` through to `open()` (`write_text` takes `newline` since Python 3.10; checked against the CPython 3.13.9 docs through Context7 on 2026-09-30): https://docs.python.org/3/library/pathlib.html#pathlib.Path.write_text
- `gitattributes`, `text` and `eol`: https://git-scm.com/docs/gitattributes
