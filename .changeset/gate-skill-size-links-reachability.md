---
"mrbinnacle-skills": minor
---

Gate three AGENTS.md authoring rules that were machine-checkable but ungated (skills#246): `SKILL.md` size bounds (400–7,168 bytes), local link resolution with case matching, and reader-facing auxiliary reachability from `SKILL.md` through local links.

`scripts/validate_card_files.py` grows the three checks. Exemption patterns for test/build files (`test_*.py`, `fixture-*.md`, `CONFIG.example.json`, `evals/`) are tree-wide; a stale pattern is reported only when the tree already uses exemptions. Link extraction follows markdown only, so Python subscript syntax cannot look like a markdown link. Case matching walks directory entries so a case-insensitive filesystem cannot hide a mismatch.

Live tree brought green in the same change: missing `EVIDENCE.md`/`gotchas.md` links added on twelve cards; `im-up`/`im-down` link packet format and operating scripts; `downstream-instruction-framing` extracts its paste-ready template to `FRAMING-TEMPLATE.md`; `subagent-research-reliability` moves the large-deliverable variant into `EXAMPLES.md`. `docs/rule-screens.md` marks the three rows gated.
