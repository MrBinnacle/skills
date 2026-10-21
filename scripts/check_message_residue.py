#!/usr/bin/env python3
"""Refuse a commit message, PR title or PR body that carries a de-personalization term.

WHY THIS EXISTS

    The pygrep hooks in `.pre-commit-config.yaml` read tracked FILES. A commit
    message is not a file in the tree, so a private codename in a message passed
    every hook and reached `main`: 14 commits on `main` carry one (for example
    122464d and 5f68de4), and a squash merge copies the PR title into history.
    A commit message is as public as a file once the branch is pushed.

ONE TERM SOURCE

    The patterns are the `entry` of every `residue-` pygrep hook in
    `.pre-commit-config.yaml`, read by `parse_hooks`. No term is copied here, so
    a codename hook added to the yaml is enforced on messages with no second
    edit. The refusal quotes the hook's `name`, which carries the replacement.
    The `leak-` account-data hooks are not applied: they guard trace VALUES, and
    a message that names a field it scrubbed leaks nothing.

    A private name that is deliberately absent from the yaml (the yaml says why:
    a public block-list would itself de-anonymize) is not caught here either.
    Keep such terms in a git-ignored local overlay.

Usage:
    python scripts/check_message_residue.py --range BASE..HEAD   # every commit message in the range
    python scripts/check_message_residue.py FILE [FILE ...]      # text files read whole (a PR title and body)
    python scripts/check_message_residue.py --commit-msg FILE    # the commit-msg hook; skips git's "# " help lines
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = REPO_ROOT / ".pre-commit-config.yaml"


def parse_hooks(config: Path = CONFIG) -> dict[str, dict[str, str]]:
    """Read id, name, entry, types, files and the resolved exclude of every pygrep hook."""
    text = config.read_text(encoding="utf-8")
    anchors: dict[str, str] = {}
    for name, value in re.findall(r"exclude: &(\w+) '([^\n]*)'\n", text):
        anchors[name] = value
    hooks: dict[str, dict[str, str]] = {}
    for block in re.split(r"^      - id: ", text, flags=re.M)[1:]:
        hook_id = block.split("\n", 1)[0].strip()
        fields: dict[str, str] = {}
        for line in block.splitlines()[1:]:
            m = re.match(r"^        (name|entry|types|files|language): (.*)$", line)
            if m:
                fields[m.group(1)] = m.group(2).strip()
            m = re.match(r"^        exclude: (?:&\w+ )?('(.*)'|\*(\w+))\s*$", line)
            if m:
                fields["exclude"] = m.group(2) if m.group(2) is not None else anchors[m.group(3)]
        if fields.get("language") == "pygrep":
            entry = fields["entry"]
            assert entry.startswith("'") and entry.endswith("'"), (hook_id, entry)
            fields["entry"] = entry[1:-1].replace("''", "'")
            fields["name"] = fields.get("name", hook_id).strip('"')
            hooks[hook_id] = fields
    return hooks


def message_breaches(label: str, message: str, hooks: dict[str, dict[str, str]]) -> list[str]:
    """One line per (message line, hook) match, naming the replacement the hook's name gives."""
    out: list[str] = []
    for number, line in enumerate(message.splitlines(), 1):
        for hook_id, fields in hooks.items():
            m = re.search(fields["entry"], line)
            if m:
                out.append(f"{label}:{number}: {hook_id} matched '{m.group(0)}'. Reword: {fields['name']}")
    return out


def commit_msg_text(path: Path) -> str:
    """The commit-msg file with git's `# ` help lines blanked, so line numbers still match."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join("" if line.startswith("# ") else line for line in lines)


def range_messages(spec: str) -> list[tuple[str, str]]:
    """(short sha, full message) for every commit in a `git log` range of the current repository."""
    result = subprocess.run(
        ["git", "log", "--format=%h%x00%B%x01", spec],
        capture_output=True,
        check=True,
    )
    pairs = []
    for record in result.stdout.decode("utf-8", "replace").split("\x01"):
        record = record.strip("\n")
        if record:
            sha, _, body = record.partition("\x00")
            pairs.append((sha, body))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--range", dest="spec", help="a git log range, BASE..HEAD")
    parser.add_argument("--commit-msg", type=Path, help="the message file git hands a commit-msg hook")
    parser.add_argument("files", nargs="*", type=Path, help="text files read whole, such as a PR title and body")
    args = parser.parse_args()
    if not (args.spec or args.commit_msg or args.files):
        parser.error("give --range, --commit-msg or at least one file")

    hooks = {hook_id: f for hook_id, f in parse_hooks().items() if hook_id.startswith("residue-")}
    messages = [(str(f), f.read_text(encoding="utf-8", errors="replace")) for f in args.files]
    if args.commit_msg:
        messages.append((str(args.commit_msg), commit_msg_text(args.commit_msg)))
    if args.spec:
        messages += range_messages(args.spec)

    breaches = [b for label, text in messages for b in message_breaches(label, text, hooks)]
    for breach in breaches:
        print(f"  - {breach}")
    if breaches:
        print(
            f"REJECTED: {len(breaches)} residue term(s) in {len(messages)} message(s). "
            "A pushed commit message is public; reword it before push (an unpushed commit: "
            "`git commit --amend`; a PR title or body: edit it on GitHub)."
        )
        return 1
    print(f"PASS: {len(messages)} message(s) read against {len(hooks)} residue hook pattern(s), no residue term")
    return 0


if __name__ == "__main__":
    sys.exit(main())
