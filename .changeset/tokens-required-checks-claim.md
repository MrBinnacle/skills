---
---

`assets/tokens.json` prose only. The `closed_gaps.not_enforced.how` string said `main` carries no branch protection and no required checks, so the brand-kit validator was a signal rather than a gate. The `protect-main` ruleset requires both validator cells, so the string now records that it gates, and names the ruleset endpoint as the probe. The legacy branch-protection endpoint reports 404 for a branch a ruleset protects, which is what produced the stale reading. No shipped card changed, so nothing reaches installed users.
