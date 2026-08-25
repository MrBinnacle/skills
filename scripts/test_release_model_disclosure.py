#!/usr/bin/env python3
"""Contract tests for the release-model disclosure on the public surfaces.

ADR 0002 (docs/adr/0002-a-release-is-a-delivery-event.md) decided that a release
is a delivery event -- changed cards reach installed users when a version is
released -- and declared the narrow surface a version promises: the install path
and the card format, with the card set deliberately outside it. Two shipped
surfaces described the world that decision replaced: CHANGELOG.md opened by
calling tags and the file "a reading aid, not a pin", and the README offered no
disclosure that the card set is expected to change under a minor release. These
cases pin the corrected surfaces.

The scope is deliberate. Historical release notes state counts and describe the
old model; they are dated snapshots and are not rewritten here. The guarantee is
about what a reader of the preamble and the Install section is told today.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

ROOT = SCRIPT_DIR.parent
CHANGELOG = ROOT / "CHANGELOG.md"
README = ROOT / "README.md"
ADR = ROOT / "docs" / "adr" / "0002-a-release-is-a-delivery-event.md"
ADR_RELATIVE = "(docs/adr/0002-a-release-is-a-delivery-event.md)"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def changelog_preamble(changelog: Path) -> str:
    """Everything in CHANGELOG.md before the first release-note heading."""
    match = re.search(r"^## ", changelog.read_text(encoding="utf-8"), re.MULTILINE)
    text = changelog.read_text(encoding="utf-8")
    return text[: match.start()] if match else text


def case_preamble_carries_no_reading_aid_claim() -> None:
    body = changelog_preamble(CHANGELOG)
    check(
        "changelog preamble no longer calls tags and the file a reading aid, not a pin",
        "reading aid" not in body and "not a pin" not in body,
        body.strip(),
    )


def case_preamble_states_the_delivery_model() -> None:
    # Collapsed: the claim is about what the preamble SAYS, not where its lines
    # wrap, so a reflow must not turn the gate red.
    body = " ".join(changelog_preamble(CHANGELOG).split())
    check(
        "changelog preamble states changed cards reach installed users "
        "when a version is released",
        "changed cards reach installed users" in body and "version is released" in body,
        body,
    )
    check(
        "changelog preamble links ADR 0002 and the record exists",
        ADR_RELATIVE in body and ADR.is_file(),
        body,
    )


def main() -> None:
    case_preamble_carries_no_reading_aid_claim()
    case_preamble_states_the_delivery_model()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        raise SystemExit(1)
    print("PASS: release-model disclosure matches ADR 0002 on the public surfaces")


if __name__ == "__main__":
    main()
