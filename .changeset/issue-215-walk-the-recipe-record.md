---
"mrbinnacle-skills": patch
---

The quarantined `walk-the-recipe` candidate now has an evidence record: `EVIDENCE.md`, `gotchas.md`, and two clean-state replay receipts with sha256 hashes. The positive replay walks the v3.0.1 README install as a Windows user with no SSH key and a long configuration path, and the card finds the path-length assumption that README did not state. The negative replay walks the v3.1.0 README, which declares that environment unsupported, and the card classifies it as declared rather than as a hidden assumption. `SKILL.md` lost its `metadata:` block, gained a "declared out of scope" class, and was compressed under the size bound. The card stays in `_quarantine/`; no published card changes.
