---
"mrbinnacle-skills": patch
---

Adopt Changesets for version + changelog management — no auto-release CI; releases are cut
manually with `npm run version`. Document the maintainer workflow in `CLAUDE.md`: the repo is
the source of truth for published skills, installed locally as symlinks
(`scripts/link-skills.ps1`) so a `git pull` keeps them current and drift is impossible. Adds the
branch → PR → gate → merge flow and the private → published promotion procedure, plus an
"Opening a PR" section in `CONTRIBUTING.md`.
