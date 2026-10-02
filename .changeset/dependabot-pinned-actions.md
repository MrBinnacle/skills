---
---

chore: add `.github/dependabot.yml` so the SHA-pinned GitHub Actions receive update pull requests (#329).

The config covers the `github-actions` ecosystem, runs weekly on Monday at 06:00 UTC, and groups
every action into one pull request. It changes repository automation only. No card and no package
behaviour changes, so this changeset is empty and the release is not bumped by it.
