---
"mrbinnacle-skills": patch
---

The `pull-rebase` card now fires after a pull has already rebased your commits, not only before one, and its recovery step 2 gives a `git range-diff` command that pairs each old SHA with its rewritten copy. It also states, measured on git 2.56.0, that `git pull --ff-only` refuses diverged history under `pull.rebase=true` without rewriting anything, and its guard recipe now lets that command pass.
