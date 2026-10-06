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

When a row is already a zero form ("No recorded dispatch"), only the
measurement date is moved. Card-specific diagnosis — hook-unobservable prose
on pull-rebase and stale-deploy, quarantine tautology prose elsewhere — stays.
Replacing that prose with a generic zero would erase the harvest pass's
unobservable-vs-insurance discriminator (AGENTS.md step 2).

Record kinds:
  baseline — absolute lifetime totals in "counts.skillUsage". The logger
             writes one on its first run and again whenever it loses its
             cursor; the latest baseline replaces everything before it.
  delta    — every later record, per-session changes in "deltas.skillUsage".
  anomaly  — counter went backwards; skipped, count reported.

The total for one card is the sum, over every telemetry key that names the
card, of that key's value in the latest baseline plus every delta after it. The keys that name a card
are its directory name, each earlier name in EARLIER_NAMES, and each of those
prefixed by the bucket's plugin name (`<plugin.json name>:<name>`), the form
the platform records when the card is invoked from the installed plugin
(plugin skills are namespaced `plugin-name:skill-name`, per
code.claude.com/docs/en/agent-sdk/plugins, checked through Context7
2026-10-05). A key absent from a record contributes zero. Only skillUsage is
read; pluginUsage counts plugin loads, not card dispatches.

The date written into a row is the ts of the newest record consumed, not
today's date. An empty log has no record ts; the date then is the UTC day
the script ran, because a measured clause is required and no log timestamp
exists to prefer.
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

# Regex matching the full table row containing the dispatch value.
_DISPATCH_ROW_RE = re.compile(
    r"^\| \*\*Dispatches recorded\*\* \|.*\|(?=\r?$)", re.MULTILINE
)
_MEASURED_DATE_RE = re.compile(r"measured 20\d{2}-\d{2}-\d{2}")
_ZERO_OPEN_RE = re.compile(r"No recorded dispatch\b")

# The boilerplate suffix shared by all nonzero dispatch rows. The prefix
# (count + "dispatches, ...") varies; the suffix is constant.
_NONZERO_SUFFIX = (
    "Demand evidence only: slash + model Skill invocations, summed lifetime, "
    "not deduplicated by working occasion, blind to hook-injected and "
    "always-loaded firings. Summed lifetime is the chosen reading because the "
    "counter predates the per-session delta log (2026-08-16), so a lifetime "
    "per-session figure is not derivable. Never recurrence, lift, or worth."
)

# Every earlier name a published card was dispatched under, with the record
# that ties the old key to the card. The single place a card's aliases live.
# A key whose link to a card cannot be cited is left out, even when the name
# resembles the card: see UNATTRIBUTED below.
EARLIER_NAMES: dict[str, tuple[tuple[str, str], ...]] = {
    "clirunner-env": (("click-clirunner-env-none-deletes",
                       "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "closure-mode": (("closure-mode-at-boundaries",
                      "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "dead-predicate": (("router-skill-predicate-gap",
                        "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "decision-rights": (("downstream-instruction-framing",
                         "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "disposition-schema": (("parallel-review-disposition-schema",
                            "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "im-down": (("session-close",
                 "git mv in fc5009c (#11): session-close becomes im-down"),),
    "mocked-stub": (("mock-masked-stub-trap",
                     "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "pretooluse-prose": (("pretooluse-bash-guard-prose-false-positive",
                          "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "pull-rebase": (("git-pull-rebase-trap",
                     "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "stale-deploy": (("github-pages-deploy-verification",
                      "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "subagent-handback": (("subagent-research-reliability",
                           "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
    "vacuous-check": (("success-test-accepts-any-output",
                       "git mv in 541522a (#286); CHANGELOG v2.0.0 rename table"),),
}

# Earlier names deliberately not mapped, with the reason. Kept beside the map
# so a later reader does not "fix" the omission.
UNATTRIBUTED: dict[str, str] = {
    "session-start-from-state": (
        "im-up carried this name until fc5009c (#11), which renamed it because "
        "a separate, widely installed local skill holds the same name; the "
        "key's dispatches cannot be split between the two"
    ),
}

# Standard zero form used only when the previous row was nonzero (or had no
# zero opening). Already-zero rows keep their card-specific diagnosis.
_ZERO_SUFFIX = "Demand evidence only: never recurrence, lift, or worth."

# Hook-fired cards (AGENTS.md harvest step 2, branch 1: pull-rebase and
# stale-deploy) say in their own row that the counter cannot see their
# enforcing path. The marker identifies such a row whatever its count, so the
# statement survives a zero-to-nonzero rewrite and comes back on the return.
_UNOBSERVABLE_MARK = "hook and trap mechanisms this counter cannot see"
_UNOBSERVABLE_ZERO = (
    "This card enforces through hook and trap mechanisms this counter cannot "
    "see, so zero means no recorded dispatch, never unused."
)
_UNOBSERVABLE_NONZERO = (
    "This card enforces through hook and trap mechanisms this counter cannot "
    "see, so the figure counts Skill invocations only, never hook firings."
)


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
            # Absolute lifetime totals: a later baseline already contains every
            # earlier record, so it replaces the running totals.
            counts = {}
            skill_map = record.get("counts", {}).get("skillUsage", {})
        elif kind == "delta":
            skill_map = record.get("deltas", {}).get("skillUsage", {})
        else:
            # Unknown kind — skip, but do not count as anomaly.
            continue

        for key, value in skill_map.items():
            counts[key] = counts.get(key, 0) + int(value)

        if ts and (newest_ts is None or ts > newest_ts):
            newest_ts = ts

    return counts, newest_ts, anomaly_count


def _format_date(ts: str) -> str:
    """Extract YYYY-MM-DD from an ISO-8601 timestamp."""
    # Handle both "2026-08-16T19:40:42Z" and "2026-08-16T19:40:42+00:00".
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d")


def _make_row(count: int, date: str, unobservable: bool = False) -> str:
    """Build a full replacement dispatch row (nonzero, or first-time zero)."""
    if count == 0 and unobservable:
        prefix = (f"No recorded dispatch, lifetime platform counter, measured "
                  f"{date}. {_UNOBSERVABLE_ZERO}")
        return f"| **Dispatches recorded** | {prefix} {_NONZERO_SUFFIX} |"
    if count == 0:
        prefix = f"No recorded dispatch, measured {date}."
        return f"| **Dispatches recorded** | {prefix} {_ZERO_SUFFIX} |"
    noun = "dispatch" if count == 1 else "dispatches"
    prefix = f"{count} {noun}, lifetime platform counter, measured {date}."
    if unobservable:
        prefix = f"{prefix} {_UNOBSERVABLE_NONZERO}"
    return f"| **Dispatches recorded** | {prefix} {_NONZERO_SUFFIX} |"


def _row_for(count: int, date: str, existing_row: str) -> str:
    """Choose the replacement row, preserving card-specific diagnosis."""
    unobservable = _UNOBSERVABLE_MARK in existing_row
    if count == 0 and _ZERO_OPEN_RE.search(existing_row):
        # Keep hook-unobservable / quarantine tautology prose; move the date.
        if _MEASURED_DATE_RE.search(existing_row):
            return _MEASURED_DATE_RE.sub(f"measured {date}", existing_row, count=1)
        return _make_row(0, date, unobservable)
    return _make_row(count, date, unobservable)


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
        if card.is_dir() and not card.name.startswith(".")
    )


def _plugin_name(bucket: Path) -> str | None:
    """The bucket's plugin name from .claude-plugin/plugin.json, if present."""
    manifest = bucket / ".claude-plugin" / "plugin.json"
    try:
        name = json.loads(manifest.read_text(encoding="utf-8")).get("name")
    except (OSError, json.JSONDecodeError):
        return None
    return name if isinstance(name, str) and name else None


def telemetry_keys(card: Path) -> list[str]:
    """Every skillUsage key that names this card, current name first."""
    names = [card.name] + [old for old, _ in EARLIER_NAMES.get(card.name, ())]
    names = [n for n in names if n not in UNATTRIBUTED]
    plugin = _plugin_name(card.parent)
    prefixed = [f"{plugin}:{n}" for n in names] if plugin else []
    return names + prefixed


def rewrite_dispatch_row(evidence: Path, count: int, date: str) -> bool:
    """Rewrite the dispatch row in an EVIDENCE.md file.

    Returns True if the file was changed, False if the row was not found
    or the replacement matched the existing text.
    """
    text = evidence.read_text(encoding="utf-8", newline="")
    match = _DISPATCH_ROW_RE.search(text)
    if match is None:
        return False
    existing = match.group(0)
    new_row = _row_for(count, date, existing)
    if new_row == existing:
        return False
    new_text = text[: match.start()] + new_row + text[match.end() :]
    evidence.write_text(new_text, encoding="utf-8", newline="")
    return True


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

    if newest_ts:
        date = _format_date(newest_ts)
    else:
        # Empty log: no record ts to prefer; a measured clause is still required.
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    cards = find_cards(repo_root)
    if not cards:
        print("REJECTED: no published cards found", file=sys.stderr)
        raise SystemExit(1)

    changed = 0
    for card in cards:
        evidence = card / "EVIDENCE.md"
        if not evidence.is_file():
            continue
        summed = {k: counts[k] for k in telemetry_keys(card) if counts.get(k)}
        count = sum(summed.values())
        if rewrite_dispatch_row(evidence, count, date):
            changed += 1
            print(f"  {card.relative_to(repo_root)}: {count} dispatch(es) "
                  f"from {summed or 'no key'}")

    print(f"PASS: refreshed dispatch rows in {changed}/{len(cards)} card(s)")


if __name__ == "__main__":
    main()
