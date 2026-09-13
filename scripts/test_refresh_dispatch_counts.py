#!/usr/bin/env python3
"""Tests for refresh_dispatch_counts.py.

Exercises the three controls from issue #296:
  1. A fixture log with a known count produces the known row.
  2. An empty log produces a row that says zero, not the previous figure.
  3. A missing log leaves every card byte-identical and exits 0.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "refresh_dispatch_counts.py"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _make_fixture_log(
    tmp_path: Path,
    skill_counts: dict[str, int],
    ts: str = "2026-09-12T10:00:00Z",
    *,
    include_delta: bool = False,
    delta_counts: dict[str, int] | None = None,
) -> Path:
    """Write a fixture usage log and return its path."""
    log = tmp_path / "usage-log.jsonl"
    lines = []
    baseline = {"kind": "baseline", "ts": ts, "v": 1, "counts": {"skillUsage": skill_counts}}
    lines.append(json.dumps(baseline))
    if include_delta and delta_counts:
        delta = {"kind": "delta", "ts": ts, "v": 1, "deltas": {"skillUsage": delta_counts}}
        lines.append(json.dumps(delta))
    log.write_text("\n".join(lines) + "\n")
    return log


def _read_dispatch_row(evidence: Path) -> str:
    """Extract the dispatch row value from an EVIDENCE.md."""
    for line in evidence.read_text(encoding="utf-8").splitlines():
        if "Dispatches recorded" in line and line.startswith("|"):
            # Extract the value cell (between second and last |)
            cells = line.strip().strip("|").split("|")
            if len(cells) >= 2:
                return cells[1].strip()
    return ""


def _run_script(log_path: Path | None, tmp_path: Path) -> subprocess.CompletedProcess:
    """Run refresh_dispatch_counts.py against a temp repo copy."""
    env = os.environ.copy()
    if log_path is not None:
        env["SKILL_USAGE_LOG"] = str(log_path)
    else:
        env.pop("SKILL_USAGE_LOG", None)
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
    )


def _copy_published_tree(tmp_path: Path) -> None:
    """Copy the published skills tree into tmp_path for isolation."""
    skills_dir = REPO_ROOT / "skills"
    dest = tmp_path / "skills"
    dest.mkdir(parents=True)
    for bucket in skills_dir.iterdir():
        if not bucket.is_dir() or bucket.name.startswith("."):
            continue
        bucket_dest = dest / bucket.name
        bucket_dest.mkdir()
        for card in bucket.iterdir():
            if not card.is_dir():
                continue
            card_dest = bucket_dest / card.name
            card_dest.mkdir()
            for f in card.iterdir():
                if f.is_file():
                    (card_dest / f.name).write_bytes(f.read_bytes())
    # Copy scripts dir so validate_scoreboard is importable.
    scripts_dest = tmp_path / "scripts"
    scripts_dest.mkdir()
    for f in (REPO_ROOT / "scripts").iterdir():
        if f.is_file() and f.suffix == ".py":
            (scripts_dest / f.name).write_bytes(f.read_bytes())


@pytest.fixture()
def repo_copy(tmp_path: Path) -> Path:
    """A temporary copy of the published tree for test isolation."""
    _copy_published_tree(tmp_path)
    return tmp_path


class TestControl1FixtureLog:
    """Control 1: a fixture log with a known count produces the known row."""

    def test_nonzero_count(self, repo_copy: Path) -> None:
        log = _make_fixture_log(repo_copy, {"im-up": 42})
        result = _run_script(log, repo_copy)
        assert result.returncode == 0
        row = _read_dispatch_row(repo_copy / "skills/engineering/im-up/EVIDENCE.md")
        assert "42 dispatches" in row
        assert "measured 2026-09-12" in row

    def test_baseline_plus_delta(self, repo_copy: Path) -> None:
        log = _make_fixture_log(
            repo_copy, {"im-up": 10}, include_delta=True, delta_counts={"im-up": 5}
        )
        result = _run_script(log, repo_copy)
        assert result.returncode == 0
        row = _read_dispatch_row(repo_copy / "skills/engineering/im-up/EVIDENCE.md")
        assert "15 dispatches" in row

    def test_absent_skill_gets_zero(self, repo_copy: Path) -> None:
        """A card not in the log gets zero, not the previous figure."""
        # Read the original dispatch row.
        original = _read_dispatch_row(
            repo_copy / "skills/engineering/im-up/EVIDENCE.md"
        )
        # Run with a log that names a DIFFERENT skill.
        log = _make_fixture_log(repo_copy, {"vacuous-check": 7})
        result = _run_script(log, repo_copy)
        assert result.returncode == 0
        row = _read_dispatch_row(repo_copy / "skills/engineering/im-up/EVIDENCE.md")
        assert "No recorded dispatch" in row
        assert row != original  # Must have changed.

    def test_plugin_key_not_counted(self, repo_copy: Path) -> None:
        """A plugin:skill key does not add to the bare skill's count."""
        log = _make_fixture_log(repo_copy, {"plugin:im-up": 99})
        result = _run_script(log, repo_copy)
        assert result.returncode == 0
        row = _read_dispatch_row(repo_copy / "skills/engineering/im-up/EVIDENCE.md")
        assert "No recorded dispatch" in row

    def test_anomaly_records_skipped(self, repo_copy: Path) -> None:
        """Anomaly records do not contribute to the count."""
        records = [
            {"kind": "baseline", "ts": "2026-09-10T00:00:00Z", "v": 1,
             "counts": {"skillUsage": {"im-up": 10}}},
            {"kind": "anomaly", "ts": "2026-09-11T00:00:00Z", "v": 1},
            {"kind": "delta", "ts": "2026-09-12T00:00:00Z", "v": 1,
             "deltas": {"skillUsage": {"im-up": 3}}},
        ]
        log = repo_copy / "usage-log.jsonl"
        log.write_text("\n".join(json.dumps(r) for r in records) + "\n")
        result = _run_script(log, repo_copy)
        assert result.returncode == 0
        assert "skipped 1 anomaly" in result.stderr
        row = _read_dispatch_row(repo_copy / "skills/engineering/im-up/EVIDENCE.md")
        assert "13 dispatches" in row  # 10 + 3, not counting the anomaly.


class TestControl2EmptyLog:
    """Control 2: an empty log produces a row that says zero."""

    def test_empty_log_writes_zero(self, repo_copy: Path) -> None:
        """Every card's dispatch row says zero, not the previous figure."""
        # Read originals.
        originals = {}
        for card in (repo_copy / "skills").rglob("EVIDENCE.md"):
            originals[card] = _read_dispatch_row(card)

        log = repo_copy / "empty.jsonl"
        log.write_text("")
        result = _run_script(log, repo_copy)
        assert result.returncode == 0

        for card in (repo_copy / "skills").rglob("EVIDENCE.md"):
            row = _read_dispatch_row(card)
            assert "No recorded dispatch" in row, f"{card}: expected zero row"
            # Must differ from original if original was nonzero.
            orig = originals[card]
            if "dispatches" in orig and "No recorded" not in orig:
                assert row != orig, f"{card}: row was not rewritten from nonzero"


class TestControl3MissingLog:
    """Control 3: a missing log leaves every card byte-identical and exits 0."""

    def test_missing_log_no_change(self, repo_copy: Path) -> None:
        """With no log, no card is changed and the script prints SKIP."""
        # Snapshot all EVIDENCE.md files.
        snapshots = {}
        for card in (repo_copy / "skills").rglob("EVIDENCE.md"):
            snapshots[card] = card.read_bytes()

        result = _run_script(None, repo_copy)
        assert result.returncode == 0
        assert "SKIP" in result.stdout

        for card, original_bytes in snapshots.items():
            assert card.read_bytes() == original_bytes, f"{card} was modified"

    def test_skip_message_names_path(self, repo_copy: Path) -> None:
        """The SKIP message includes the path that was tried."""
        result = _run_script(None, repo_copy)
        assert "SKIP" in result.stdout
        assert "usage log not found" in result.stdout


class TestEdgeCases:
    """Additional edge cases for robustness."""

    def test_multiple_skills_in_log(self, repo_copy: Path) -> None:
        """Multiple skills in one log are all rewritten correctly."""
        log = _make_fixture_log(repo_copy, {"im-up": 10, "vacuous-check": 20})
        result = _run_script(log, repo_copy)
        assert result.returncode == 0
        assert "10 dispatches" in _read_dispatch_row(
            repo_copy / "skills/engineering/im-up/EVIDENCE.md"
        )
        assert "20 dispatches" in _read_dispatch_row(
            repo_copy / "skills/engineering/vacuous-check/EVIDENCE.md"
        )

    def test_date_from_newest_record(self, repo_copy: Path) -> None:
        """The date comes from the newest record's ts, not today."""
        log = repo_copy / "usage-log.jsonl"
        records = [
            {"kind": "baseline", "ts": "2026-06-01T00:00:00Z", "v": 1,
             "counts": {"skillUsage": {"im-up": 5}}},
            {"kind": "delta", "ts": "2026-08-15T12:00:00Z", "v": 1,
             "deltas": {"skillUsage": {"im-up": 3}}},
        ]
        log.write_text("\n".join(json.dumps(r) for r in records) + "\n")
        result = _run_script(log, repo_copy)
        assert result.returncode == 0
        row = _read_dispatch_row(repo_copy / "skills/engineering/im-up/EVIDENCE.md")
        # Date should be from the delta record, not the baseline.
        assert "measured 2026-08-15" in row

    def test_row_passes_validator_format(self, repo_copy: Path) -> None:
        """The rewritten row satisfies validate_card_files.py dispatch checks."""
        log = _make_fixture_log(repo_copy, {"im-up": 42})
        result = _run_script(log, repo_copy)
        assert result.returncode == 0

        # Now run the card file validator.
        val_result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "validate_card_files.py"),
             "--root", str(repo_copy)],
            capture_output=True, text=True,
        )
        # The validator should not reject the dispatch row format.
        # (It may fail for other reasons like missing files, but the
        # dispatch row should be clean.)
        assert "must open with a nonzero integer" not in val_result.stderr
        assert "states no 'measured <date>'" not in val_result.stderr
