---
name: exit-worktree-cwd-override-merge-from-worktree
description: |
  When ExitWorktree refuses with "cannot be called from a subagent with
  a cwd override," merge the worktree branch back to main using
  `git -C "<main-repo-path>" merge <worktree-branch>` from inside the
  worktree, instead of trying to exit first. Git merge operates on
  branch refs and doesn't care about working directory. Use when: (1) you
  entered a worktree via EnterWorktree, did your work, and now want to
  merge back to main but ExitWorktree refuses with the cwd-override error;
  (2) you need to merge a branch in worktree A while you are physically
  cwd'd in worktree B; (3) any situation where the harness-managed cwd
  state blocks the directory change ExitWorktree would normally do.
  Avoids the trap of trying to chase the ExitWorktree refusal by
  navigating manually — the merge doesn't need the navigation.
metadata:
  type: workaround
---

# ExitWorktree cwd-override: merge from inside the worktree with `git -C`

## Problem

You called `EnterWorktree(name="my-feature")` to set up an isolated branch. The harness moved your session's working directory into `.claude/worktrees/my-feature` on branch `worktree-my-feature`. You dispatched a subagent, the work landed, you ran reviews, and now you want to ExitWorktree(action="keep") to return to main so you can fast-forward main to the new commits.

`ExitWorktree` refuses:

```
ExitWorktree cannot be called from a subagent with a cwd override
(isolation: "worktree" or explicit cwd) — it would mutate the parent
session's process-wide working directory.
```

You're stuck: you can't exit; you can't change directory from inside the tool calls; the merge command appears to require being on the target branch.

## Root cause

`ExitWorktree`'s job is to revert the session's working directory. In some harness configurations (notably when the session itself was launched with a cwd override, or after EnterWorktree has nested-overridden the cwd), the tool can't safely mutate the process-wide cwd back. It refuses rather than corrupt parent state.

But the BLOCKER assumed by the error message — "I need to be on main to merge into main" — is wrong for `git merge`. Git operates on branch REFS, not on working directory state. You can merge into main from anywhere as long as you tell git which repo to operate on.

## Fix

Use `git -C "<path-to-main-repo>"` to invoke git as if you were in the main repo directory. The merge runs against main's HEAD ref, brings in the worktree branch's commits, and updates main's pointer — all without your shell ever cd'ing.

```bash
# You're currently in C:/...repo/.claude/worktrees/my-feature
# Main repo is at C:/...repo
git -C "C:/.../repo" merge --ff-only worktree-my-feature
# Or for a non-ff merge:
git -C "C:/.../repo" merge --no-ff worktree-my-feature -m "Merge worktree-my-feature"
```

This works because:

- `git -C <path>` is equivalent to `cd <path> && git ...` but doesn't change YOUR shell's cwd
- The merge target (main) is checked out in the main repo's working directory
- The merge source (`worktree-my-feature`) is a branch ref in the shared `.git/` directory
- No two checkouts of the same branch are needed; main stays checked out in main's working dir, the feature branch stays checked out in the worktree

## Verification

After the merge, verify main advanced and the worktree branch is preserved:

```bash
git -C "<main-path>" log --oneline -3            # main now contains the merged commits
git -C "<main-path>" branch -v                   # both 'main' and 'worktree-my-feature' present
git -C "<main-path>" status                      # clean
```

If you want to push immediately:

```bash
git -C "<main-path>" push origin main
```

## When NOT to use this

- If ExitWorktree DOES work, just use it. This workaround is for when the cwd-override refusal happens.
- If your merge has conflicts, you'll want to be ON the merging branch (main) interactively — the `git -C` approach still works, but you can't navigate to fix conflicts from inside the same shell. Resolve them by editing files (Edit tool works fine regardless of shell cwd).
- If you're doing a rebase rather than a merge, the same `git -C` works.

## Notes

- Don't try to use `EnterWorktree(path=<existing-worktree>)` to "switch" to the main worktree as a workaround — the main worktree typically isn't a *linked* worktree and isn't in the worktree registry the tool checks.
- Don't try to `cd "<main>"` in a Bash tool call and then run plain `git merge` — Bash tool calls don't persist cwd between invocations on most platforms, and even when they do, the harness's process-wide cwd may not be what the next tool call sees.
- The same `git -C` pattern works for `git log`, `git diff`, `git status`, etc. — any time you need to ask git about a repo other than the one your shell is currently in.

## Example (from skill-harness 2026-06-09)

```text
1. EnterWorktree(name="w2-cli-engineering") — session moves to .claude/worktrees/w2-cli-engineering
2. Implementer subagent commits a9bdacc, then f6201a8, on branch worktree-w2-cli-engineering
3. Reviews pass.
4. Try ExitWorktree(action="keep") — REFUSED ("cwd override").
5. Workaround:
   git -C "/path/to/your/repo" merge --ff-only worktree-w2-cli-engineering
   → Fast-forward; main advanced f13b3fd → f6201a8 (2 commits, +521 insertions).
6. git -C "/path/to/your/repo" push origin main
```

The merge succeeded without ever exiting the worktree session.

## References

- `git -C` documentation: https://git-scm.com/docs/git#Documentation/git.txt--Cltpathgt
- Git worktree documentation: https://git-scm.com/docs/git-worktree
