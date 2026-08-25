---
"mrbinnacle-skills": patch
---

Pin every workflow `uses:` to a full 40-hex commit SHA with a trailing version comment.

Five of six actions rode mutable tags (`actions/checkout@v4`, `actions/setup-python@v5`,
`actions/github-script@v7`, `lycheeverse/lychee-action@v2`, `pre-commit/action@v3.0.1`). Only
`actions/setup-node` was already pinned. Each new SHA was verified via `git ls-remote` to be
the commit its named tag points at, so the workflows run the same action versions they ran
before. CVE-2025-30066 repointed every `tj-actions/changed-files` tag from v1 to v45 inside a
24-hour window; a floating tag is not a pin. The gate that will refuse a future floating tag
is tracked separately.
