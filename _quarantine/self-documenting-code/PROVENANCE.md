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
