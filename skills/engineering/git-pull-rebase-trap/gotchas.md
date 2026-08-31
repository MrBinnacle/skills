# gotchas — git-pull-rebase-trap

## [ANTICIPATED]

- **Per-branch rebase config overrides global.** `branch.<name>.rebase=true` set per-branch will silently override a global `pull.rebase=false`. Check both.

- **`pull.rebase=interactive` exists.** Certain configs set `pull.rebase=interactive`, which opens an editor mid-pull. If you're in a non-interactive context (Claude Code, CI), this hangs.

- **`git config --global --list | grep rebase` misses repo-local.** Check three scopes: `--system`, `--global`, `--local`.

- **The reflog is your only friend after a rebase.** If you didn't note the pre-pull HEAD SHA, `git reflog` is the recovery surface. Don't `git gc` between the rebase and the recovery.

- **Backfill commits look like "drift" to audit-state-consistency checks.** If your project has an audit-state check that compares state-file SHA references to git history, a post-rebase backfill needs an explicit event_type (e.g., `SHA_BACKFILL`) so the check doesn't flag it as silent state-file editing.

## [OBSERVED]

*(Append observed gotchas here as they surface in future sessions. Do not delete entries — gotchas are stress-test signal.)*

- **2026-05-25 / a personal production project:** Hit on `git pull origin main --no-commit --no-ff` during a push-divergence incident. `pull.rebase=true` configured globally. Rewrote 22 commits, required 111 SHA substitutions across 5 state files. User authorized "accept rebase + backfill" recovery path. Direct trigger that produced this skill.

- **2026-08-10 / mention-only false positives:** A private guard matched a `git` token followed later by a `pull` token anywhere in the command string. It repeatedly blocked legitimate commands that only named the skill or guard, including reading the guard's own source; two later reproductions blocked path globs naming this skill's directory. Parse actual shell/Git arguments instead. A guard that trains users to bypass the whole family is worse than no guard.

- **2026-08-23 / discriminator run (rotation pass, step 2):** This card had never been
  model-invoked across 261 tracked startups, so the retrieval-vs-insurance discriminator ran: a
  corpus sweep of the maintainer's three tracked clones (all `.md` surfaces, including session
  checkpoint archives; raw transcripts and the private archive not swept) found **zero trap
  occurrences outside the 2026-05-25 founding incident**. Diagnosis: **insurance — and partly
  displaced enforcement.** A PreToolUse guard in the maintainer's environment deterministically
  blocks the bare `git pull` that caused the founding incident, so the trap is prevented upstream
  of any skill retrieval; non-invocation says nothing about the card's worth (consistent with its
  `CANT_TELL_YET` screen shape). The guard's mention-only false positive (entry above) reproduced
  twice during this very run: it blocked the verification `grep`, then blocked the `git commit`
  recording this entry because the commit message's prose contained the trigger words.
