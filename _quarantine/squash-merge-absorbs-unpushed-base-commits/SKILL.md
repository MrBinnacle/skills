---
name: squash-merge-absorbs-unpushed-base-commits
description: |
  A squash merge silently relabels commits that were never yours to squash, when the
  branch was cut from a local base that sat ahead of its remote. Use when: (1) a PR's
  commit list shows commits you did not write on that branch — a release commit, a
  session close, a colleague's merge — alongside your own; (2) `git log` on the default
  branch no longer shows a commit you know landed, though its content is present;
  (3) a tag, a changelog entry, a state file or a handoff references a SHA that is no
  longer reachable from the default branch; (4) you are about to cut a feature branch
  and `git status` says "Your branch is ahead of 'origin/main' by N commits"; (5) a
  workflow commits to the default branch locally without pushing (a close ritual, a
  version bump, a generated-artifact commit) and later work branches off it. The content
  always survives; the absorbed commits' messages, SHAs and authorship do not.
author: Claude Code
version: 1.0.0
date: 2026-08-31
---

# A Squash Merge Absorbs Commits From an Unpushed Base

## Problem

You cut a feature branch, open a PR, squash-merge it. The default branch afterwards is
missing commits that had nothing to do with your feature — their content is there, but
their messages, SHAs and authorship are gone, folded into your feature's commit.

Nothing failed. No warning appeared. Both behaviours that produced it are correct.

## Context / Trigger Conditions

The composition needs three things, and each is individually unremarkable:

1. **A commit lands on the default branch locally and is not pushed.** Any workflow that
   commits without pushing does this: a session-close ritual, a `version` bump before a
   release, a script that commits generated artifacts, or simply forgetting.
2. **A feature branch is cut from that local default branch.** The normal move.
3. **The PR is squash-merged.** The default on many repositories, and often enforced.

Symptoms, in the order you are likely to meet them:

- The PR's **Commits** tab lists commits you did not write on this branch.
- After the merge, `git log --oneline main` no longer shows a commit you remember landing.
- `git rev-list --left-right --count origin/main...main` reports both sides non-zero, and
  a `git merge --ff-only` refuses with "Diverging branches can't be fast-forwarded".
- A file, ticket, tag or handoff cites a SHA that `git branch --contains <sha>` says is on
  no branch.

## Mechanism

GitHub computes a PR's commit list as the commits reachable from the **head** and not from
the **base as the remote knows it** — effectively `origin/main...head`. Your unpushed
commits are on the head and absent from `origin/main`, so they are part of the PR by
construction. The docs describe squashing "the pull request's commits"; that phrase is
doing more work than it looks, because which commits those are depends on a base you may
have moved locally.

Squash then writes **one** commit whose tree is the head's tree and whose message is the
PR's. Every input commit's identity — message, SHA, author, date — is discarded. The
content survives intact, which is exactly why nothing alerts you.

## Solution

**Before cutting a branch**, check that the base is not ahead of its remote:

```sh
git fetch origin
git rev-list --left-right --count origin/main...main   # want "0<TAB>0"
```

Non-zero on the right means local commits that a squash will absorb. Push them, or cut the
branch from `origin/main` instead:

```sh
git switch -c feature/x origin/main
```

**Fix the workflow, not the instance.** If a scripted or ritual commit lands on the default
branch, make that script push. The check above is a guard against a window; pushing closes
the window. A push moves no commit, so it is safe to add to almost any commit step — but
make a failed push **report and continue** rather than abort, because the commit has already
landed and killing the workflow on a network error is the worse failure.

**After the fact**, if the squash already happened:

```sh
git diff <your-branch-head> origin/main        # empty output = no content was lost
git merge origin/main                          # reconcile; do NOT reset --hard
```

Use `git merge`, not `git reset --hard`: the merge records why the histories diverged and
keeps the absorbed commits reachable through the merge's second parent, which is the only
remaining way to resolve a citation of their SHAs.

## Verification

- `git rev-list --left-right --count origin/main...main` reports `0	0`.
- `git diff <branch-head> origin/main` is empty, proving the squash preserved every tree.
- `git branch --contains <absorbed-sha>` names a branch — if it names none, the commit
  survives only in the reflog and will expire.

## Example

Observed 2026-08-31. A session-close ritual committed to `main` and, by design, did not
push. Two closes ran, so `main` sat two commits ahead of `origin/main`. A bug-fix branch cut
from `main` therefore carried three commits, and the PR listed all three:

```
docs(state): S374 close - ...
docs(state): S375 close - ...
fix(factory): carry the repository qualifier on a body blocker reference
```

The squash produced one commit under the bug fix's message. `git diff` between the branch
head and the new `origin/main` was empty — no content lost. But a state file recorded head
`1a43824` as the S375 close, and that SHA was no longer reachable from `main`, so the record
pointed at nothing.

The fix was applied to the workflow rather than to the incident: the close script now pushes
between its commit and its snapshot step.

## Notes

- **The content is never at risk.** Say so first when reporting this, or the reader
  reasonably panics. What is lost is provenance: which commit did what, and when.
- **Not specific to GitHub.** GitLab's "Squash commits" and Azure Repos' squash merge
  compute the same `base...head` set and have the same consequence.
- **A rebase merge has the same exposure, differently shaped**: it replays the base-only
  commits onto the base, so they survive as commits but with new SHAs. Citations still break.
  A plain merge commit is the only strategy that preserves the original SHAs.
- **`git status`'s "ahead by N commits" is the warning**, and it is easy to read as routine
  because it is routine. The line is not "you are about to lose something"; it becomes that
  only in combination with a branch cut and a squash.
- Related: `git-pull-rebase-trap` (a bare `git pull` under `pull.rebase=true` rewrites local
  SHAs, which breaks citations by a different route).

## References

- [Pull request merges — GitHub Docs](https://docs.github.com/en/pull-requests/reference/pull-request-merges)
  — describes squash as combining "the pull request's commits" without specifying how that
  set is computed when the branch's base is ahead of the remote.
- [Configuring commit squashing for pull requests — GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/configuring-commit-squashing-for-pull-requests)
- [Merge strategies and squash merge — Azure Repos, Microsoft Learn](https://learn.microsoft.com/en-us/azure/devops/repos/git/merging-with-squash?view=azure-devops)
  — the same `base...head` semantics outside GitHub.
