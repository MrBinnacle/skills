---
"mrbinnacle-skills": patch
---

The skill-format gate no longer rejects files git ignores.

`scripts/validate_skill_formats.py` walked the working tree and judged everything in it, so a maintainer who ran `im-up`'s test suite — which its own `SKILL.md` tells them to run — got six rejections on `.pytest_cache/` files that `.gitignore` excludes and that CI has never seen. CI was green and stayed green, because a fresh checkout has no ignored files. The only person the gate ever shouted at was the only person who could act on it, about something that was never a violation, which is how a reader learns to route around a whole family of checks.

The gate now asks git, via one `git check-ignore` call for the whole file list. That is deliberately not `git ls-files`: an untracked file no rule ignores — a `payload.sh` dropped in five minutes ago — is still judged, and a tracked file is judged even if a pattern matches it. A tree that is not a git work tree (a reader's install directory, a released tarball) is judged in full, and the status line now says which mode the run was in rather than leaving it to be inferred.

Five suite cases cover it: an ignored undeclared format passes, the same file tracked still fails, an untracked unignored file still fails, a non-git tree is judged in full, and a non-git run says nothing was skipped. The existing poison controls still fail for their own reasons.
