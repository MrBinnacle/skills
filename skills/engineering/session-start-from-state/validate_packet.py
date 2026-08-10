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
    for marker in ("__REQUIRED__", "TODO", "TBD"):
        if marker in text:
            errors.append(f"unfinished marker present: {marker}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            errors.append("possible secret detected")
    for section in ("## Narrative", "## Decisions", "## What We Tried", "## Resume Bootstrap"):
        if section not in text:
            errors.append(f"missing narrative section: {section}")
    return errors


def validate_repository(data: dict, repo_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []
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
            notes.append(f"claim {claim.get('id')} command probe requires trusted config: {value}")
    return errors, notes


def rerun_checks(config_path: Path, repo_root: Path) -> list[dict]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
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
        if args.repo_root:
            repo_errors, notes = validate_repository(data, args.repo_root.resolve())
            errors.extend(repo_errors)
        if args.mode == "receive" and args.config and args.repo_root:
            checks = rerun_checks(args.config, args.repo_root.resolve())
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
