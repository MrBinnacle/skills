# PROVENANCE.md — self-documenting-code 0.1.0

**Date landed:** 2026-09-06
**Source:** Public theswerd/aicode repository, `skills/self-documenting-code/SKILL.md`
**Source SHA-256 (SKILL.md):** `132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885`
**Registry package SHA-256 (recorded on issue #216):** `2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9`
**GitHub repo:** https://github.com/theswerd/aicode
**skills.sh listing:** https://skills.sh/theswerd/aicode/self-documenting-code

## Canonical-copy check

Issue #216 requires hashing the maintainer's local install against the registry package
SHA-256 before landing, and recording divergence rather than silently picking a copy.

| Copy | Accessible here | SHA-256 |
|---|---|---|
| Registry package (tarball, per issue body) | Hash only — package bytes not in this container | `2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9` |
| Maintainer local install | Not mounted in this disposable container | unknown |
| Public GitHub `SKILL.md` (landed) | Yes | `132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885` |

The registry figure is a **package** digest; the landed figure is a **single-file** digest.
They name different artifacts, so inequality alone does not prove content drift. The local
install that would close the comparison was not available. **Divergence between the three
copies was not resolved** — it is recorded as an open finding. The public GitHub file is
what was landable; it is frozen byte-identical to upstream `main` at land time.

## What was landed

`SKILL.md` is the frozen 0.1.0 baseline: **no rewrite**. Frontmatter and body match the
public source byte-for-byte. Frontmatter is:

```yaml
name: self-documenting-code
description: A guide for writing self-documenting code
```

Description length is 43 characters (already under the published 200-character bar). No
frontmatter normalization was applied on this landing — that step belongs to promotion, not
to freezing the baseline (issue #216 criterion 5; `AGENTS.md` step 2a is a promotion pass).

## Files added

- `SKILL.md` — frozen 0.1.0 baseline (byte-identical to public source)
- `PROVENANCE.md` — this file
- `gotchas.md` — append-only log, seeded with anticipated gotchas

## `validate_package.py`

Issue #216 also asks to update the registry's bundled `validate_package.py` allow-list so
`gotchas.md` is accepted. That script is **not present in this repository** and is not part
of the public theswerd/aicode tree (only `SKILL.md` exists under the skill path). No in-tree
path can satisfy that half of criterion 4; the gap is recorded in `gotchas.md`. This repo's
`scripts/validate_card_files.py` gates published cards under `skills/`, not `_quarantine/`.

## What this landing does not do

- Does not publish. The candidate fails ADMISSION.md criteria 1, 2, and 4.
- Does not build 0.2.0-rc.1. That is separate work.
- Does not add a second skill identity.

---

## Correction, 2026-09-06 — we ran the check this file left open. Two things above are wrong.

When this card was landed, the build could not reach the maintainer's machine. So it could not
compare the copy it was landing against the copy actually in use. It said so, and left the
question open.

We ran that comparison on 2026-09-06. Here is the result.

| Copy | `SKILL.md` fingerprint | Number of files |
|---|---|---|
| The one landed here, taken from the public source | `132dc292…` | 3 |
| The one on the maintainer's machine | `34c408a9…` | 14 |

Both fingerprints are of the same file, `SKILL.md`. They do not match. So the two copies are
genuinely different — this is not an apples-to-oranges comparison.

**The card in this repository is not the card the maintainer runs.**

Two statements earlier in this file are wrong. We are leaving them in place, rather than editing
them, so you can see what changed and why.

1. The table above says the maintainer's copy is `unknown`. It is not unknown any more. See above.
2. The section on `validate_package.py` says that script does not exist anywhere. It does exist.
   It is on the maintainer's machine, at `scripts/validate_package.py`, 3,464 bytes. The build
   could not see it. That is not the same as it being missing.

Eleven files never made it into this repository: the field report, `README.md`, two template
files, two eval files, five reference documents, and two scripts. That is tracked in `skills#233`.

**Why this matters for the 0.2.0 candidate landing next to this file.** The 0.1.0 copy here came
from the public source. The 0.2.0 candidate was built from the maintainer's full package. So the
two do not share a starting point, and you cannot cleanly measure one against the other until
`skills#233` is done.

**The lesson worth keeping.** A build agent running in a sealed container could not see some
files. It reported them as missing. "I could not find it" became "it does not exist" — and that
went into the record as a fact about the card. If you say something is absent, say what you
searched.

---

## Second correction, 2026-09-06 — the count was wrong, and the two copies are not two versions of one document

The correction above resolved one question and opened three more. We ran all of them on the
maintainer's host on 2026-09-06. Everything below is measured there, not inferred.

### Thirteen files were missing, not eleven

`skills#233` says eleven and then lists thirteen. Its arithmetic was fourteen local files minus
three repository files. That subtraction assumed the three repository files also sat in the local
install. They do not.

The local install holds fourteen files. Only `SKILL.md` is shared with this repository.
`PROVENANCE.md`, `gotchas.md` and `EVIDENCE.md` exist only here. So thirteen files were missing.
Thirteen landed in this change.

### The public copy and the local copy are not two versions of one document

The correction above proved the two `SKILL.md` files differ. It did not ask what kind of
difference. We read both.

| | Public source | Maintainer local install |
|---|---|---|
| Size | 6,018 bytes | 6,191 bytes |
| SHA-256 | `132dc292...` | `34c408a9...` |
| Declares a version | no | yes, `metadata.version: "0.1.0"` |
| Shape | an essay in five headed sections | a procedure: seven numbered steps, a disclosure map, hard boundaries, a completion test |
| Links to sibling files | none | nine, and all nine exist beside it |

The two share a name and almost no text. This is not drift between two releases. These are
different documents.

**The finding: the local install is the canonical 0.1.0 package, and the public file is an earlier
draft.** Three things decide it. The local copy states its own version and the public copy makes no
version claim at all. The local copy's nine internal links all resolve, and a package whose links
resolve is the package those links were written for. Every file of the local package carries the
same modification time, 2026-08-11 23:25, which is what an install writes; only the field report is
later, at 2026-08-17 13:38, because the maintainer wrote it afterwards. Nothing in the install was
edited after it landed.

So the ticket's own `Revisit if:` does not fire. The local install is not a modified copy. It is the
whole package, and this repository had a fragment of something else.

**The consequence, and it reaches further than this ticket.** `#216` landed the public essay and
recorded it as "the frozen 0.1.0 baseline". It is not that baseline. A reader who opens this card to
see what 0.1.0 was will read a document the maintainer never ran.

We are not repairing that here. `SKILL.md` in this directory now holds the 0.2.0 candidate that
landed in `6e81b5d`, so the frozen 0.1.0 baseline `#216` criterion 5 asked for is not at HEAD in
either form: the public essay was replaced, and the canonical package file never arrived. Restoring
it is a choice between three documents, and it belongs to whoever owns the 0.2.0 candidate rather
than to this landing. It is recorded so the choice can be made on purpose.

### What we could not check, and the search that says so

We did not compare the registry package digest
`2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9`. We could not obtain the
package. Three addresses were tried on 2026-09-06:
`https://skills.sh/api/skills/theswerd/aicode/self-documenting-code` returned HTTP 404;
`https://api.skills.sh/theswerd/aicode/self-documenting-code` returned HTTP 404; and
`https://skills.sh/theswerd/aicode/self-documenting-code` returned HTTP 200 with a 68,943-byte HTML
page carrying no version string, no digest and no package link.

The public GitHub tree was listed through the contents API on the same date. It holds exactly one
file under the skill path: `SKILL.md`, 6,018 bytes.

So the comparison is still two-way, not three-way. That is the search. The gap is a property of it.

### `validate_package.py` exists

The section above says the script "is not present in this repository and is not part of the public
theswerd/aicode tree". The second half is correct. The first half was true of the container that
wrote it and false of the world: the script sat on the maintainer's host at
`scripts/validate_package.py`, 3,464 bytes. It now sits in this directory.

We left that paragraph as written rather than editing it, matching the first correction, so the
record shows what changed.

`#216` task 4 asked for the script's allow-list to accept `gotchas.md`. It now does.
`ALLOWED_TOP_LEVEL` gained one entry, and nothing else in the script changed.

**The script still fails against this card, and the reason is structural.** It validates the
upstream nested layout. It expects `references/`, `assets/`, `scripts/` and `evals/`, and it checks
that `scripts/snapshot.py` exists. This repository's card layout is flat. Run here, the script
reports twelve flattened files as unexpected top-level entries and reports `scripts/snapshot.py`
missing. Both errors describe the layout choice, not the card. Widening the allow-list far enough to
hide them would rewrite a frozen artifact well past what `#216` asked, so we did not.

### The eval files, read first-hand

`#216` recorded the registry's claim that the evals contain no fixture files, and said the evidence
ceiling was fixed until executable contrasting fixtures replaced them. Nobody had opened the files,
because they were not here. We opened both.

`evals/evals.json` holds five cases. Each carries a prompt, an expected output and three or four
assertions. Every one of them also carries `"files": []`. The array is empty in all five. So there
is no code for a run to act on, and the registry's claim is correct as far as it goes.

`evals/trigger-evals.json` is a different matter. It holds twenty labelled queries: ten marked
`"should_trigger": true` and ten marked `false`. The negative rows name near neighbours the card
should decline, among them writing an architecture decision record, generating API reference
documentation, reviewing a pull request for injection defects, and adding docstrings without
changing code. That is a contrasting fixture set, and it needs no code to run.

**The finding: `#216`'s evidence ceiling is right about efficacy and wrong about triggering.** No run
can measure what this card does to code, because no code fixtures exist. A run can measure whether
the card fires on the right requests, today, against twenty labelled rows that are already written.
Those are two different claims, and the ceiling applies to only one of them.

One thing a promotion pass must handle: this file uses the key `"evals"`, and this repository's own
corpus convention, checked by `scripts/validate_eval_corpora.py`, uses `"cases"`. That validator
walks published cards under `skills/` and does not reach `_quarantine/`, so nothing fails today. The
mismatch becomes real at promotion.

### What we changed while landing, and why

`#216` criterion 5 forbids rewriting the baseline while landing it. Twelve of the thirteen files are
byte-identical to the local install, verified with `cmp`. Two changes were made, and both are
recorded here rather than left for a reader to notice.

**Flattening.** `AGENTS.md:44` sets a flat per-skill layout. House practice agrees and is unanimous:
no card in `_quarantine/` has any subdirectory, and across all published cards the only subdirectory
in use is `evals/`, on fourteen of them. So nine files moved up one level and kept their names:

- `references/assessment-model.md`, `references/claude-code-integration.md`, `references/python.md`,
  `references/refactoring-patterns.md`, `references/review-protocol.md`
- `assets/claude-rules-template.md`, `assets/report-template.md`
- `scripts/snapshot.py`, `scripts/validate_package.py`

`evals/evals.json` and `evals/trigger-evals.json` stayed where they were, because `AGENTS.md:190`
names `evals/` as this repository's own sanctioned convention.

No file contents were rewritten to match the new paths. `README.md` therefore still describes the
nested layout under its "Package structure" heading, and the canonical 0.1.0 `SKILL.md`, which is
not in this tree, still links into `references/` and `assets/`. Correcting either would be a
rewrite, and criterion 5 forbids it. The discrepancy is real, and it is recorded here instead.

**De-personalization.** The field report named the maintainer's private repository on its line 3.
The de-personalization gate bans that name in Markdown, and `500ac26` had just replaced five public
occurrences of it. We made the same replacement, using the identical phrase that commit chose, so
passages counting distinct projects as separate evidence stay distinguishable. One line changed; a
`diff` against the source confirms nothing else did.

The file was also renamed. It arrived as `FIELD-REPORT-2026-08-17-workspace-lint.md` and landed as
`FIELD-REPORT-2026-08-17.md`. The old name carried the private repository in the path. The gate
would not have caught it: the hook matches the underscored spelling inside file contents, and the
filename used a hyphen. A residue check that reads only file contents cannot see a filename.
