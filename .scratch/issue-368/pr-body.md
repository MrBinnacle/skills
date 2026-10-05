# #368 — receiver-check cache with weekly full-run audit

Implements the session-boundary design step named in the parent research ticket
(#450, spec step 2 / design D3): the `im-up` open command and the packet
validator now honour an optional `cache_inputs` list on each `receiver_checks`
entry, with a machine-level cache outside the tree and a weekly uncached audit.

## What changed

- `skills/engineering/im-up/validate_packet.py` (shared byte-identical with
  `im-down/validate_packet.py`): `rerun_checks` now keys each cacheable check
  on the blob hashes (sha256 of file bytes) of its `cache_inputs`, the Python
  version, `git --version` and the command string. `~` expands; a directory
  means every file under it. A key that matches its last passing run is not
  re-run. Only passing runs are cached. Checks with no `cache_inputs` always
  run. Every receipt check gains `status` (`passed`, `cached`, `failed`) and
  `duration_ms`. A `cached` entry also carries `cache_key` and `cached_at`.
  Once a week every check runs uncached and is compared with its cached
  verdict; a disagreement fails the open and clears that entry. The cache file
  defaults to `~/.cache/mrbinnacle-skills/receiver-check-cache.json` and can be
  overridden with config key `receiver_check_cache`.
- `skills/engineering/im-up/open_session.py`: unchanged. It already runs receive
  mode through `validate_packet.py`; a cache disagreement surfaces as a
  `REJECTED` verdict and the open fails.
- `skills/engineering/im-up/SKILL.md` and `PACKET-FORMAT.md` (shared): document
  `status`, `duration_ms`, `cache_inputs`, the weekly audit, and what `cached`
  promises.
- `CONFIG.example.json` (shared): example check carrying `cache_inputs`.
- `im-up/gotchas.md`: appended `[ANTICIPATED]` entry for a check that reads a
  path it did not declare.
- `im-up/EVIDENCE.md`: names the new fixture classes; enforcement note records
  the cache contract.
- `scripts/standing-costs.json`: im-up's new SKILL.md hash (zero-cost procedure;
  token figure stays 0).
- `.changeset/im-up-receiver-check-cache.md`: minor bump for the card change.

Shared files (`validate_packet.py`, `test_validate_packet.py`,
`CONFIG.example.json`, `PACKET-FORMAT.md`) remain byte-identical across the
pair; both suites print `, no-drift`.

## Acceptance criteria

### 1. Changing one byte under `cache_inputs` re-runs that check

Built: the cache key includes sha256 of every file under each `cache_inputs`
path, so one byte changes the key and the last passing run no longer matches.

Test: `cache_hit_and_input_change_cases()` in
`skills/engineering/im-up/test_validate_packet.py` (shared). It runs a counter
check once (`passed`, run-count 1), again unchanged (`cached`, run-count still
1), then writes `locked-v2` into `inputs/locked.txt` and requires `passed`
again with a different `cache_key` and run-count 2.

Observed before the change: the same assertion failed with
`KeyError: 'status'` — the pre-change validator emitted no `status` on receipt
checks and served no cache. After the change the case passes.

Also pinned by `cache_directory_inputs_cases()`: a directory in
`cache_inputs` covers every file under it; a byte in `inputs/other.txt` under
`cache_inputs: ["inputs/"]` re-runs the check.

### 2. Changing a file outside every `cache_inputs` re-runs no cached check

Built: the key covers only the declared inputs (plus Python, git version and
command). A change elsewhere leaves the key unchanged, so the cached verdict
is served.

Test: `cache_outside_change_cases()`. After a cached pass it rewrites
`inputs/other.txt` and `outside.txt` (neither declared) and requires the next
receipt to report `status: cached` with run-count still 1.

Observed before: `KeyError: 'status'` on the first status assertion. After:
passes.

### 3. A failing check is never served from cache

Built: `_run_one_check` stores an entry only when `exit_code == 0`. A failing
run is reported `failed` and writes nothing the next lookup can hit.

Test: `cache_failing_never_cached_cases()`. A counter-fail check with
`cache_inputs` runs twice with no change. Both receipts must be `REJECTED`
with `status: failed`, and the side-effect file must show two executions.
Also asserts the cache file holds no checks entry after the first failure.

Observed before: `KeyError: 'status'`. After: both runs execute and fail.

### 4. A planted disagreement is caught by the weekly full run, which fails the open

Built: `weekly_full_due()` treats a missing or >7-day-old `last_full_run_at` as
due. On a due run every check executes uncached; if a cache entry recorded a
pass for the current key and the fresh run is non-zero, `rerun_checks` returns
a `receiver check cache disagreement` error, pops that entry, and the open
rejects.

Test: `cache_weekly_disagreement_cases()`. Closes a session so `open_session.py`
has durable state, opens once while the flag file exists (pass, cache
populated), ages `last_full_run_at` eight days, deletes `flag-ok` — outside
`cache_inputs` — and opens again. Requires exit 2, `verdict: REJECTED`, an
error containing `cache disagreement` and the check name, and an empty
`checks` map in the cache file.

Observed before: `KeyError: 'status'`. After: the open fails for the planted
disagreement and the stale entry is cleared.

### 5. A config with no `cache_inputs` keeps prior fields, plus `status` and `duration_ms`

Built: checks without `cache_inputs` always run; the receipt still carries
`name`, `command`, `exit_code`, and `output` (pass) or `stdout`/`stderr`
(fail). New fields `status` and `duration_ms` are always present. No cache
file is opened when no check declares `cache_inputs` and no
`receiver_check_cache` is set.

Test: `cache_no_inputs_fields_cases()`. Green config: `status: passed`,
integer `duration_ms`, prior fields intact, no `cache_key`/`cached_at`, cache
path not created. Red config: `status: failed`, non-zero `exit_code`,
`duration_ms` present, diagnostic fields present.

Observed before: `KeyError: 'status'`. After: passes. Existing suite cases
(assertions-held, close-session, open-session, red-check) still pass unchanged.

### 6. `test_validate_packet.py` passes; card documentation states `cached`

Built: `SKILL.md` section "Receiver-check status and the cache" states that
`cached` means the check was not re-executed on this open, that its verdict is
the last passing run under the same key, that only passing runs are cached,
that a check with no `cache_inputs` always runs, and that the weekly full run
audits and fails the open on disagreement. `PACKET-FORMAT.md` carries the full
contract including the cache file location outside the tree. The revisit
condition did not fire: the card can carry this without changing what it
promises — a failing check still fails the open, and the weekly audit is the
backstop for a stale cache. No wrapper-command fallback was needed.

Test: both card suites print the full PASS roster including `cache-hit`,
`cache-outside`, `cache-directory`, `cache-fail`, `cache-weekly`,
`cache-no-inputs`, `cache-expand`, and `, no-drift`.

Observed before: suite failed at the first cache case (`KeyError: 'status'`)
and parity was not yet restaged. After: both suites green with no-drift.

## Which test covers which criterion

| Criterion | Test |
|---|---|
| 1 byte under cache_inputs re-runs | `cache_hit_and_input_change_cases`, `cache_directory_inputs_cases` |
| 2 outside change re-runs nothing cached | `cache_outside_change_cases` |
| 3 failing check never cached | `cache_failing_never_cached_cases` |
| 4 weekly disagreement fails the open | `cache_weekly_disagreement_cases` |
| 5 no cache_inputs → prior fields + status/duration_ms | `cache_no_inputs_fields_cases` |
| 6 suite green + docs state `cached` | full PASS roster; `SKILL.md` + `PACKET-FORMAT.md` |

## Mutation campaign

The ticket does not name a mutation receipt, so `scripts/mutation_receipt.py`
was not run and no receipt was written under `docs/assurance/`. The named
assertions that would kill a cache regression are the run-count checks in
criteria 1–3, the `status`/`duration_ms` assertions in criterion 5, and the
`cache disagreement` / cleared-entry assertions in criterion 4. A monkeypatch
of `rerun_checks` would not satisfy those criteria: each case drives the
shipped CLI (`validate_packet.py --mode receive` or `open_session.py`) against
a temp repository and a temp cache file.

## Gate evidence

Run on this branch after the final commit:

- `skills/engineering/im-up/test_validate_packet.py` — PASS roster includes
  every cache case, `, no-drift`.
- `skills/engineering/im-down/test_validate_packet.py` — same roster, `, no-drift`.
- Poison control: `validate_packet.py fixture-stale.md --mode produce` exits 2
  with `REJECTED`.
- `scripts/validate_card_files.py`, `validate_scoreboard.py`,
  `validate_eval_corpora.py`, `validate_skill_formats.py`,
  `validate_voice_provenance.py`, `validate_brand_kit.py`,
  `validate_conformance.py`, `validate_path_residue.py`,
  `check_prose_claims.py`, `validate_site_links.py`,
  `validate_standing_costs.py`, `validate_disposition_counts.py` — all PASS.
- Matching `scripts/test_*.py` suites — PASS lines present.
- `pre-commit run --all-files` — residue, quarantine-landing, vale-style,
  vale-prose all Passed.

## Companion artifacts

- Parent research ticket: #450 (named in the ticket text; this container has no
  GitHub token, so the tracker was not fetched from the network).
- Design reference: spec step 2 / design D3, as named in the ticket.
- Changeset: `.changeset/im-up-receiver-check-cache.md`.
- No `docs/assurance/` receipt: the ticket names no mutation-receipt obligation.
