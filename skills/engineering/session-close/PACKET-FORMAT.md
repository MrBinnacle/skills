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
      "text": "load-bearing claim",
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
