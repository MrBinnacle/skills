---
"mrbinnacle-skills": patch
---

`pull-rebase`'s paired verdict now reads `CANT_TELL_YET (stale receipt: card_hash_mismatch)`. The receipt was issued against the card's `SKILL.md` before the v2.0.0 rename changed its bytes, so under the rotation pass's currency gate it no longer disposes anything; the link stays as history. The verdict word is unchanged. The conformance check O5, run with the harness root, failed on this row until now.
