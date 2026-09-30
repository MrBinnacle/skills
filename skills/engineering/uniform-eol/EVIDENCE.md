# EVIDENCE — uniform-eol

Provenance record per the collection's evidence convention (see [CATALOG.md → "Evidence
records"](../../../CATALOG.md#evidence-records)). Fields are honest by construction: UNMEASURED
means exactly that.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-09-06, [gotchas.md](gotchas.md) first entry. A script applied six exact-string replacements to a 788-line `AGENTS.md` with `pathlib.Path.write_text()`, which on Windows translates LF to `os.linesep`. Every assertion passed, the hooks passed, the commit succeeded, and the diffstat read `810 insertions(+), 788 deletions(-)` for a six-line edit. |
| **Occasions counted** | 6 — 2026-09-06 whole-file rewrite caught only by a diffstat ([gotchas.md](gotchas.md)); 2026-09-07 nineteen URLs written with a trailing CR, every `curl` returning `000`, with no commit and so no diffstat ([gotchas.md](gotchas.md)); 2026-09-07 a state-file rotation wrote a uniformly-CRLF file as LF, 199 insertions against 199 deletions for a 15-line change; 2026-09-08 a rename script normalised four files to LF while repointing one reference each, 1,520 against 1,520 for a 53-line change; 2026-09-29 a repair script flipped a CRLF hook to LF, a 1,695-line diff ([gotchas.md](gotchas.md)); 2026-09-30 this collection's `refresh_dispatch_counts.py` rewrote fourteen LF records as CRLF, fixed in commit `ca82030` ([gotchas.md](gotchas.md)). Separate sessions and separate scripts; none is fan-out from another. |
| **Dispatches recorded** | No recorded dispatch, measured 2026-09-30. The card sat in `_quarantine/` until this release, so it was never installed and the counter had nothing to count. Not evidence about demand or worth. |
| **Validated against** | The six occurrences above. They bound what each diagnostic catches: the diffstat catches the cases that reach git, and only the write rule covers the 2026-09-07 URL case, which never did. A guard predicate of `crlf > 0 and lone_lf > 0` is blind to all six, because a uniform conversion is not mixed ([guard-design.md](guard-design.md)). Model in use was not recorded. |
| **Screen result** | UNMEASURED. Not screened. A Full-vs-Null screen fits poorly: the failure is a platform default, so the arms differ only when a task happens to route through a text-mode write. A deterministic fixture fits better (write a file both ways on Windows and compare byte counts), and none exists yet. |
| **Paired verdict** | UNMEASURED. Methodology for any future paired Full-vs-Null run: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md). No prior claimed either way. |
| **Standing cost** | Description: 49 tokens, measured by `skill-harness skill audit` (skill-harness 0.3.0, 2026-09-22). Body loads only on invocation. |
| **Re-screen trigger** | A Python release that changes the default newline translation on Windows, or a platform line-ending guard whose predicate catches a uniform conversion rather than only a mixed one. Either would subsume the card and retire it. Otherwise, record each new occurrence here; an occurrence the card's write rule would have prevented and did not is the falsifier. |

## Admission, answered against `admission-policy v1`

1. **Unaided failure exists.** Six observed occurrences, each by a frontier model working without this card, which was in `_quarantine/` and not installed.
2. **Recurs independently.** Six occasions across separate sessions and scripts between 2026-09-06 and 2026-09-30.
3. **A skill is the correct surface.** A line-ending hook exists in the maintainer's own setup, and it detects the conversion after the write. It is not available to a user of this collection, and it cannot see data that never reaches a watched path (the 2026-09-07 URL case). The card carries the write rule a hook cannot supply.
4. **Evidence supports admission and later retirement.** This record, and the re-screen trigger above.
