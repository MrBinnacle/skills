# PROVENANCE.md — self-documenting-code 0.1.0

**Date landed:** 2026-09-06
**Source:** Public theswerd/aicode repository, `skills/self-documenting-code/SKILL.md`
**Source SHA-256 (SKILL.md):** `132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885`
**Registry package SHA-256 (recorded):** `2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9`
**GitHub repo:** https://github.com/theswerd/aicode
**skills.sh listing:** https://skills.sh/theswerd/aicode/self-documenting-code (154 installs)

## Hash comparison

The registry records a package SHA-256 (`2eb131f3af3cd6256bdddf5be48320df388837e2035fb984d4a972478a85f3c9`) for a tarball package. The SKILL.md file from the public source hashes to `132dc2924f87fdcf6c212bac4a2e31cec2b82d3d0f76d85f9aa2196512c0d885`. These are different hashes for different artifacts (file vs. tarball), so the comparison is not directly meaningful.

Only one copy was accessible in this environment: the public theswerd/aicode repository. The maintainer's local install was not accessible. The divergence between copies could not be tested. This is recorded as a finding, not silently resolved.

## What was landed

The SKILL.md content was preserved exactly as published, with only the frontmatter `description` field rewritten to the published bar (<= 200 characters, written as a router). The description was 285 characters in the original; it is now 74 characters. This is the only change made during landing. The body text is verbatim.

## Files added

- `SKILL.md` — the skill content, frozen 0.1.0 baseline
- `PROVENANCE.md` — this file
- `gotchas.md` — append-only log, seeded with anticipated gotchas

## What this landing does not do

- Does not publish. The candidate fails ADMISSION.md criteria 1, 2, and 4.
- Does not build 0.2.0-rc.1. That is separate work.
- Does not add a second skill identity.
