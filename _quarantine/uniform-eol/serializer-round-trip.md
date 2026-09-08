# The second mechanism with the same signature: a serializer round-trip

Reached from `SKILL.md`. Read it when a targeted edit produced a whole-file diff and
the insertion and deletion counts are NOT equal.

Observed 2026-09-07, in the same class of task and caught by the same detector. A script
added one sentence to one string field in a 214-line `assets/tokens.json`:

```python
d = json.loads(p.read_text(encoding="utf-8"))
d["copy"]["words_to_avoid_scope"] += addition
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
```

The diffstat: `312 insertions(+), 214 deletions(-)`.

**The insertions and deletions are unequal, and that is the tell.** An EOL conversion
rewrites every line and leaves the two numbers identical to the file's line count. A
structural round-trip re-indents, re-escapes and re-wraps, so the line count itself moves.
Two mechanisms, one signature, distinguishable by arithmetic alone:

| Diffstat shape | Mechanism |
|---|---|
| `N insertions, N deletions`, N == file line count | line endings converted |
| insertions != deletions, both near the line count | serializer round-trip |
| both, in one commit | a text-mode write of a re-serialized document |

`json.dumps` is not a formatter for the file it read. It applies **its own** `indent`,
`separators`, key order, and — the one that bites hardest — `ensure_ascii`, which decides
whether every non-ASCII character is stored raw or as `\uXXXX`. Nothing in the read tells
it what the file used, so the defaults win. `yaml.safe_dump`, `tomlkit.dumps` used without
its round-trip API, and any XML pretty-printer behave the same way.

The fix is the same as the EOL fix and for the same reason: **do not re-serialize a document
in order to change a string inside it.** Operate on the bytes, and assert the match count so
the edit still cannot land silently:

```python
b = p.read_bytes()
assert b.count(old) == 1
p.write_bytes(b.replace(old, new))
```

Diffstat after: `1 insertion(+), 1 deletion(-)`. Validate the result parses
(`json.load`) as a separate step — the byte edit does not check syntax, and that is the one
thing the round-trip did give you for free.

