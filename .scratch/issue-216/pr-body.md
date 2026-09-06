# PR Body — Issue #216: Land self-documenting-code 0.1.0 into _quarantine/

## Acceptance Criteria

### 1. Establish which copy of 0.1.0 is canonical before copying anything

**What was built:** Retrieved public `SKILL.md` from theswerd/aicode. Hashed it. Compared
against the registry package SHA-256 recorded on the issue. Local install was not mounted.

**Result:** Public file SHA-256
`132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885`. Registry package SHA-256
`2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9` (tarball digest; not
directly comparable to a single-file digest). Three-way comparison incomplete — recorded in
`PROVENANCE.md` and `gotchas.md`, not silently resolved.

### 2. Land the canonical 0.1.0 into _quarantine/self-documenting-code/ (flat layout)

**What was built:** `_quarantine/self-documenting-code/{SKILL.md,PROVENANCE.md,gotchas.md}`.
Flat layout. `SKILL.md` is byte-identical to the public source (no rewrite).

### 3. Add PROVENANCE.md recording where it came from, its hash, and the date

**What was built:** Source URL, file hash, registry package hash, land date 2026-09-06, open
canonical-copy finding, note that `validate_package.py` is not in-tree.

### 4. Add append-only gotchas.md and update validate_package.py

**What was built:** `gotchas.md` with anticipated entries plus one observed (baseline rewrite
caught on review). `validate_package.py` is not in this repository and not in the public
source tree — criterion 4's validator half cannot be satisfied in-tree; gap recorded.

### 5. Preserve 0.1.0 as the frozen executable baseline

**What was built:** `SKILL.md` restored and verified byte-identical to upstream after an
implement pass had rewritten `description`. Frontmatter remains
`description: A guide for writing self-documenting code` (43 characters).

## What this landing does not do

- Does not publish. Fails ADMISSION.md criteria 1, 2, and 4.
- Does not build 0.2.0-rc.1.
- Does not add a second skill identity.

## Files changed

| File | Action |
|---|---|
| `_quarantine/self-documenting-code/SKILL.md` | Added (frozen 0.1.0, byte-identical to public source) |
| `_quarantine/self-documenting-code/PROVENANCE.md` | Added |
| `_quarantine/self-documenting-code/gotchas.md` | Added |
