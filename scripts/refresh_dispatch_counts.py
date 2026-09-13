#!/usr/bin/env python3
"""Rewrite each published card's Dispatches recorded row from the usage log.

Reads the JSONL usage log (one JSON object per line) and rewrites every
published card's EVIDENCE.md dispatch row with the current count and the
measurement date of the newest record consumed. The log path is read from
SKILL_USAGE_LOG when set; otherwise it defaults to
../skills_research/.claude/state/skill-usage-log.jsonl relative to the
repository root, which is correct for a checkout beside its sibling.

When the log is absent or unreadable: change no card, print one line saying
the log was not found and at which path, and exit 0. A stranger running
the harvest step sees an honest skip.

When the log is present but contains no record for a card: write a row that
says zero, dated. Never leave the previous figure standing.

Record kinds:
  baseline — first record, absolute lifetime totals in "counts.skillUsage".
  delta    — every later record, per-session changes in "deltas.skillUsage".
  anomaly  — counter went backwards; skipped, count reported.

The total for one card is its value in the baseline counts plus every delta,
keyed by the card's directory name. A key absent from a record contributes
zero. Only skillUsage is read; pluginUsage counts plugin loads, not card
dispatches.

The date written into a row is the ts of the newest record consumed, not
today's date.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# The dispatch row in EVIDENCE.md is the one this script owns.
DISPATCH_ROW_HEADER = "Dispatches recorded"
# Regex matching the full table row containing the dispatch value.
_DISPATCH_ROW_RE = re.compile(
    r"^\| \*\*Dispatches recorded\*\* \|.*\|$", re.MULTILINE
)

# The boilerplate suffix shared by all nonzero dispatch rows. The prefix
# (count + "dispatches, ...") varies; the suffix is constant.
_NONZERO_SUFFIX = (
    "Demand evidence only: slash + model Skill invocations, summed lifetime, "
    "not deduplicated by working occasion, blind to hook-injected and "
    "always-loaded firings. Summed lifetime is the chosen reading because the "
    "counter predates the per-session delta log (2026-08-16), so a lifetime "
    "per-session figure is not derivable. Never recurrence, lift, or worth."
)

# The zero row's prose. It is deliberately standardised: a tautology stated
# only so the row is not blank.
_ZERO_PREFIX = "No recorded dispatch, measured {date}."
_ZERO_SUFFIX = "Demand evidence only: never recurrence, lift, or worth."


def _parse_log(log_path: Path) -> tuple[dict[str, int], str | None, int]:
    """Parse the JSONL usage log.

    Returns (skill_counts, newest_ts, anomaly_count).

    skill_counts: skill name → total dispatch count (baseline + deltas).
    newest_ts: ISO-8601 timestamp of the newest record consumed, or None
               if the log was empty.
    anomaly_count: number of anomaly records skipped.
    """
    counts: dict[str, int] = {}
    newest_ts: str | None = None
    anomaly_count = 0

    for line_no, raw_line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            print(f"WARN: {log_path}:{line_no}: unparseable JSON, skipping", file=sys.stderr)
            continue

        kind = record.get("kind", "")
        ts = record.get("ts", "")

        if kind == "anomaly":
            anomaly_count += 1
            continue

        if kind == "baseline":
            skill_map = record.get("counts", {}).get("skillUsage", {})
        elif kind == "delta":
            skill_map = record.get("deltas", {}).get("skillUsage", {})
        else:
            # Unknown kind — skip, but do not count as anomaly.
            continue

        for key, value in skill_map.items():
            # Only match bare skill names, not plugin:skill form.
            if ":" in key:
                continue
            counts[key] = counts.get(key, 0) + int(value)

        if ts and (newest_ts is None or ts > newest_ts):
            newest_ts = ts

    return counts, newest_ts, anomaly_count


def _format_date(ts: str) -> str:
    """Extract YYYY-MM-DD from an ISO-8601 timestamp."""
    # Handle both "2026-08-16T19:40:42Z" and "2026-08-16T19:40:42+00:00".
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d")


def _make_row(count: int, date: str) -> str:
    """Build the replacement dispatch row string."""
    if count == 0:
        prefix = f"No recorded dispatch, measured {date}."
        return f"| **Dispatches recorded** | {prefix} {_ZERO_SUFFIX} |"
    prefix = f"{count} dispatches, lifetime platform counter, measured {date}."
    return f"| **Dispatches recorded** | {prefix} {_NONZERO_SUFFIX} |"


def find_cards(repo_root: Path) -> list[Path]:
    """Find all published skill directories."""
    import sys as _sys
    # Import validate_scoreboard to get the bucket set.
    _sys.path.insert(0, str(SCRIPT_DIR))
    import validate_scoreboard as scoreboard

    skills = repo_root / "skills"
    if not skills.is_dir():
        return []
    return sorted(
        card
        for bucket in skills.iterdir()
        if bucket.is_dir()
        and not bucket.name.startswith(".")
        and bucket.name not in scoreboard.UNSHIPPED_BUCKETS
        for card in bucket.iterdir()
        if card.is_dir()
    )


def _skill_name_from_path(card: Path) -> str:
    """The card's directory name — the key to match in skillUsage."""
    return card.name


def rewrite_dispatch_row(evidence: Path, count: int, date: str) -> bool:
    """Rewrite the dispatch row in an EVIDENCE.md file.

    Returns True if the file was changed, False if the row was not found.
    """
    text = evidence.read_text(encoding="utf-8")
    new_row = _make_row(count, date)
    new_text, n = _DISPATCH_ROW_RE.subn(new_row, text, count=1)
    if n == 0:
        return False
    if new_text != text:
        evidence.write_text(new_text, encoding="utf-8")
        return True
    return False


def resolve_log_path(repo_root: Path) -> Path | None:
    """Resolve the usage log path from env or default.

    Returns None when the log does not exist.
    """
    env = os.environ.get("SKILL_USAGE_LOG", "").strip()
    if env:
        p = Path(env).expanduser()
        if not p.is_absolute():
            p = (repo_root / p).resolve()
        return p if p.is_file() else None

    default = (repo_root / ".." / "skills_research" / ".claude" / "state"
               / "skill-usage-log.jsonl").resolve()
    return default if default.is_file() else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: this repository)",
    )
    args = parser.parse_args()
    repo_root = args.root.resolve()

    log_path = resolve_log_path(repo_root)
    if log_path is None:
        # Determine what path was tried for the skip message.
        env = os.environ.get("SKILL_USAGE_LOG", "").strip()
        if env:
            tried = Path(env).expanduser()
            if not tried.is_absolute():
                tried = (repo_root / tried).resolve()
        else:
            tried = (repo_root / ".." / "skills_research" / ".claude" / "state"
                     / "skill-usage-log.jsonl").resolve()
        print(f"SKIP: usage log not found at {tried}")
        return

    counts, newest_ts, anomaly_count = _parse_log(log_path)

    if anomaly_count:
        print(f"NOTE: skipped {anomaly_count} anomaly record(s)", file=sys.stderr)

    date = _format_date(newest_ts) if newest_ts else "1970-01-01"

    cards = find_cards(repo_root)
    if not cards:
        print("REJECTED: no published cards found", file=sys.stderr)
        raise SystemExit(1)

    changed = 0
    for card in cards:
        evidence = card / "EVIDENCE.md"
        if not evidence.is_file():
            continue
        skill_key = _skill_name_from_path(card)
        count = counts.get(skill_key, 0)
        if rewrite_dispatch_row(evidence, count, date):
            changed += 1
            print(f"  {card.relative_to(repo_root)}: {count} dispatch(es)")

    print(f"PASS: refreshed dispatch rows in {changed}/{len(cards)} card(s)")


if __name__ == "__main__":
    main()
