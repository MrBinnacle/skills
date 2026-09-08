---
name: shared-checkout
description: Use before dispatching more than one agent that runs git in the same repo, or when a commit or rebase lands on a branch nobody targeted. They share one HEAD, which a file-overlap check cannot see.
---

# Concurrent subagents share one checkout and contend on HEAD

## Problem

You dispatch two agents to do independent work in the same repository. You check
for collisions by asking whether they touch the same files. They do not, so you
launch both and tell the user they cannot collide.

They collide anyway. A working directory has exactly one HEAD, one index, and
one set of refs. Two agents running `git checkout`, `git commit` and
`git rebase` in that directory are writing to shared mutable state that no file
manifest describes.

Observed failure, S308: agent A created its branch and wrote a file. Before it
committed, the parent session ran `git checkout main` then `git checkout -b` in
the same directory. Agent A's commit landed on the **parent's** new branch.
Agent A then ran `git rebase origin/main`, believing it was on its own branch,
and rebased a branch it did not own. Both pieces of work survived, but for a
while one agent's commit existed only inside a branch belonging to unrelated
work, and the parent pushed it there.

## Context / Trigger conditions

- More than one agent will run git in the same repository, concurrently.
- A dispatch names a repository by absolute path with no isolation set.
- You reasoned about collision risk in terms of files, directories, or "different
  repos" and concluded the agents are independent.
- `git status -sb` reports ahead/behind numbers inconsistent with what you just
  pushed.
- `git log --oneline origin/main..<your-branch>` lists a commit whose message you
  did not write.
- `git branch -a --contains <sha>` shows a commit living only on a branch that
  belongs to other work.
- An agent reports that a force operation was refused by a safety net and asks
  someone else to run it — that is usually this defect surfacing downstream.

## Root cause

Agent isolation is about context windows, not filesystems. Two agents with
separate context windows still share every checkout they are pointed at.

Git's mutable per-worktree state is HEAD, the index, and `.git/` refs. None of
it is namespaced per caller. `git checkout` in one process silently changes
which branch a *different* process is about to commit to, and neither process
can observe the other's intent.

File-overlap analysis is the wrong instrument because it models the repository
as a set of paths. The contended resource is not a path.

## Solution

**Set worktree isolation at dispatch.** In Claude Code, the Agent tool takes
`isolation: "worktree"`, which gives the agent its own git worktree with its own
HEAD, and removes it afterwards if unchanged.

```
Agent({
  description: "...",
  isolation: "worktree",     // <- not optional for concurrent git work
  prompt: "..."
})
```

Apply it whenever **any** of these is true:

- two or more agents will run git in the same repo;
- one agent will run git in a repo the parent session is also using;
- you do not know whether the agent will run git at all.

The last case matters. The cost of an unused worktree is a few hundred
milliseconds and some disk. The cost of a collision is a corrupted branch
topology discovered after a push.

**If a collision has already happened**, prefer non-destructive recovery:

```bash
git fetch origin
git log --oneline origin/main..<tangled-branch>   # see what is actually on it
git checkout -b <clean-branch> origin/main
git cherry-pick <only-your-commit>                # rebuild, do not rewrite
```

Cherry-picking onto a fresh branch from `origin/main` needs no force push and
leaves the tangled branch intact until every commit on it is confirmed safe
elsewhere. Do not delete the tangled branch while it is the only home of
somebody's commit.

## Verification

Before dispatch:

- Confirm the isolation flag is set on every concurrent agent touching the repo.

After each agent reports:

```bash
git diff --name-only origin/main        # only the files that agent should own
git log --oneline origin/main..HEAD     # only commits that agent authored
```

Both must be true. `git diff` alone is insufficient — a foreign commit whose
changes were later superseded shows no files but is still in the history you are
about to open a PR from.

## Example

The tell, as it actually appeared:

```console
$ git status -sb
## research/sers-preregistration...origin/research/sers-preregistration [ahead 7, behind 2]
```

Ahead 7 and behind 2 on a branch pushed sixty seconds earlier is not a network
problem. It is someone else's history in your branch.

```console
$ git log --oneline origin/main..research/sers-representation-preregistration
1cc62b1 docs(research): pre-register the representation-adequacy question
5f3565a docs(readme): greenfield rewrite per #181 surface 2      <- not mine
```

## Notes

- Symmetry matters: the parent session is one of the concurrent actors. Isolating
  the agents while the parent keeps running `git checkout` in the same directory
  does not fix it.
- A safety net that blocks `git branch -f`, `git reset --hard` and
  `git push --delete` will block the agent that notices the tangle from repairing
  it. That is correct behaviour and it means recovery routes to whoever holds the
  looser permissions — usually the parent. Plan for the repair, not just the
  prevention.
- Sibling worktrees created by other tooling (sandcastle, factory runners) already
  exist in some repos. `git worktree list` before dispatch tells you what is
  already attached.
- This is distinct from `cwd-drift` (one process, drifted
  cwd, wrong tree searched) and from
  `worktree-cwd` (merging out of a worktree the
  harness will not let you exit). Same neighbourhood, different defect.

## References

- Observed and recovered 2026-08-23 (S308), `MrBinnacle/skill-harness`. Parent
  session plus two dispatched README agents, one shared checkout.
- Claude Code Agent tool, `isolation: "worktree"`.
