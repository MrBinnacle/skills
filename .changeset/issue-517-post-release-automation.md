---
"mrbinnacle-skills": patch
---

Two workflows now finish a release ([#517](https://github.com/MrBinnacle/skills/issues/517)). `release-pin.yml` opens the marketplace pin pull request when a push to `main` changes the version. `release-receipt.yml` opens the README install-receipt pull request after the first passing `tests.yml` push run at the new version. Both use `GITHUB_TOKEN`; a maintainer approves each pull request's checks, then merges it. Nothing changes for installed users.
