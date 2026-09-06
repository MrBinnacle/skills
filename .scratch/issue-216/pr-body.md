# PR Body — Issue #216: Land self-documenting-code 0.1.0 into _quarantine/

## Acceptance Criteria

### 1. Establish which copy of 0.1.0 is canonical before copying anything

**What was built:** Retrieved SKILL.md from the public theswerd/aicode repository
(https://github.com/theswerd/aicode). Hashed the file with sha256sum.

**Test:** `sha256sum` of the retrieved SKILL.md produced
`132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885`.

**Observation:** The registry records package SHA-256
`2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9`, which is a tarball
hash, not a file hash. Only one copy was accessible (the public source). The maintainer's
local install was not available in this disposable container. The divergence between copies
could not be tested. This is recorded in `PROVENANCE.md` as a finding, not silently resolved.

**What failed before:** Nothing — the skill did not exist in this repository.
**What passed after:** The skill directory exists under `_quarantine/` with the correct
content.

### 2. Land the canonical 0.1.0 into _quarantine/self-documenting-code/ (flat layout)

**What was built:** Created `_quarantine/self-documenting-code/` containing `SKILL.md`,
`PROVENANCE.md`, and `gotchas.md`. The layout is flat — no `references/` or `assets/`
subdirectories, matching the per-skill flat layout convention.

**Test:** `ls _quarantine/self-documenting-code/` lists exactly three files: `SKILL.md`,
`PROVENANCE.md`, `gotchas.md`.

**Observation:** The directory structure matches existing quarantine cards (e.g.,
`walk-the-recipe-as-target-user/` with only `SKILL.md`). The SKILL.md content is preserved
verbatim from the source, with only the frontmatter `description` field rewritten to the
published bar (<= 200 characters, router form). The original description was 285 characters;
the rewrite is 74 characters.

**What failed before:** `git ls-files | grep self-documenting` returned nothing.
**What passed after:** `git ls-files _quarantine/self-documenting-code/` returns three files.

### 3. Add PROVENANCE.md recording where it came from, its hash, and the date

**What was built:** `_quarantine/self-documenting-code/PROVENANCE.md` records the source
(GitHub repo URL), the SKILL.md SHA-256 hash, the registry package SHA-256 (as recorded),
the skills.sh listing URL, and the landing date (2026-09-06).

**Test:** `cat _quarantine/self-documenting-code/PROVENANCE.md` contains all required fields.

**Observation:** The hash comparison section documents that the two hashes are for different
artifacts (file vs. tarball) and are not directly comparable. Only one copy was accessible.

**What failed before:** No PROVENANCE.md existed for this skill anywhere.
**What passed after:** PROVENANCE.md exists with complete provenance record.

### 4. Add append-only gotchas.md and update validate_package.py

**What was built:** `_quarantine/self-documenting-code/gotchas.md` with four `[ANTICIPATED]`
entries seeded from the ticket's own findings: description rewrite risk, missing evidence,
missing eval fixtures, and the external registry validator gap.

**Test:** `cat _quarantine/self-documenting-code/gotchas.md` contains four dated entries.

**Observation:** The `validate_package.py` script does not exist in this repository — it is
part of the external registry's package-governance system. The entry in gotchas.md documents
this gap. The repository's own `validate_card_files.py` checks published cards under
`skills/`, not quarantine cards, so no gate is tripped by the quarantine landing.

**What failed before:** No gotchas.md existed for this skill anywhere.
**What passed after:** gotchas.md exists with append-only structure and four entries.

### 5. Preserve 0.1.0 as the frozen executable baseline

**What was built:** The SKILL.md body text is preserved verbatim from the source repository.
The only change is the frontmatter `description` field, rewritten from 285 to 74 characters
to meet the published description bar.

**Test:** Diff between source SKILL.md body and landed SKILL.md body shows zero changes.

**Observation:** The description rewrite is the single intentional change, documented in
PROVENANCE.md. The body text — Semantic Functions, Pragmatic Functions, Models, Where Things
Break — is byte-identical to the source.

**What failed before:** N/A — the baseline did not exist in this repository.
**What passed after:** The baseline exists and is preserved.

## What this landing does not do

- Does not publish. The candidate fails ADMISSION.md criteria 1, 2, and 4.
- Does not build 0.2.0-rc.1.
- Does not add a second skill identity.

## Files changed

| File | Action |
|---|---|
| `_quarantine/self-documenting-code/SKILL.md` | Added (frozen 0.1.0 baseline) |
| `_quarantine/self-documenting-code/PROVENANCE.md` | Added (provenance record) |
| `_quarantine/self-documenting-code/gotchas.md` | Added (append-only gotcha log) |
