# Disposition record — S432 admission re-test of the quarantine candidates that carry evidence

Date: 2026-09-08. Source session: S432 of the maintainer's private research notebook, opened on
the adjudication tier for this question by the maintainer's own instruction.

Method: every candidate in `_quarantine/` that carries an `EVIDENCE.md` was re-tested against
[admission-policy v1](../ADMISSION.md), one criterion at a time, from the candidate's own record
and from the environment the failures happened in, measured at source on the day of this record.
Criterion 3 was answered with the rubric in [`AGENTS.md` → Choosing the control
surface](../AGENTS.md#choosing-the-control-surface). The draft was then sent to a two-family
cross-model challenge review, and two of its claims were withdrawn on that review; the section
"What the review changed" says which. Nothing here is a count of the directory; read the directory.

## Verdicts

| Candidate | Criterion 1: unaided failure | Criterion 2: independent recurrence | Criterion 3: control surface | Criterion 4: evidence for entry and exit | Disposition |
|---|---|---|---|---|---|
| `frontend-slop` | ABSENT. Its record dates the card's materialisation, not an occurrence. | 0 counted. | Not reached. | Not reached. | **NOT ADMITTED.** Unchanged from the record it already carries. |
| `self-documenting-code` | ABSENT. Its record states the deciding words: the edits were prevented, not observed happening without the card. | ABSENT. The n = 1 in its report is an assisted session. | Not reached. | Not reached. | **NOT ADMITTED.** Unchanged from the record it already carries. |
| `uniform-eol` | OBSERVED, four times, 2026-09-06 to 2026-09-08. | 4 counted, dated, in four different scripts across three repositories; four separate runs, so not fan-out. One operator, one host, three days — a cluster reading is possible and is stated, not resolved. **Clears as counted.** | **Not decidable from the record as it stands.** Enforcement is the working hypothesis; the deciding observation is named below and has not been made. | The record names its own retirement trigger: a guard whose predicate catches a uniform conversion. That guard is specified and unbuilt. | **DEFERRED, dated, with a named re-test.** Stays in `_quarantine/`. |

No card is admitted by this record. No card is cut by it.

## Why `uniform-eol` is deferred rather than admitted

**The failure.** On Windows, `pathlib.Path.write_text()` and `open(path, "w")` default to
`newline=None` and translate every `\n` to `\r\n`. A read-modify-write of an LF file converts the
whole file. The write reports success, the commit succeeds, and the diff is unreadable. The remedy
is one line: `write_bytes`, or `newline=""`.

**The rule that decides it, and it needs no rubric.** The candidate's `Re-screen trigger` row
reads: "a platform EOL guard whose predicate catches a uniform conversion rather than a mixed one …
would subsume the card." The repair that produces that guard is specified in the candidate's own
`guard-design.md`, is small, and is in the maintainer's hands
(research notebook, ticket #190). Publishing the card now would hand strangers a retrieval prompt
while the maintainer holds the interlock the card itself says makes it redundant. That is the
whole reason for the deferral, and it stands on the candidate's own words.

**What the environment measured during the four occurrences, stated at its actual strength.**

1. A `PostToolUse` hook, `crlf-write-guard.py`, was wired on `Write|Edit|Bash` in the research head
   throughout and reported nothing on any of the four. The candidate's `guard-design.md` gives
   both reasons: the predicate `crlf > 0 and lone_lf > 0` cannot see a uniform conversion, and the
   hook is rooted at its own project directory, so a write into a sibling repository is never
   inspected. This is evidence that the installed guard is wrong. It is not evidence about which
   layer is right.
2. A private card, `windows-claude-code-env`, installed in the maintainer's `~/.claude/skills/`
   and not part of this collection, names "CRLF/LF (writing, …)" in its description and states
   this exact mechanism at line 319 of its `SKILL.md`. It was not retrieved before any of the four
   writes. This is evidence that a large card carrying the mechanism among many others was not
   retrieved. **It is not a measurement of whether `uniform-eol`, with its own description, would
   be retrieved.** The first draft of this record wrote "retrieval-based control on this failure,
   measured: 0 of 4" and that sentence is withdrawn; the trial it describes has not been run.

Both controls scored zero. That is compatible with enforcement being the right layer and the hook
being buggy, with retrieval being the right layer and the wrong text being installed, and with
neither control sitting in the path of a three-day scripted-edit run. The rubric's authoring rule —
a discipline you depend on needs a hook — is a reason to build the guard first. It is not a
measurement, and this record does not cite it as one.

**A third surface the first draft did not consider.** The standard control for this class is the
version-control layer: a `.gitattributes` `eol` declaration, or a pre-commit check that a file's
dominant separator matches what `HEAD` holds. Neither depends on the agent harness, and the second
would have caught occurrences 1, 3 and 4 in any tool. This collection's own `.gitattributes`
declares `eol` for two path patterns only, and both public repositories hold files that are
uniformly CRLF on purpose, so a blanket `eol=lf` is not available; the `HEAD`-comparison check is.
`#190` carries it as an alternative to, or a second seat beside, the `PostToolUse` repair. The
rubric row for that shape is `SCRIPT_OR_CHECK`, and it competes with `HOOK_ENFORCEMENT` for the
same failure.

**What the guard cannot reach, stated so it is not lost.** Occurrence 2 (2026-09-07) wrote nineteen
URLs to a scratch file that was never staged, and every `curl` then returned `000`. A guard that
finds Bash-touched files through `git status`, and a pre-commit check, are both blind to a file git
never sees. That is the residual a card-shaped habit covers. It is one occurrence today. This
record does not re-attribute the other three to a guard that does not exist yet; the count stays
at four until a built guard is observed catching the class.

## What would admit it, and when to re-test

1. **Build the guard** (research notebook, ticket #190): compare the working file's dominant separator
   against `git show HEAD:<path>`, resolve the repository root from the written path, and add
   occurrences 1 and 4 as poison fixtures that go red against the current guard and green after.
   Decide there whether the check also runs at pre-commit.
2. **Observe, do not wait a release cycle.** Over the next scripted writes on Windows into the
   sibling repositories, plus at least one deliberate unstaged scratch write:
   - the guard catches every git-visible uniform conversion and misses only git-invisible ones →
     enforcement is the layer; the card stays quarantined until two git-invisible occurrences
     are counted, and then is rebuilt in the `pull-rebase` shape, where the card prescribes its
     guard and carries the in-flight byte check as the backstop;
   - a git-visible uniform conversion still lands with the guard live → criterion 3 reopens, and
     "guard first" was incomplete or wrong.
3. **Run the retrieval trial this record did not run.** Install this candidate's description alone
   (no `windows-claude-code-env` alongside) and record whether it is retrieved before the next
   Windows `write_text`. That is the measurement the withdrawn "0 of 4" sentence stood in for.

Whichever branch is reached, the card's substance (14.6 KB across five files against a 7,168-byte
`SKILL.md` ceiling) is a section 1.5 change and is not made here.

## What the review changed

Two seats from two model families reviewed the first draft under the calibrated
claim-adjudication brief. Both returned PARTLY SOUND. They converged on the same two objections,
and both are accepted here:

- **"Retrieval measured 0 of 4" was measured on a different card.** Withdrawn, as above.
- **Both controls failing does not identify the layer; the draft read the rubric's rule as a
  measurement.** Withdrawn. Criterion 3 is now recorded as not yet decidable, with enforcement as
  the hypothesis and the deciding observation named.

One seat added two points the other did not raise, and both are taken: the version-control layer
as a candidate surface (now in the record and on `#190`), and the prospective re-attribution of
past occurrences to an unbuilt guard as accounting rather than measurement (removed; the count
stays at four). One seat proposed the retrieval trial in step 3.

Neither seat could refute "do not publish the card while the maintainer holds the repair its own
record says subsumes it." That is the sentence the disposition rests on.

## A routing note on the private card

`windows-claude-code-env` and this candidate share a trigger. The rubric names a second identity
for an existing trigger surface as a routing defect. That card is outside this collection, so the
collection has no collision today. If `uniform-eol` is ever admitted, the private card's Problem 9
should point at it or give up that section, and the maintainer should decide which. Recorded so the
choice is made on purpose when it comes due.

## Observation log — step 2, open

Step 1 of "What would admit it, and when to re-test" is complete. The guard is built and merged.
It compares the working file's dominant separator against the bytes git would check out, and it
resolves the repository from the written path. Step 2 is the observation window, and it is open,
not concluded. Each entry below is one observation with the instrument that produced it.

| Date | Observation | Instrument | Result |
|---|---|---|---|
| 2026-09-08 | Deliberate scratch write into this repository: a tracked, uniformly-CRLF file converted to LF the way occurrence 4's normaliser did. | `git diff --numstat` after the write; the guard run with a real `PostToolUse` payload. | **Caught.** The diffstat read 53 / 53 for a zero-content change, which is occurrence 4's signature. The guard named the file and the direction, `CRLF -> LF`. The file was restored byte-identical and the tree left clean. |

**One observation is not the branch condition.** The record asks whether the guard catches *every*
git-visible uniform conversion over the next scripted writes. One deliberate probe in the "caught"
direction does not settle that, and criterion 3 stays exactly where this record put it: not
decidable, with enforcement as the hypothesis. This candidate stays in `_quarantine/`. No verdict
in the table above is changed by this section.

Three defects were found in the guard during the build. They are recorded here because they bear on
what the observation can be trusted to mean. The first draft compared against the stored blob,
which under `core.autocrlf=true` would have reported every honest write to every tracked text file
as a conversion; the reference is now `git cat-file --filters`. The second draft repaired only the
lane that receives a file path, leaving the lane that receives a shell command — the lane
occurrence 4 itself arrived on — still single-repository. The third read quoted porcelain paths, so
a file with a non-ASCII name was skipped in silence. Each has a fixture, and six hand-run mutations
establish which fixture holds which line. Build record: research notebook ticket `#190`.

*Revisit if:* a git-visible uniform conversion lands with the guard live. That reopens criterion 3
and is adjudication-class.

## Links

- The four occurrences, dated: [`_quarantine/uniform-eol/EVIDENCE.md`](../_quarantine/uniform-eol/EVIDENCE.md)
- The guard diagnosis and repair: [`_quarantine/uniform-eol/guard-design.md`](../_quarantine/uniform-eol/guard-design.md)
- The guard repair ticket: research notebook, ticket #190
- The measurement this record was made from: research notebook, `docs/audit/from-zero-S432.md`, rows 37 and 38
- The cross-family review receipt: research notebook, `docs/audit/t1-uniform-eol-S432/`
- The precedent record for this method: [`2026-08-15-S295-admission-triage.md`](2026-08-15-S295-admission-triage.md)
