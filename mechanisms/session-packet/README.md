# session-packet

A Pi port of the `im-down` / `im-up` session-boundary packet. The packet format is v1 from
`skills/engineering/im-down/PACKET-FORMAT.md`. The manifest keys stay snake_case. A packet that this
extension produces and fills is `ACCEPTED` by `validate_packet.py` in produce mode and in receive
mode. This was checked once against a real repository. The reverse direction (a Python-produced
packet opened here) was not tested end to end; the Python fixtures pass the structure rules.

## Deliberate deviations from the Python contract

1. **No receiver-check cache and no weekly uncached audit.** `cache_inputs` and
   `receiver_check_cache` are not supported. Every receiver check runs on every open and every close,
   so a check's `status` is only `passed` or `failed`, never `cached`.
2. **No state file and no close commit.** `/packet-close` never commits. It follows the
   `snapshot_state.py` path, where the project owns its own close. The project commits its close
   first. Then `/packet-close` measures that HEAD. The `closeCommit.contains` and unclaimed-HEAD
   refusals enforce this order (with `chain` on, the chain checks replace the unclaimed-HEAD
   refusal). Because no state file exists, `/packet-open` does not return a `state_read`.
3. **`status_porcelain` is checked.** `validate_packet.py` records it but never compares it. This
   port compares it with the live tree after trimming whitespace, and a mismatch is `status drift`. The
   packet directory is excluded from both the recorded value and the compared value
   (`git status --porcelain -- . ':(exclude)<dir>'`). Without this exclusion, the packet file would
   make its own packet stale. With a branch store, the store's worktree is excluded too. With
   `headPolicy: "ancestor"`, the status is compared only while HEAD is unchanged.
4. **The fill cannot change the measured facts.** In produce mode, validation of the filled packet
   also refuses a change to `packet_id`, `created_at`, `repository` or `tests`. These are the values
   that `/packet-close` measured. With `chain` on, `previous_packet_id` is a measured fact too.
5. **Receiver checks and trusted command probes run through `sh -c`.** On Windows, `sh` resolves to
   Git's `sh.exe`. `bash` can resolve to WSL's `System32\bash.exe`. Python's `shell=True` uses
   `cmd.exe`.
6. **Receive mode needs a `sessionPacket` section** in `.pi/engineering-env.json`. This replaces
   Python's `--config`. The section may be empty (`{}`). The unclaimed-HEAD check is on unless
   `chain` is on, because the packet store always has a value (default: the directory
   `.pi/session-packets`).
7. **An unreadable packet** (no markers, bad JSON, git failure) returns `{verdict, errors}` only.
   Python behaves the same way.
8. **Opt-in extensions.** `headPolicy`, `chain`, `parked[]` and the branch store (next section) have
   no counterpart in the Python scripts. With none of them configured, this port behaves exactly as
   items 1 to 7 describe. `validate_packet.py` ignores the extra manifest keys, so it still reads a
   packet that carries them, but it checks none of them.

## Opt-in configuration

Every key below is optional. Leaving a key out keeps today's behaviour.

| Key | Values | Default | Effect |
|---|---|---|---|
| `headPolicy` | `"exact"` or `"ancestor"` | `"exact"` | How receive mode judges a packet HEAD that differs from the current HEAD. Produce mode is always exact, so a commit made during the fill still makes the packet stale. |
| `chain` | boolean | `false` | Each packet records `previous_packet_id`. The chain checks replace the unclaimed-HEAD refusal. |
| `store` | `{ "kind": "dir" }` or `{ "kind": "branch", "ref": "<branch>", "worktree": "<path>" }` | `{ "kind": "dir" }` | Where packets live. `worktree` defaults to `var/session-log-worktree`, relative to the repository root. |

```json
{
  "sessionPacket": {
    "receiverChecks": [{ "name": "clean-tree", "command": "git diff --quiet && git diff --cached --quiet" }],
    "headPolicy": "ancestor",
    "chain": true,
    "store": { "kind": "branch", "ref": "session-log" }
  }
}
```

### `headPolicy: "ancestor"`

A packet HEAD that equals the current HEAD is checked as in exact mode, including
`status_porcelain`. A packet HEAD that differs is acceptable through the first route that holds.
Each acceptance is a note in the receipt:

1. It is reachable from the current HEAD.
2. It is reachable from origin's default branch (`origin/HEAD`, or `git ls-remote --symref origin
   HEAD` when that ref is not set locally).
3. The packet's branch still exists on origin (`git ls-remote --heads origin`).
4. The packet's branch is absent on origin and its PR merged (the squash-merge case). The probe is
   injectable. By default it runs `gh pr list --state merged --head <branch>`.

When no route holds, the receipt carries one `HEAD drift: packet=<sha> current=<sha>: ...` error. The
error names every route that failed, and it names a vanished HEAD as absent from this repository.
When `gh` cannot run, or origin cannot be reached, the receipt gets a note and the drift stays an
error. A missing tool never turns drift into a pass. A branch change is a note
(`branch changed: ...`), not `branch drift`, so a packet closed on a feature branch can be opened on
main after the merge. While HEAD has moved, `status_porcelain` is not compared, and a note says so.

### `chain: true`

The scaffold records `previous_packet_id`: the `packet_id` of the newest packet in the store, or
`null` for the first packet. The scaffold also gets an empty `parked` array, and the fill
instructions explain it. The unclaimed-HEAD refusal is off, so a session may close again without a
new commit. When two stored packets name the same parent, open and close add a
`two heads: packets A and B both follow P; both are kept` note. Both packets are kept and neither
is refused.

### `parked[]`

A manifest may carry `parked: [{ "kind", "ref", "reason" }]`. Each entry records work set aside for
later. Receive mode probes every entry, and a failed probe rejects the packet like a failed claim
probe.

| `kind` | `ref` | Probe |
|---|---|---|
| `branch-exists` | branch name | `git show-ref --verify refs/heads/<ref>` |
| `remote-branch-exists` | branch name on origin | `git ls-remote --exit-code --heads origin`. An unreachable origin is a note, not an error. |
| `stash-exists` | stash commit SHA, at least 7 hex characters | a prefix match against `git stash list --format=%H` |
| `worktree-exists` | path, relative to the repository root | a match against `git worktree list --porcelain` |

`stash@{n}` is refused in both modes, because the index renumbers when a stash is pushed or dropped.
The refusal names the command that records a stable SHA: `git rev-parse stash@{n}`. A manifest
without `parked` is not checked for it.

### `store: { "kind": "branch", "ref": ... }`

- **Close.** The scaffold is written into a private worktree of the store branch, at `worktree`.
  The worktree is created on first use: from the local store branch, else from `origin/<ref>`, else
  as a new orphan branch. The orphan branch shares no history with the code. Creating it needs
  `git worktree add --orphan`, so an older git is refused with a message naming git 2.42.
  A worktree inside the repository is added to `.git/info/exclude` and to the `status_porcelain`
  exclusion.
- **Publish.** When the fill is `ACCEPTED`, the packet is committed to the store branch as
  `<UTC stamp>-<id8>.md` and pushed to origin. A failed push is a warning, not a refusal. A
  non-fast-forward is resolved by fetch and rebase. The rebase cannot conflict, because every file
  name is unique.
- **Open.** Open fetches `origin/<ref>`. It reads the newest packet from the local store branch and
  from origin's, whichever holds the newer name. A local store commit that is not on origin is
  reported as a `packet unpushed: ...` note. A failed fetch is a note too.
- **The store bypasses the repository's hooks.** The store commit and push run with `--no-verify`,
  and nothing else in this extension does. The repository's hooks are written for the code tree,
  and in the orphan tree, which has no hook config, a framework such as pre-commit fails every
  store commit. The gate on those bytes is this extension's own scan. The packet's blob is
  written, then scanned, then staged, so the bytes scanned are the bytes committed. A possible
  secret or an email address refuses the commit, and nothing is committed or pushed. A repository
  that needs more should add its scan as a receiver check.
- The remote is always `origin`. In branch mode, `dir` is unused except as a status exclusion. An
  abandoned, unfilled scaffold stays uncommitted in the worktree. It never enters the store, so it
  claims no HEAD.

## Commands

- `/packet-close <objective…>` does these steps in order:
  1. Refuses an empty objective.
  2. Runs every receiver check. If one is red, it refuses and writes no file. The refusal JSON lists
     `failed_receiver_checks` with the output of each failed check.
  3. Refuses when HEAD lacks the `closeCommit` marker or when a prior packet already claims HEAD. It
     makes this check before the agent spends a turn on the fill.
  4. Writes a scaffold to `<dir>/<UTC stamp>-<id8>.md` (or, with a branch store, into the store's
     worktree). The scaffold contains the measured repository facts and the `tests[]` entries.
     `__REQUIRED__` markers stand in for the narrative.
  5. Sends the agent a user message that asks it to fill the scaffold.

  When the agent stops (`agent_before_settle`), the extension validates the file in produce mode. An
  `ACCEPTED` receipt goes to the operator. With a branch store, the packet is committed and pushed
  first, and the operator also gets the publish result. A `REJECTED` receipt goes back to the agent
  as a continuation, at most twice. After that, the extension gives up and reports the rejection as an
  error.
- `/packet-open [path]` validates the latest packet (or the packet at `path`) in receive mode. It
  notifies the operator with the receipt JSON and also posts the receipt into the session.
- `session_start` (reasons startup, new and resume) runs the same check as `/packet-open`. It runs
  only when the project declares `sessionPacket` and a packet exists. It reports the verdict through
  `ctx.ui.notify`, or through stderr when no UI exists. An exception is reported and never thrown.

### Why two steps for the close

Only the model can write the narrative and the claims, so the close cannot be one mechanical
command. The extension keeps the refusals mechanical. All measurement and refusal happens before the
model is asked to write anything. Validation runs when the agent stops, and nobody needs to remember
to run it. If the agent leaves a scaffold unfinished, that scaffold still claims HEAD, as in Python.
Delete the scaffold, or close again after a new commit.

## Layout

The core modules import nothing from Pi. Process execution is injected as `Exec`, which has the same
shape as `pi.exec`.

| File | Role |
|---|---|
| `packet.ts` | Extracts the manifest. Holds the structure, placeholder and recorded-check rules and the always-zero lint. |
| `repo.ts` | Holds the git assertions (branch, HEAD, porcelain status, path/commit/command probes), the close-commit check, the unclaimed-HEAD check and the shell runner. |
| `head.ts` | Holds the `ancestor` head policy and the default `gh` squash-merge probe. |
| `parked.ts` | Holds the receive-mode probes for `parked[]`. |
| `chain.ts` | Holds the packet chain: the newest packet id and the two-heads note. |
| `store.ts` | Holds the dir and branch stores: listing, the private worktree, and publishing. |
| `validate.ts` | Runs the receiver checks and builds the receipt. |
| `close.ts` | Holds the producer: the snapshot and its refusals, the scaffold, the fill instructions and the fill validation. |
| `settings.ts` | Parses the `sessionPacket` config section. |
| `index.ts` | The Pi adapter. |
| `testkit.ts`, `*.test.ts`, `fixtures/` | The bun tests. They run against real temporary git repositories. |

The adapter tests use a fake `ExtensionAPI`. The `agent_before_settle` continuation path has not been
exercised against a live model.
