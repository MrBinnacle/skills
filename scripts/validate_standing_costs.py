#!/usr/bin/env python3
"""Verify each card's Standing cost row matches the skill-harness audit.

The ticket (MrBinnacle/skills#323) recorded a claim-integrity break: every
model-invocable card's EVIDENCE.md carried a hand-estimated description token
count, and every estimate disagreed with the calibrated figure from
`skill-harness skill audit`.  This script rechecks each card's figure.

Two paths:

  1. When `skill-harness` is installed, the script runs `skill-harness skill
     audit <SKILL.md>` and reads the calibrated standing cost from its output.

  2. When skill-harness is unavailable (typical in CI), the script reads the
     committed `standing-costs.json`, which carries the calibrated figure
     alongside a sha256 of the SKILL.md file.  If the hash has changed since
     the JSON was last written, the script reports staleness and fails.

In both cases the stated figure in EVIDENCE.md is compared against the
calibrated figure, and disagreement fails the check.  The claims ledger
states the measurement date of the range and must carry the snapshot's
`calibrated_on` date (MrBinnacle/skills#472).  The README no longer states the
skill-harness range: it cites `/context` (MrBinnacle/skills#361), and the
paragraph that states the per-skill session cost must name `/context`, a Claude
Code version and an ISO date, and link the measurement (MrBinnacle/skills#536).

Output is ASCII-only, matching the other validators.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from validate_scoreboard import iter_skill_dirs  # noqa: E402

STANDING_COST_ROW: str = "Standing cost"
PINNED_HARNESS_VERSION = "0.3.0"
# Pattern: "Description: N tokens, measured by ..."
# The N is the calibrated figure we verify.
CALIBRATED_RE = re.compile(r"Description:\s*(\d+)\s*tokens")
ZERO_STANDING_COST_RE = re.compile(r"\bZero\s+(?:always-on|standing context cost)\b")
DISABLE_MODEL_INVOCATION_RE = re.compile(
    r"^disable-model-invocation:\s*true\s*$", re.MULTILINE
)
VERSION_RE = re.compile(r"version\s+(\d+\.\d+\.\d+)")
# The full audit line: "Standing cost (mechanical): raw N tokens · calibrated M tokens"
AUDIT_RE = re.compile(
    r"Standing cost \(mechanical\):.*?calibrated\s+(\d+)\s+tokens"
)
# Prose surfaces that state the measurement date of the skill-harness range.
# Each must carry the snapshot's calibrated_on date (MrBinnacle/skills#472).
DATED_PROSE_SURFACES = ("docs/product/claims-ledger.md",)
PROSE_DATE_RE = re.compile(
    r"measured by `skill-harness skill audit` on (\d{4}-\d{2}-\d{2})"
)


# The README paragraph that states the per-skill session cost cites `/context`
# (MrBinnacle/skills#361, #536).  It is found by its two stable words, not by
# the citation parts it must carry, so dropping a part cannot hide the paragraph.
README_COST_ANCHORS = ("every session", "tokens")
README_COST_PARTS = (
    ("`/context`", re.compile(r"`/context`")),
    ("a Claude Code version", re.compile(r"Claude Code \d+\.\d+\.\d+")),
    ("an ISO date", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    ("a link to the measurement", re.compile(r"\]\(https?://[^)\s]+\)")),
)


def readme_cost_citation_gaps(root: Path) -> list[str]:
    """The README's session-cost paragraph must carry its whole citation."""
    path = root / "README.md"
    if not path.is_file():
        return []
    paragraphs = re.split(r"\n\s*\n", path.read_text(encoding="utf-8"))
    cost = [p for p in paragraphs if all(a in p for a in README_COST_ANCHORS)]
    if not cost:
        return [
            "  - README.md: no paragraph states the per-skill session cost "
            "(expected one with 'every session' and 'tokens')"
        ]
    return [
        f"  - README.md: the session-cost paragraph does not name {label}"
        for label, rx in README_COST_PARTS
        if not rx.search(cost[0])
    ]


def standing_cost_row(evidence: Path) -> str | None:
    """Return the Standing cost row's value, skipping examples in fenced blocks."""
    fenced = False
    for line in evidence.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0].strip("* ")
        if name == STANDING_COST_ROW:
            return cells[1]
    return None


def extract_stated_tokens(evidence: Path, disabled: bool) -> int | None:
    """Return the stated standing cost, including the zero-cost procedure form."""
    row = standing_cost_row(evidence)
    if row is None:
        return None
    m = CALIBRATED_RE.search(row)
    if m:
        return int(m.group(1))
    if disabled and ZERO_STANDING_COST_RE.search(row):
        return 0
    return None


def installed_harness() -> tuple[list[str], str] | None:
    """Return an installed audit command and its version, preferring the module."""
    for command in ([sys.executable, "-m", "skill_harness"], ["skill-harness"]):
        try:
            result = subprocess.run(
                [*command, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
        m = VERSION_RE.search(result.stdout or "")
        if result.returncode == 0 and m:
            return command, m.group(1)
    return None


def audit_calibrated(command: list[str], skill_md: Path) -> int | None:
    """Run skill-harness skill audit and extract the calibrated figure."""
    try:
        result = subprocess.run(
            [*command, "skill", "audit", str(skill_md)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if result.returncode != 0:
        return None
    m = AUDIT_RE.search(result.stdout or "")
    if m:
        return int(m.group(1))
    return None


def load_standing_costs(root: Path) -> dict:
    """Load the committed standing-costs.json."""
    path = root / "scripts" / "standing-costs.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    """Hash the file with CRLF folded to LF.

    Git checks Markdown out with CRLF on Windows runners and LF elsewhere, so a
    hash over raw bytes describes one runner's checkout and not the other's.
    """
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def prose_date_disagreements(root: Path, calibrated_on: object) -> list[str]:
    """Each dated prose surface present in the tree must state calibrated_on."""
    blocking: list[str] = []
    for rel in DATED_PROSE_SURFACES:
        path = root / rel
        if not path.is_file():
            continue
        found = [
            (n, m.group(1))
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
            for m in PROSE_DATE_RE.finditer(line)
        ]
        if not found:
            blocking.append(
                f"  - {rel}: no dated standing-cost sentence "
                "(measured by `skill-harness skill audit` on YYYY-MM-DD)"
            )
        for n, stated in found:
            if stated != calibrated_on:
                blocking.append(
                    f"  - {rel}:{n}: prose says {stated}, "
                    f"standing-costs.json calibrated_on says {calibrated_on}"
                )
    return blocking


def validate(root: Path, *, use_snapshot: bool = False) -> None:
    cards = iter_skill_dirs(root)
    snapshot = load_standing_costs(root)
    harness = None if use_snapshot else installed_harness()

    blocking = prose_date_disagreements(root, snapshot.get("calibrated_on"))
    blocking += readme_cost_citation_gaps(root)

    if harness is None:
        snapshot_version = snapshot.get("skill_harness_version")
        if snapshot_version != PINNED_HARNESS_VERSION:
            blocking.append(
                "  - standing-costs.json: expected pinned skill-harness "
                f"{PINNED_HARNESS_VERSION}, found {snapshot_version!r}"
            )
        standing_costs = snapshot.get("cards", {})
    else:
        command, version = harness
        standing_costs = {}
        if version != PINNED_HARNESS_VERSION:
            blocking.append(
                "  - skill-harness: expected pinned version "
                f"{PINNED_HARNESS_VERSION}, found {version}"
            )

    for skill_dir in cards:
        card = skill_dir.name
        evidence = skill_dir / "EVIDENCE.md"
        skill_md = skill_dir / "SKILL.md"

        if not evidence.is_file():
            continue  # other gates catch missing files

        disabled = bool(
            DISABLE_MODEL_INVOCATION_RE.search(skill_md.read_text(encoding="utf-8"))
        )
        stated = extract_stated_tokens(evidence, disabled)
        if stated is None:
            expected = "zero standing cost" if disabled else "Description: N tokens"
            blocking.append(
                f"  - {card}: Standing cost row must state {expected}"
            )
            continue

        if harness is not None:
            calibrated = audit_calibrated(command, skill_md)
            if calibrated is None:
                blocking.append(
                    f"  - {card}: skill-harness audit failed to return a figure"
                )
                continue
            if stated != calibrated:
                blocking.append(
                    f"  - {card}: stated {stated} tokens, "
                    f"audit says {calibrated} tokens"
                )
        else:
            # Fallback: read standing-costs.json from the validated tree.
            entry = standing_costs.get(card)
            if entry is None:
                blocking.append(
                    f"  - {card}: not found in standing-costs.json"
                )
                continue
            # Check freshness: SHA256 of SKILL.md must match the committed hash
            current_sha = file_sha256(skill_md)
            expected_sha = entry.get("skill_md_sha256")
            if current_sha != expected_sha:
                blocking.append(
                    f"  - {card}: SKILL.md has changed since standing-costs.json "
                    f"was written (expected sha256={str(expected_sha)[:16]}, "
                    f"got {current_sha[:16]}). Regenerate with: "
                    f"python scripts/refresh_standing_costs.py"
                )
                continue
            calibrated = entry.get("standing_cost_tokens")
            if not isinstance(calibrated, int):
                blocking.append(
                    f"  - {card}: standing-costs.json has no calibrated token figure"
                )
                continue
            if stated != calibrated:
                blocking.append(
                    f"  - {card}: stated {stated} tokens, "
                    f"standing-costs.json says {calibrated} tokens"
                )

    if blocking:
        for line in blocking:
            print(line, file=sys.stderr)
        print(
            f"REJECTED: {len(blocking)} standing-cost disagreement(s) across "
            f"{len(cards)} published card(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    print(
        f"PASS: {len(cards)} published card(s), all standing cost figures "
        f"match the audit"
        + (
            " (via standing-costs.json; skill-harness not available)"
            if harness is None
            else ""
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to validate (default: this repository)",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="validate the committed fallback snapshot instead of running skill-harness",
    )
    args = parser.parse_args()
    validate(args.root.resolve(), use_snapshot=args.snapshot)


if __name__ == "__main__":
    main()
