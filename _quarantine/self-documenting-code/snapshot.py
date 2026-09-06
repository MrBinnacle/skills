#!/usr/bin/env python3
"""Capture a compact Git evidence snapshot before or after a refactor."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_git(repo: Path, *args: str) -> str:
    """Run Git in repo and return stdout, or raise with a useful message."""
    command = ["git", "-C", str(repo), *args]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Git command failed: {' '.join(command)}\n{detail}")
    return result.stdout.rstrip("\n")


def file_digest(path: Path) -> str:
    """Return the SHA-256 digest for one file."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def changed_paths(repo: Path, base: str, staged: bool) -> list[str]:
    """Return sorted paths in the selected Git diff."""
    args = ["diff", "--name-only"]
    if staged:
        args.append("--cached")
    elif base:
        args.append(base)
    output = run_git(repo, *args)
    return sorted(path for path in output.splitlines() if path)


def build_snapshot(repo: Path, base: str, staged: bool) -> dict[str, object]:
    """Build a JSON-safe snapshot with revision, status, stats, and file hashes."""
    repo = Path(run_git(repo, "rev-parse", "--show-toplevel"))
    paths = changed_paths(repo, base, staged)
    diff_args = ["diff"]
    if staged:
        diff_args.append("--cached")
    elif base:
        diff_args.append(base)

    files: list[dict[str, object]] = []
    for relative in paths:
        target = repo / relative
        entry: dict[str, object] = {"path": relative, "exists": target.is_file()}
        if target.is_file():
            entry["bytes"] = target.stat().st_size
            entry["sha256"] = file_digest(target)
        files.append(entry)

    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "repository": str(repo),
        "head": run_git(repo, "rev-parse", "HEAD"),
        "base": base or None,
        "staged": staged,
        "status_short": run_git(repo, "status", "--short").splitlines(),
        "diff_stat": run_git(repo, *diff_args, "--stat"),
        "files": files,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Git repository path")
    parser.add_argument("--base", default="HEAD", help="Diff base revision")
    parser.add_argument("--staged", action="store_true", help="Capture the staged diff")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        snapshot = build_snapshot(Path(args.repo).resolve(), args.base, args.staged)
    except (OSError, RuntimeError) as error:
        print(f"snapshot failed: {error}", file=sys.stderr)
        return 2

    rendered = json.dumps(snapshot, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
