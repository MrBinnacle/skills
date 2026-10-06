---
---

chore: clear the red `dependency-audit` run and make a red run file an issue (#358).

`braces` GHSA-vfj7-8cjw-p6xm has no patched release (every version up to 3.0.3 is affected), so
no override can fix it. The fix bumps the release tooling instead: `@changesets/cli` 2.31.1 to
3.0.3 and `@changesets/changelog-github` 0.7.0 to 1.0.1. Changesets 3 no longer depends on
`micromatch` or `globby`, so `braces` leaves the tree and `npm audit` reports 0 vulnerabilities.
When the audit fails, a new `report-failure` job opens an issue, or comments on the open one,
with the run URL and the advisory IDs. Only that job holds `issues: write`. These are
devDependencies of a private package and repository automation, so no card changes and this
changeset is empty.
