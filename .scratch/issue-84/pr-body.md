# Evidence body — #84: merge four session-boundary skills to two

## What changed

The operator's local setup carried four session-boundary skills: `session-end-to-state` and
`im-down` on the close side, `session-start-from-state` and `im-up` on the open side. The
close required two typed commands in a specific order — `/session-end-to-state` commits (moving
HEAD), then `/im-down` records HEAD into the packet. Reversed, the packet recorded a
pre-commit HEAD and the receiver rejected it as stale at the next session.

The merge promotes the unpublished `session-end-to-state` and `session-start-from-state`
into the published `im-down` and `im-up`. `im-down` already writes durable state, commits
with the close marker, produces the packet scaffold, and validates in produce mode — all in
one invocation. `im-up` already validates the packet in receive mode and reports an
acceptance receipt. The four-skill split was the defect; the two published cards already
carry the merged functionality.

The only code change is a boundary-limits note in `im-down/SKILL.md` explicitly marking band
rotation as out of scope with the enforcing surface named (none exists; the operator manages
it manually).

## Acceptance criteria

### Criterion 1: Exactly two boundary skills exist

**Built:** The repo contains exactly two session-boundary skills: `im-down` (close) and
`im-up` (open). The other two (`session-end-to-state`, `session-start-from-state`) exist
only in the operator's local `~/.claude/skills/` and were never part of this repo. The
retirement of those local skills is outside the scope of this repository — the operator
removes them from their local install.

**Test:** `git ls-files 'skills/**/SKILL.md' | grep -E 'im-(down|up)'` returns exactly two
paths. No files matching `session-end-to-state` or `session-start-from-state` exist anywhere
in the repo (confirmed by exhaustive `find` and `grep` across all trees).

### Criterion 2: One typed command closes a session. One typed command opens one.

**Built:** `/im-down` closes. `/im-up` opens. No other command is required.

**Test:** `write_state_cases()` in `test_validate_packet.py` — runs `write_state.py` then
`snapshot_state.py` as part of one close invocation, verifies the state file exists, the
commit moved HEAD, and the packet validates in produce mode. `cli_cases()` — verifies
receive mode requires `--config` and `--repo-root`.

### Criterion 3: Wrong order is impossible, not merely documented

**Built:** `write_state.py` commits first (moving HEAD), then `snapshot_state.py` records
HEAD into the packet. `validate_close_commit()` in produce mode refuses a packet whose HEAD
commit message does not carry the `close_commit.contains` marker. `validate_unclaimed_head()`
refuses a HEAD already claimed by a prior packet. The ordering is structural: the scripts
enforce it, and the validator catches violations.

**Test:** `close_commit_cases()` — creates a repo with no close commit, verifies the
validator refuses. Commits with the RITUAL: marker, verifies the validator accepts.
`cli_close_commit_case()` — runs produce mode via CLI, verifies exit 2 and the "is not the
close commit" message. `claimed_head_cases()` — writes a prior packet claiming HEAD, verifies
the new packet is refused with "already claimed".

### Criterion 4: Packet passes receive-mode validation against a clean tree

**Built:** `write_state_cases()` writes state, commits, creates a packet fixture at the
post-commit HEAD, and validates it in produce mode. The fixture's HEAD matches the close
commit.

**Test:** `write_state_cases()` — the final block creates a fixture at the correct HEAD and
runs `validate_packet.py` in produce mode. Exits 0 with no errors. `repository_cases()` —
sets the clean fixture's HEAD to match a temp repo, verifies no errors.

### Criterion 5: Stale-HEAD regression fixture rejects

**Built:** `fixture-stale.md` carries a fake HEAD (`deadbeef...`). The validator rejects it
in both produce and receive modes when `--repo-root` points at a live repo.

**Test:** `repository_cases()` — loads the stale fixture, verifies "stale HEAD" appears in
errors. CI poison control — runs `validate_packet.py fixture-stale.md --mode produce
--repo-root "$GITHUB_WORKSPACE"`, verifies exit 2 and "REJECTED" in output.

### Criterion 6: Doctrine write still happens

**Built:** `write_state.py` writes a durable JSON state file with session objective, next
action, repository facts, and timestamp. It commits with the close_commit marker. The state
file is tracked in the commit.

**Test:** `write_state_cases()` — runs `write_state.py`, verifies the state file exists,
contains the correct objective/next-action/purpose, the commit moved HEAD, the commit message
contains "RITUAL:", and the state file is tracked. Also verifies that a config without
`state_file` fails rather than writing nothing.

### Criterion 7: Band rotation is out of scope

**Built:** `im-down/SKILL.md` boundary-limits section now states: "Band rotation (removing
stale session-band index stubs from the state file) is out of scope. The convention is
carried as prose in the project's state file, not enforced by this skill. No enforcing
surface exists; the operator manages it manually."

**Test:** The note is in the committed SKILL.md. No automated test pins this prose — the
enforcing surface is the operator's manual process, and no validator reads boundary-limits
section content.

## Mutation

Replacing `deadbeef` in `fixture-stale.md` with a valid-but-wrong SHA does not change the
outcome — the stale-HEAD check still rejects. Removing the RITUAL: marker from the close
commit in `close_commit_cases()` causes the validator to refuse. Removing the state file
commit step from the write_state test causes the packet to record the pre-commit HEAD and
fail produce-mode validation.

## Gate results

All eight validator suites pass:

- `test_validate_card_files.py` — PASS
- `test_validate_skill_formats.py` — PASS
- `test_validate_conformance.py` — PASS
- `test_validate_eval_corpora.py` — PASS
- `test_validate_voice_provenance.py` — PASS
- `test_validate_brand_kit.py` — PASS
- `test_validate_vale_style.py` — PASS
- `test_readme_admission_lead.py` — PASS

Additional suites:
- `test_validate_disposition_counts.py` — PASS
- `test_release_model_disclosure.py` — PASS
- `test_captured_exit_handling.py` — PASS
- Parity suites (im-down, im-up) — both PASS with `, no-drift`
- Stale-HEAD poison control — PASS (REJECTED as expected)
