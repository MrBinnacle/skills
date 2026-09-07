# gotchas.md — self-documenting-code

Append-only log of observed and anticipated failure modes.

## [ANTICIPATED] 2026-09-06 — Canonical copy not fully verified at landing

Issue #216 required hashing the maintainer's local install against registry package SHA-256
`2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9` before choosing a
canonical copy. The local install was not available in the landing environment; only the
public GitHub `SKILL.md` (SHA-256 `132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885`)
was. Package digest and file digest are different artifact kinds. Re-run the three-way
comparison when the local install is reachable; do not treat this landing as proof the
registry package and the public file agree.

## [ANTICIPATED] 2026-09-06 — No EVIDENCE.md, no occurrences counted

The card carries zero counted occurrences. Against ADMISSION.md it fails criterion 1 (no
observed unaided failure), criterion 2 (no occasions counted), and criterion 4 (no
EVIDENCE.md). Three of four. The card is not admissible today.

## [ANTICIPATED] 2026-09-06 — No eval fixtures

The registry notes the current evals contain no fixture files. Without executable contrasting
fixtures the card cannot be screened. The ceiling is fixed regardless of treatment quality.

## [ANTICIPATED] 2026-09-06 — External registry validator not updated in-tree

Issue #216 asked to add `gotchas.md` and update the registry's bundled `validate_package.py`
allow-list in the same change. That script is not in this repository and not in the public
source tree that supplied `SKILL.md`. `gotchas.md` was added anyway for this collection's
discipline. When the external registry validator is reachable, extend its allow-list and
close this entry.

## [OBSERVED] 2026-09-06 — Landing attempt rewrote the frozen description

An implement pass rewrote `description` from the upstream
`A guide for writing self-documenting code` (43 characters) to a longer router string, and
documented the original as "285 characters" (that figure belongs to a different candidate,
`anti-slop-frontend-secure`). Issue #216 criterion 5 forbids rewriting the baseline while
landing it. Restored byte-identical to upstream; keep the freeze on any later edit that is
not an explicit version bump.

---

## Entries added with the 0.2.0 candidate

## 2026-08-17 - Test helpers can certify the wrong thing

Failure behavior exposed two loose comparison helpers. A list could compare
equal to a string.

Executable examples exposed a section assertion whose pattern ran beyond the
section's end. An item in a later section satisfied the test.

The assessment model covered test code. Neither problem required a
production-only review.

## 2026-08-17 - No question can mean no edit

The rule "write the question before the correction" stopped two proposed edits:
renaming a short local CLI helper and splitting a 50-line linear orchestration
function.

The agent could not name a reader question either edit answered. The report
records prevention, not a run where those edits shipped without the card.

## 2026-08-17 - Comments held the governing authority

Most comments cited architecture decisions or specifications and included
incident history. The repository kept decisions frozen and superseded them
rather than editing them.

The six comment classes and the false-positive list protected those records.
The report does not record a comment-stripping incident. It records the card
preventing that loss.

## 2026-08-17 - A real finding needed a decision, not an edit

A resource skipped by design received a status whose documented remedy could
not help. Fixing the mismatch needed an architecture decision.

The agent used a local evidence record because the priority ladder had no clear
place for this case. The compatibility gate also kept two frozen primary-source
files out of scope.

## 2026-08-17 - An empty diff left scope unresolved

The pass began just after a commit. No file was named. The fallback to the
"smallest relevant module" gave the agent nothing to select.

The agent improvised by using the last commit. The later whole-project scope
came from the user.

## 2026-08-17 - A review arrived during an open slice

A background review returned while clarity edits were underway. Three findings
touched code being edited. Two shared a root cause with logged findings.

The agent merged the work by hand, with correctness first. The baseline card
had no re-entry step.

## 2026-08-17 - Assertion totals describe two stages

The immediate harness swap kept 52 + 73 assertions, with zero failures.
The full pass ended with 53 + 92, also with zero failures.

These are not one before-and-after pair. The report separately records
byte-identical live end-to-end output. It does not establish stability for
every possible input.

## [OBSERVED] 2026-09-06 — The canonical-copy comparison resolved, and the copies differ

The `[ANTICIPATED]` entry above asked for the three-way comparison to be re-run when the
maintainer's local install became reachable. It was run on the maintainer's host on 2026-09-06.

| Copy | `SKILL.md` SHA-256 | Files |
|---|---|---|
| Landed here, from the public source | `132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885` | 3 |
| Maintainer local install | `34c408a94562429dd683b8be4701d91dd5ff0ffaf3c04549c27437857b7caf18` | 14 |

Both are single-file digests of `SKILL.md`, so this is a like-for-like comparison and the
inequality is content drift rather than an artifact of comparing a package digest against a file
digest. The landed file is 6,018 bytes; the local install's is 6,191 bytes.

**The baseline frozen in this repository is not the copy the maintainer runs.** Eleven files of
the installed package never landed, including the field report that is the card's only record of
running on real code, both eval files, and `scripts/validate_package.py` — which the landing
`PROVENANCE.md` states does not exist in any tree.

Recorded as `skills#233`. The general form, which is the part worth carrying: a build agent
running in an isolated container reported files absent when they were merely out of reach, and
that report entered the record as a property of the artifact rather than of the container. A
claim of absence must name the search that established it.


## [OBSERVED] 2026-09-06 — The missing-file count was wrong: thirteen, not eleven

The entry above says eleven files never landed. `skills#233` says eleven too, and then lists
thirteen in the same body. Thirteen is right.

The wrong number came from one subtraction: fourteen files in the local install, minus three files
in this repository. That assumed the three repository files also sat in the local install. Only
`SKILL.md` did. `PROVENANCE.md`, `gotchas.md` and `EVIDENCE.md` exist only here, so nothing was
subtracted for them.

The shape worth carrying: a count taken by subtracting two sets is only as good as the assumption
that one set contains the other. Check the overlap before you subtract, or count the difference
directly.

## [OBSERVED] 2026-09-06 — The landed baseline was never a version of the maintainer's card

The entry above records that the two `SKILL.md` files differ. It did not say how. We read both on
2026-09-06.

The public file is an essay: 6,018 bytes, five headed sections, no version in its frontmatter, no
links to any other file. The local file is a procedure: 6,191 bytes, seven numbered steps, a
disclosure map, `metadata.version: "0.1.0"` in its frontmatter, and nine links that all resolve to
files sitting beside it.

They share a name and almost no text. This was never drift between two releases of one document.

The local install is the canonical 0.1.0 package. It says so itself, its links resolve, and every
file in it carries one install timestamp with nothing edited afterwards. `#216` landed the public
essay and recorded it as the frozen 0.1.0 baseline. It was a different document that shared a name.

The shape worth carrying: two files with the same name and different digests look like two versions
of one thing, and the digest alone cannot tell you otherwise. Open both before you call it drift.

## [OBSERVED] 2026-09-06 — The evals hold no code fixtures, and twenty labelled trigger rows

The `[ANTICIPATED]` entry above repeats the registry's claim that the evals contain no fixture
files, and concludes the card cannot be screened. Both eval files were read first-hand on
2026-09-06, from this repository, for the first time.

The claim is half right. `evals/evals.json` holds five cases and every one carries `"files": []`.
There is no code for a run to act on, so nothing can measure what the card does to code.

`evals/trigger-evals.json` holds twenty labelled queries: ten `should_trigger: true` and ten
`false`. The negative rows name near neighbours the card should decline. That is a contrasting
fixture set, it needs no code, and it can run today.

So the ceiling covers efficacy and not triggering. Those are two claims and the entry above merged
them.

The shape worth carrying: a second-hand claim about a file is a claim about whoever read it. Open
the file before you build a conclusion on top.

## [OBSERVED] 2026-09-06 — `validate_package.py` exists, and it cannot pass in a flat layout

The `[ANTICIPATED]` entry above asks for the registry validator's allow-list to be extended when
the script becomes reachable. The script was never unreachable in the way that entry assumed. It
sat on the maintainer's host at `scripts/validate_package.py`, 3,464 bytes. It is now in this
directory and `gotchas.md` is in its `ALLOWED_TOP_LEVEL`. That closes `#216` task 4.

It still exits non-zero here, and the reason is not the allow-list. The script validates the
upstream nested layout: it expects `references/`, `assets/` and `scripts/`, and it checks that
`scripts/snapshot.py` exists. This repository's card layout is flat, so the script reports twelve
flattened files as unexpected and reports `scripts/snapshot.py` missing. Both errors describe the
layout, not the card.

The shape worth carrying: a validator shipped inside a package encodes that package's layout. Move
the package and the validator becomes a test of the move.

## [OBSERVED] 2026-09-06 — A filename carried residue the gate could not see

The field report arrived as `FIELD-REPORT-2026-08-17-<private-repo-name>.md`. The last part of that name
is the maintainer's private repository.

The de-personalization gate did not catch it, and would not have. Its hooks are content greps over
`.md` files: they read what is inside a file and never read the name of it. This name also used a
hyphen where the banned term uses an underscore, so even a filename-aware grep with that pattern
would have passed it.

The file landed as `FIELD-REPORT-2026-08-17.md`. Its line 3 named the same repository inside the
content, and that occurrence the gate would have caught; it was replaced with the same generic
phrase `500ac26` used across five files.

The shape worth carrying: a residue check that reads only file contents cannot see a path. Scan the
names as well as the bytes, and remember that a name often spells a term differently from the way
the code inside spells it.
