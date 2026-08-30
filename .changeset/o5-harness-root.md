---
"mrbinnacle-skills": patch
---

`scripts/validate_conformance.py`: O5 gains an optional `--harness-root <path>`. Without it, O5 stays `CANNOT-CHECK`, so CI never prints a green line for a check that did not run. With it, O5 reads the receipt each card's controlled row links in its `Receipt:` clause (markdown-link or backtick form) and fails on four conditions: the receipt file is absent; its `subject_identity.skill_id` differs from sha256 of the card's `SKILL.md`; its `verdict` differs from the row's opening verdict word; a newer receipt with the same `skill_id` exists that the row does not link. Eight subprocess-driven cases cover the flag-less path, PASS, both clause shapes and one FAIL per condition. No published card changed.
