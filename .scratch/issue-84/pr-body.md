# Evidence body — #84: merge four session-boundary skills to two

## Review correction

The first implement pass added `write_state.py` as a second public script and claimed
ordering was structural. Review rejected that: two CLIs the agent sequences is the same
defect as two slash commands the operator sequences. This pass lands one close entrypoint
and one open entrypoint.

## What changed

- `im-down/close_session.py` — one public close: write durable state, commit with the
  `close_commit` marker, snapshot the packet at the post-commit HEAD. Order is fixed inside
  the process; callers cannot reorder stages.
- `im-up/open_session.py` — one public open: receive-mode validate, then load `state_file`,
  then emit one receipt carrying `state_read` evidence. Missing doctrine rejects.
- `im-down/SKILL.md` / `im-up/SKILL.md` — procedures name only those entrypoints.
- Band rotation explicitly out of scope on the close card, with no enforcing surface.
- `write_state.py` removed (it was the two-script false fix).
- Shared parity contract stays the eight previously shared files; close/open scripts are
  card-private (same pattern as `snapshot_state.py`).

`session-end-to-state` and `session-start-from-state` were never published in this repo.
Retirement of local-only installs is the operator's local install step, not a `RETIRED.md`
row. Merge direction (keep published `im-down`/`im-up` as trunk) matches the 2026-08-15
architecture comment on #84.

## Acceptance criteria

### Criterion 1: Exactly two boundary skills exist

**Built:** Published tree has `im-down` and `im-up` only. No `session-end-to-state` or
`session-start-from-state` paths in the repo.

**Test:** `git ls-files 'skills/**/SKILL.md' | grep -E 'im-(down|up)|session-'` — only the
pair. Exhaustive path search finds no session-* skill dirs.

### Criterion 2: One typed command closes; one opens

**Built:** `/im-down` runs `close_session.py`. `/im-up` runs `open_session.py`.

**Test:** `close_session_cases()` and `open_session_cases()` invoke those single scripts end
to end.

### Criterion 3: Wrong order is impossible, not merely documented

**Built:** State write, commit, and snapshot run inside `close_session.py` in fixed order.
No public flag reorders them. Packet HEAD is the head captured after the close commit.

**Test:** `close_session_cases()` asserts packet `repository.head ==` post-commit HEAD and
that a config without `state_file` fails before any packet is written.

### Criterion 4: Packet passes receive-mode against a clean tree

**Built:** After fill, produce and receive both ACCEPTED at the close HEAD.

**Test:** Final block of `close_session_cases()`.

### Criterion 5: Stale-HEAD regression still rejects

**Built:** Unchanged `fixture-stale.md` + existing `repository_cases()` + CI poison control.

**Test:** `repository_cases()` stale branch; poison control exit 2 + REJECTED.

### Criterion 6: Doctrine write still happens; skip fails

**Built:** Close requires `state_file` and commits it. Open requires the file and embeds
`state_read` on ACCEPTED. Open with a never-written `state_file` path rejects.

**Test:** `close_session_cases()` state contents + missing `state_file` config fail;
`open_session_cases()` loaded state + missing-path reject.

### Criterion 7: Band rotation out of scope

**Built:** Boundary-limits note in `im-down/SKILL.md` names no enforcing surface.

## Gate results (touched surfaces)

- `im-down` suite — PASS with `, no-drift`
- `im-up` suite — PASS with `, no-drift`
- Stale-HEAD poison control — REJECTED exit 2
