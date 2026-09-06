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
