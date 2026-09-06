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
