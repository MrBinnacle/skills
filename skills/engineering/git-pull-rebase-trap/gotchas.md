# gotchas — git-pull-rebase-trap

## [ANTICIPATED]

- **Per-branch rebase config overrides global.** `branch.<name>.rebase=true` set per-branch will silently override a global `pull.rebase=false`. Check both.

- **`pull.rebase=interactive` exists.** Some configs set `pull.rebase=interactive`, which opens an editor mid-pull. If you're in a non-interactive context (Claude Code, CI), this hangs.

- **`git config --global --list | grep rebase` misses repo-local.** Check three scopes: `--system`, `--global`, `--local`.

- **The reflog is your only friend after a rebase.** If you didn't note the pre-pull HEAD SHA, `git reflog` is the recovery surface. Don't `git gc` between the rebase and the recovery.

- **Backfill commits look like "drift" to audit-state-consistency checks.** If your project has an audit-state check that compares state-file SHA references to git history, a post-rebase backfill needs an explicit event_type (e.g., `SHA_BACKFILL`) so the check doesn't flag it as silent state-file editing.

## [OBSERVED]

*(Append observed gotchas here as they surface in future sessions. Do not delete entries — gotchas are stress-test signal.)*

- **2026-05-25 / Writ:** Hit on `git pull origin main --no-commit --no-ff` during SEC-009 push divergence. `pull.rebase=true` configured globally. Rewrote 22 commits, required 111 SHA substitutions across 5 state files. User authorized "accept rebase + backfill" recovery path. Direct trigger that produced this skill.
