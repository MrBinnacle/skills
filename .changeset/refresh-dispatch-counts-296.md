---
"mrbinnacle-skills": minor
---

Add `scripts/refresh_dispatch_counts.py`: a harvest-step path that rewrites each published card's `Dispatches recorded` row from the usage log.

The log path is an input (`SKILL_USAGE_LOG`, defaulting to a sibling private research checkout). A missing log prints SKIP, changes nothing, and exits 0. An empty log rewrites nonzero rows to zero. Already-zero rows keep their card-specific diagnosis (hook-unobservable prose on `pull-rebase` and `stale-deploy`) and only move the measurement date. AGENTS.md harvest step 2 names the script.
