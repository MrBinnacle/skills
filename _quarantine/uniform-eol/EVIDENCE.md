# EVIDENCE — uniform-eol

Provenance record per the collection's evidence convention (see top-level README →
"Evidence records"). Fields are honest by construction: UNMEASURED means exactly that.

**This candidate is in `_quarantine/` and is not published.** Landing is not admission
(`LANDING.md`). This record exists so the occurrences are counted where they happened; it does
not assert the candidate has passed any gate. No section 1.5 review has been run.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-09-06, during a session that had landed this candidate an hour earlier. A script applied six exact-string replacements to a 788-line `AGENTS.md` using `pathlib.Path.write_text()`, which on Windows translates LF to `os.linesep`. Every replacement asserted its pattern occurred exactly once and every assertion passed; the script reported success; the pre-commit hooks passed; the commit succeeded. The diffstat read `810 insertions(+), 788 deletions(-)` for a six-line edit. Details: gotchas.md. |
| **Occasions counted** | 4 — 2026-09-06 whole-file rewrite caught only by a diffstat (gotchas.md); 2026-09-07 nineteen URLs written with a trailing CR, every `curl` returning `000`, no commit and therefore no diffstat to catch it (gotchas.md); 2026-09-07 a band rotation wrote `checkpoint.md` with `write_bytes` of a `"\n".join(...)`, converting a uniformly-CRLF file to LF and reading 199 insertions against 199 deletions for a 15-line change; 2026-09-08 the rename script for this very card normalised four files to LF while repointing one reference each, reading 1,520 insertions against 1,520 deletions across a 53-line change. |
| **Dispatches recorded** | 0. The candidate has never been installed or published, so the platform invocation counter has no row for it. Not a demand signal either way. |
| **Validated against** | The two occurrences above, which differ in failure surface and together bound what the card's stated diagnostic can catch. The 2026-09-06 case reaches git, so `git diff --numstat` catches it. The 2026-09-07 case never reaches git — scratch data consumed by another process — so the diffstat check cannot fire and the symptom surfaces as an unrelated-looking tool failure. A guard predicate of `crlf > 0 and lone_lf > 0` is blind to both, because a uniform conversion is not mixed. |
| **Screen result** | UNMEASURED. Not screened, and the Full-vs-Null protocol is a poor fit: the failure is a property of a platform API's default, not of agent judgement, so a bare arm and a treated arm differ only if the task happens to route through a text-mode write. A deterministic fixture is the better instrument — write a file both ways on Windows and assert the byte count — and no such fixture exists yet. |
| **Paired verdict** | UNMEASURED. Method for any future paired Full-vs-Null run: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md). No prior claimed either way. |
| **Standing cost** | Not installed, so nothing standing. Body 14.6 KB across five files (`SKILL.md`, `gotchas.md`, `guard-design.md`, `serializer-round-trip.md`, `LANDING.md`), which is above the ~7 KB authoring convention and would need splitting before any promotion. |
| **Re-screen trigger** | A Python release changing the default newline translation on Windows, or a platform EOL guard whose predicate catches a uniform conversion rather than a mixed one — either would subsume the card. Otherwise re-validate by recording each new occurrence here; an occurrence where the card's stated diagnostic would have caught the failure and did not is the falsifier. |

## Known gaps, stated rather than left to inference

- **The version history is unrecoverable.** `SKILL.md` carries `version: 1.1.0`, so the candidate
  was edited after it was first written while still untracked. That edit has no commit and no
  diff (`LANDING.md`).
- **The card's stated general rule is narrower than its own evidence.** The card leads with the
  diffstat diagnostic. The 2026-09-07 occurrence shows the rule that covers both cases is about
  the write, not the diff: use `write_bytes`, or pass an explicit `newline`, for any file another
  program will parse. Reconciling `SKILL.md` to that is outstanding work, not done here, because
  editing the card's substance is a section 1.5 matter.
- **No admission claim is made.** Four counted occurrences satisfy ADMISSION.md criterion 2's
  recurrence bar as counted, and satisfy nothing else.
- **Occurrence 4 was caused by the script that renamed this card.** On 2026-09-08 a rename pass
  rewrote 23 candidate directories and repointed one reference in each of several files. Its write
  step called `.replace("\r\n", "\n")` before encoding, so four files that were uniformly CRLF in
  the index were normalised to LF: three inside this collection's `frontend-slop` candidate and one
  published card's `gotchas.md`. The staged diff read 1,520 insertions against 1,520 deletions for
  what was a 53-line change. The author had written that guard deliberately, to stop the opposite
  error — introducing CRLF on Windows — which is precisely the failure this card names. Avoiding
  the wrong ending is not the same as matching the file's ending. Repaired by restoring CRLF on the
  four files; the diff then read 53 against 53.
