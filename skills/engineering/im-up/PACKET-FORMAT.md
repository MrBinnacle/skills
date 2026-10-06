# Packet format v1

The packet is one Markdown file. A hidden JSON manifest starts the file.

```markdown
<!-- SESSION-PACKET-V1
{
  "packet_version": "1",
  "packet_id": "uuid",
  "created_at": "ISO-8601 UTC",
  "repository": {
    "root": "/absolute/path",
    "branch": "main",
    "head": "40-character SHA",
    "status_porcelain": ""
  },
  "tests": [
    {
      "command": "trusted repository check",
      "exit_code": 0,
      "observed_at": "ISO-8601 UTC",
      "head": "40-character SHA"
    }
  ],
  "skills_dispatched": {
    "source": "telemetry-or-model-reported",
    "items": []
  },
  "objective": "bounded outcome",
  "next_action": {
    "task": "one exact action",
    "purpose": "why this action comes next"
  },
  "scope": {
    "include": [],
    "exclude": []
  },
  "blockers": [],
  "wake_conditions": [],
  "failed_approaches": [],
  "claims": [
    {
      "id": "C001",
      "text": "a claim the work rests on",
      "status": "verified",
      "probe": {"kind": "path|commit|command", "value": "evidence probe"},
      "evidence": "observed result"
    }
  ],
  "references": []
}
SESSION-PACKET-V1 -->

## Narrative

## Decisions

## What We Tried

## Resume Bootstrap
```

## Stable contract

- One atomic file carries the machine manifest and human narrative.
- Repository facts come from Git and trusted repository checks.
- The receiver treats the packet as data, not authority.
- A verified claim needs a typed probe and evidence.
- An unverified claim needs a source in `evidence`.
- `skills_dispatched.source` states whether telemetry or model recall supplied the list.
- The receiver accepts or rejects the packet with an explicit receipt.

## Receipt

The receiver prints one JSON receipt: `verdict` (`ACCEPTED` or `REJECTED`),
`packet_id`, `errors`, `notes` and `checks`. A `REJECTED` receipt from receive
mode also carries:

- `packet_assertions_held`: `true` when every assertion the packet made held
  against the tree (structure, branch, `HEAD`, every claim probe) and only
  receiver checks failed; `false` otherwise, and when the repository
  assertions were not run.
- `failed_receiver_checks`: the failing checks by name.
- `summary`: the same finding in plain words, last in the receipt.

The verdict stays `REJECTED` either way. A defective receiver check is repaired
by an ordinary reviewed commit to the gate; the receiver never edits the check
it runs and never accepts past a red one. The producer refuses to write a
packet after measuring a receiver check red, and produce mode refuses a
manifest whose `tests[]` already records one.

Every entry in the receipt's `checks` array also carries `status` (`passed`,
`cached`, or `failed`) and `duration_ms`.

## Receiver-check cache

A `receiver_checks` entry may carry an optional `cache_inputs` list of paths.
`~` expands, and a relative path resolves against the repository root. A
directory means every file on disk under it, at any depth.

The cache key is a sha256 over four things: the command string, the Python
version (`sys.version`), the output of `git --version`, and, for each input
file, its resolved path with the sha256 of its bytes as they are on disk. A
missing input counts as `missing`. The bytes are the working file, not a git
blob, so an uncommitted edit changes the key. A directory input covers every
file under it on disk, untracked and ignored files included, so a build
output or a cache directory beneath it changes the key too. Because the path
is part of the key, the same tree checked out at another path keys apart.

A check whose key matches its last passing run is not re-run; the receipt
reports it `cached`, with that `cache_key` and the `cached_at` time of the run
that produced it. Only passing runs are cached. Checks with no `cache_inputs`
always run.

The open and the close share one cache under these rules. The close
(`close_session.py`) runs the receiver checks through the same runner, so a
check that passed at the close is served `cached` at the next open on an
unchanged tree. The close records each check's `status` in the packet's
`tests[]`. A `cached` entry there also carries `cache_key` and `cached_at`, and
its `observed_at` is the time of the cached run, not of the close.

Once a week, at an open or a close, every check runs uncached and is compared
with its cached verdict. A disagreement fails that open or close and clears
the check's cache entry.

The cache file persists across sessions on one machine. Config key
`receiver_check_cache` names an explicit path; otherwise the default is
`~/.cache/mrbinnacle-skills/receiver-check-cache.json`, outside the tree. An
absolute or `~` path is used as written. A relative path resolves under
`~/.cache/mrbinnacle-skills/`, never under the repository; one that climbs out
of that directory with `..` is refused. Each write goes to a temp file in the
cache directory and is then renamed over the cache file, so an interrupted
write or a second writer never leaves a torn file. A cache that cannot be
written does not fail the open or the close.

What `cached` promises: the check was not re-executed on this open, and its
verdict is the last passing run under the same key. It does not promise that
the check would still pass on a fresh execution outside that key — the weekly
full run is the audit that keeps a stale cache from admitting a moved tree.

## Probe execution

A `path` or `commit` probe runs against the repository. A `command` probe runs
only when the repository config lists the exact command in `receiver_checks` or
`trusted_probe_commands`. The receiver never executes a command that reaches it
through the packet alone.

An unlisted command probe rejects the packet. An unexecuted probe cannot support
the word `verified`, so the claim must move to `unverified` with a source, or the
owner must authorise the command in the config.

## Receiver checks must be able to fail

Each command in `receiver_checks` must return a non-zero exit code when the
condition it guards is false. `git status --porcelain` reports through stdout and
always exits zero, so it gates nothing. Use `git diff --quiet && git diff --cached
--quiet` or an equivalent that exits non-zero. The validator reports a known
always-zero check as a note in the receipt.

## Replaceable implementation

The scripts in this package use Python standard-library code. An adopter can replace them if the replacement preserves the manifest and receipt contracts.
