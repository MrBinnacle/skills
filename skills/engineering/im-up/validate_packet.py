#!/usr/bin/env python3
"""Validate one session-boundary packet with Python standard-library code."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

START = "<!-- SESSION-PACKET-V1"
END = "SESSION-PACKET-V1 -->"
REQUIRED = [
    "packet_version", "packet_id", "created_at", "repository", "tests",
    "skills_dispatched", "objective", "next_action", "scope", "blockers",
    "wake_conditions", "failed_approaches", "claims", "references",
]
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
SCAFFOLD_MARKER = "__REQUIRED__"
PLACEHOLDER_TOKENS = ("TODO", "TBD")
LIST_PREFIX = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|>\s*)*")
# A receiver check signals through stdout and always exits zero, so it cannot
# fail and cannot gate anything. Name the known instance rather than guess.
UNFAILABLE_CHECK = re.compile(r"^\s*git\s+status(\s+--porcelain(=\S+)?)*\s*$")


class PacketError(ValueError):
    pass


def run(cmd: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True)


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise PacketError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def extract(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < 0 or end <= start:
        raise PacketError("packet markers are absent or out of order")
    raw = text[start + len(START):end].strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PacketError(f"manifest is not valid JSON: {exc}") from exc
    return data, text


def nonempty(value) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)


def is_placeholder_line(line: str) -> bool:
    """True when the line carries a placeholder token and nothing else."""
    stripped = LIST_PREFIX.sub("", line).strip().strip("*_`#").strip()
    return stripped.rstrip(":.").strip().upper() in PLACEHOLDER_TOKENS


def placeholder_tokens(data: dict, text: str) -> set[str]:
    """Return the placeholder tokens that are genuinely placeholders.

    A mention of TODO inside narrative prose - a quoted ticket title, a file
    path, a sentence about removing them - is legitimate content, and rejecting
    it teaches the producer to censor honest narrative. Only a whole-line
    placeholder, or a manifest value that is nothing but the token, is evidence
    of unfinished work.
    """
    found: set[str] = set()
    for line in text.splitlines():
        if is_placeholder_line(line):
            upper = line.upper()
            found.update(token for token in PLACEHOLDER_TOKENS if token in upper)
    for value in walk_strings(data):
        candidate = value.strip().rstrip(":.").strip().upper()
        if candidate in PLACEHOLDER_TOKENS:
            found.add(candidate)
    return found


def trusted_commands(config: dict | None) -> set[str]:
    """Commands the repository owner has authorised, never the packet itself."""
    if not config:
        return set()
    commands = {
        check["command"] for check in config.get("receiver_checks", [])
        if isinstance(check, dict) and "command" in check
    }
    commands.update(config.get("trusted_probe_commands", []))
    return commands


def lint_receiver_checks(config: dict) -> list[str]:
    notes: list[str] = []
    for check in config.get("receiver_checks", []):
        command = check.get("command", "") if isinstance(check, dict) else ""
        if UNFAILABLE_CHECK.match(command):
            notes.append(
                f"receiver check '{check.get('name', command)}' always exits zero, "
                f"so it cannot fail and gates nothing: {command}"
            )
    return notes


def validate_close_commit(config: dict | None, repo_root: Path) -> list[str]:
    """Refuse a packet whose HEAD is not the session-close commit.

    A session close has two halves and their order is fixed by a constraint, not
    a preference: the durable close commits, and only THEN may the packet record
    HEAD. Produced in the other order, the close moves HEAD out from under a
    packet that has already recorded it, and the receiver rejects that packet as
    stale in the NEXT session -- the worst place to discover it.

    Documenting the order does not hold, because the person typing the second
    command cannot see the effect of the first. So the ordering is checked here
    instead of asked for in prose.

    Opt-in by config: with no `close_commit.contains` declared this returns
    nothing, so a project with no close ritual is unaffected. The marker stays
    the project's to define -- this validator ships to projects whose close
    vocabulary it cannot know.

    `contains` is a literal substring test, not a regex. The name says so on
    purpose: called `pattern`, a project would reasonably write "^RITUAL:" and
    get a check that silently refuses every packet forever.

    Known limit, closed elsewhere: this establishes that HEAD is A close
    commit, not that it is THIS session's. The revisit condition named here
    fired -- validate_unclaimed_head consults the packet directory for an
    already-claimed HEAD, which makes the stale close detectable. Both checks
    stay, because each refuses a case the other cannot see: a HEAD that is not
    a close commit at all sails past the unclaimed-head check whenever no
    prior packet happens to record it.
    """
    requirement = (config or {}).get("close_commit") or {}
    marker = requirement.get("contains")
    if not marker:
        return []
    message = git(repo_root, "log", "-1", "--pretty=%B")
    if marker in message:
        return []
    return [
        f"HEAD is not the close commit: its message does not carry {marker!r}. "
        "Close first, then produce the packet -- a packet made before the close "
        "records a HEAD the close then moves."
    ]


def validate_unclaimed_head(
    config: dict | None, repo_root: Path, packet_path: Path
) -> list[str]:
    """Refuse a packet whose HEAD the most recent prior packet already claimed.

    The session boundary validate_close_commit lacks: the marker test proves
    HEAD is A close commit, not THIS session's, so a session that committed
    nothing sits on the previous close and passes it. The packet directory
    supplies the boundary -- every produced packet records repository.head, so
    a HEAD equal to the most recent prior packet's recorded head is the
    PREVIOUS session's close. A packet produced there goes stale the moment
    this session closes, and the receiver rejects it at the next open, which
    is the worst place to discover it.

    The packet under validation is excluded from the comparison: the producer
    may write the file into the directory before validating it, and a packet
    must not refuse itself for claiming the HEAD it correctly records.

    The scan walks the directory newest-first and compares against the first
    file that parses as a packet and records a head. Taking the raw filename
    maximum instead would let one stray file -- a README sorts after digit-led
    timestamp names -- become "newest", fail to parse, and disable the guard
    silently and permanently, reopening the exact hole this check closes.

    Opt-in by config: with no packet_dir declared this returns nothing.

    Known limit, accepted as smaller than the hole it closes: with no usable
    prior at all -- an empty packet directory, or nothing in it that parses
    and records repository.head -- this degrades to the previous behaviour
    instead of refusing, because a fresh clone has no prior packet and must
    still be able to produce its first one.
    """
    packet_dir_name = (config or {}).get("packet_dir")
    if not packet_dir_name:
        return []
    packet_dir = Path(packet_dir_name)
    if not packet_dir.is_absolute():
        packet_dir = repo_root / packet_dir
    if not packet_dir.is_dir():
        return []
    own = packet_path.resolve()
    priors = sorted(p for p in packet_dir.glob("*.md") if p.resolve() != own)
    if not priors:
        return []
    current_head = git(repo_root, "rev-parse", "HEAD")
    for newest in reversed(priors):
        try:
            prior_data, _ = extract(newest)
        except (OSError, ValueError):
            continue
        if not isinstance(prior_data, dict):
            continue
        repository = prior_data.get("repository")
        claimed = repository.get("head") if isinstance(repository, dict) else None
        if not claimed:
            continue
        if claimed != current_head:
            return []
        return [
            f"HEAD {current_head} is already claimed by prior packet "
            f"{newest.name}: this session has not closed yet. Close first, "
            "then produce -- the close moves HEAD, and a packet made before "
            "it records a HEAD the receiver will reject as stale."
        ]
    return []


def validate_structure(data: dict, text: str) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED:
        if key not in data:
            errors.append(f"missing field: {key}")
    for key in ("packet_id", "created_at", "objective"):
        if key in data and not nonempty(data[key]):
            errors.append(f"empty field: {key}")
    if data.get("packet_version") != "1":
        errors.append("packet_version must equal 1")
    try:
        datetime.fromisoformat(str(data.get("created_at", "")).replace("Z", "+00:00"))
    except ValueError:
        errors.append("created_at must be ISO-8601")
    repo = data.get("repository", {})
    for key in ("root", "branch", "head", "status_porcelain"):
        if key not in repo:
            errors.append(f"missing repository field: {key}")
    next_action = data.get("next_action", {})
    for key in ("task", "purpose"):
        if not nonempty(next_action.get(key)):
            errors.append(f"empty next_action field: {key}")
    skills = data.get("skills_dispatched", {})
    if skills.get("source") not in {"telemetry", "model-reported"}:
        errors.append("skills_dispatched.source must be telemetry or model-reported")
    if not isinstance(skills.get("items"), list):
        errors.append("skills_dispatched.items must be an array")
    for index, test in enumerate(data.get("tests", [])):
        for key in ("command", "exit_code", "observed_at", "head"):
            if key not in test:
                errors.append(f"tests[{index}] lacks {key}")
        if not isinstance(test.get("exit_code"), int):
            errors.append(f"tests[{index}].exit_code must be an integer")
    for index, claim in enumerate(data.get("claims", [])):
        status = claim.get("status")
        if status not in {"verified", "unverified"}:
            errors.append(f"claims[{index}].status is invalid")
        if not nonempty(claim.get("id")) or not nonempty(claim.get("text")):
            errors.append(f"claims[{index}] lacks id or text")
        if status == "verified":
            probe = claim.get("probe", {})
            if probe.get("kind") not in {"path", "commit", "command"} or not nonempty(probe.get("value")):
                errors.append(f"claims[{index}] lacks a typed probe")
            if not nonempty(claim.get("evidence")):
                errors.append(f"claims[{index}] lacks evidence")
        if status == "unverified" and not nonempty(claim.get("evidence")):
            errors.append(f"claims[{index}] lacks a source in evidence")
    if SCAFFOLD_MARKER in text:
        errors.append(f"unfinished marker present: {SCAFFOLD_MARKER}")
    for token in sorted(placeholder_tokens(data, text)):
        errors.append(f"unfinished marker present: {token}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append("possible secret detected")
    for section in ("## Narrative", "## Decisions", "## What We Tried", "## Resume Bootstrap"):
        if section not in text:
            errors.append(f"missing narrative section: {section}")
    return errors


def validate_repository(
    data: dict, repo_root: Path, allowed_commands: set[str] | None = None
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []
    allowed = allowed_commands or set()
    current_head = git(repo_root, "rev-parse", "HEAD")
    current_branch = git(repo_root, "branch", "--show-current")
    expected = data.get("repository", {})
    if expected.get("head") != current_head:
        errors.append(f"stale HEAD: packet={expected.get('head')} current={current_head}")
    if expected.get("branch") != current_branch:
        errors.append(f"branch drift: packet={expected.get('branch')} current={current_branch}")
    for claim in data.get("claims", []):
        if claim.get("status") != "verified":
            continue
        probe = claim.get("probe", {})
        kind, value = probe.get("kind"), probe.get("value")
        if kind == "path" and not (repo_root / value).exists():
            errors.append(f"claim {claim.get('id')} path probe failed: {value}")
        elif kind == "commit":
            result = subprocess.run(["git", "cat-file", "-e", f"{value}^{{commit}}"], cwd=repo_root)
            if result.returncode != 0:
                errors.append(f"claim {claim.get('id')} commit probe failed: {value}")
        elif kind == "command":
            # A command supplied only by the packet is never executed. But an
            # unexecuted probe cannot support the word "verified", so the claim
            # is rejected rather than passed through on an advisory note.
            if str(value) not in allowed:
                errors.append(
                    f"claim {claim.get('id')} command probe is absent from the trusted "
                    f"config allowlist, so a verified status is unsupported: {value}"
                )
                continue
            result = run(str(value), repo_root)
            if result.returncode != 0:
                errors.append(
                    f"claim {claim.get('id')} command probe failed "
                    f"(exit {result.returncode}): {value}"
                )
            else:
                notes.append(f"claim {claim.get('id')} command probe passed: {value}")
    return errors, notes


def rerun_checks(config: dict, repo_root: Path) -> list[dict]:
    results = []
    for check in config.get("receiver_checks", []):
        result = run(check["command"], repo_root)
        results.append({
            "name": check["name"], "command": check["command"],
            "exit_code": result.returncode,
            "stdout": result.stdout[-2000:], "stderr": result.stderr[-2000:],
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--mode", choices=["produce", "receive"], default="produce")
    args = parser.parse_args()
    try:
        data, text = extract(args.packet)
        errors = validate_structure(data, text)
        notes: list[str] = []
        checks: list[dict] = []
        config: dict | None = None
        if args.config:
            loaded = json.loads(args.config.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise PacketError("config must be a JSON object")
            config = loaded
            notes.extend(lint_receiver_checks(config))
        if args.repo_root:
            repo_errors, repo_notes = validate_repository(
                data, args.repo_root.resolve(), trusted_commands(config)
            )
            errors.extend(repo_errors)
            notes.extend(repo_notes)
            if args.mode == "produce":
                # The producer's obligation, checked at the only moment it can
                # still be repaired cheaply. The receiver inherits it: a packet
                # whose HEAD is the close commit stays valid only while nothing
                # commits after it, which the stale-HEAD check already enforces.
                errors.extend(validate_close_commit(config, args.repo_root.resolve()))
                errors.extend(
                    validate_unclaimed_head(config, args.repo_root.resolve(), args.packet)
                )
        if args.mode == "receive":
            # Receive mode without a config used to skip every configured check
            # in silence and still return ACCEPTED. A verification that can be
            # switched off by omitting an argument is not a verification.
            if config is None or args.repo_root is None:
                errors.append("receive mode requires --config and --repo-root")
            else:
                checks = rerun_checks(config, args.repo_root.resolve())
                for check in checks:
                    if check["exit_code"] != 0:
                        errors.append(f"receiver check failed: {check['name']}")
        receipt = {
            "verdict": "REJECTED" if errors else "ACCEPTED",
            "packet_id": data.get("packet_id"),
            "errors": errors,
            "notes": notes,
            "checks": checks,
        }
        print(json.dumps(receipt, indent=2))
        return 2 if errors else 0
    except (OSError, PacketError, json.JSONDecodeError) as exc:
        print(json.dumps({"verdict": "REJECTED", "errors": [str(exc)]}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
