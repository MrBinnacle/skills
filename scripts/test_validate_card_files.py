#!/usr/bin/env python3
"""Suite for validate_card_files.py, including the committed poison fixtures.

Every rejection case runs the real entrypoint against a real tree, and every
one of them is paired with the same tree corrected, because a check that cannot
go green either way is as useless as one that cannot go red.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "validate_card_files.py"
REPO_ROOT = SCRIPT_DIR.parent
POISON = SCRIPT_DIR / "fixtures" / "card-missing-gotchas"
ROWLESS = SCRIPT_DIR / "fixtures" / "card-missing-evidence-row"

sys.path.insert(0, str(SCRIPT_DIR))
import validate_card_files  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


# The rows a conforming card states. Written out here rather than imported from
# the checker: a fixture built from the checker's own constants would pass by
# construction and stop being evidence that the contract is the one AGENTS.md
# states.
CONFORMING_EVIDENCE = (
    "# EVIDENCE - fixture\n\n"
    "| Field | Value |\n|---|---|\n"
    "| **Occasions counted** | 1 - 2026-03-04 the one incident. RECURRENCE-THIN. |\n"
    "| **Re-screen trigger** | A platform fix that makes the failure impossible. |\n"
)
CONFORMING_GOTCHAS = "# gotchas\n\n[OBSERVED 2026-03-04] the one incident.\n"


def write_card(root: Path, name: str, evidence: str, gotchas: str) -> Path:
    card = root / "skills" / "engineering" / name
    card.mkdir(parents=True)
    (card / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    (card / "gotchas.md").write_text(gotchas, encoding="utf-8")
    (card / "EVIDENCE.md").write_text(evidence, encoding="utf-8")
    return card


def case_committed_poison_is_red() -> None:
    result = run_checker(POISON)
    check("committed poison fixture is rejected", result.returncode != 0)
    check(
        "missing-file report names the card and file",
        "skills/engineering/poison-card" in result.stderr
        and "gotchas.md" in result.stderr,
        result.stderr.strip(),
    )
    check(
        "the missing-file fixture is red for exactly one reason",
        "1 card contract breach(es)" in result.stderr,
        result.stderr.strip(),
    )


def case_committed_missing_row_fixture_is_red() -> None:
    """The row half of the contract, proven against a committed tree.

    This card ships all three files. If the checker only looked at file
    presence -- the shape this script had before the rows were contract -- this
    fixture would be green, which is why it is committed rather than built in a
    tempdir: it is the case that would silently stop being checked.
    """
    result = run_checker(ROWLESS)
    check("committed missing-row fixture is rejected", result.returncode != 0)
    check(
        "the report names the card and the row it does not state",
        "skills/engineering/rowless-card" in result.stderr
        and "Re-screen trigger" in result.stderr,
        result.stderr.strip(),
    )
    check(
        "the missing-row fixture is red for exactly one reason",
        "1 card contract breach(es)" in result.stderr,
        result.stderr.strip(),
    )


def case_stating_the_rows_clears_it(root: Path) -> None:
    write_card(root, "clean-card", CONFORMING_EVIDENCE, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a card stating both rows passes",
        result.returncode == 0,
        result.stdout + result.stderr,
    )
    check(
        "the pass line says the rows were checked, not just the files",
        "Occasions counted" in result.stdout and "Re-screen trigger" in result.stdout,
        result.stdout.strip(),
    )


def case_count_must_match_the_dated_references(root: Path) -> None:
    evidence = CONFORMING_EVIDENCE.replace(
        "| 1 - 2026-03-04 the one incident.",
        "| 3 - 2026-03-04 the one incident.",
    )
    write_card(root, "inflated-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a count above its dated references is rejected",
        result.returncode != 0 and "states 3 but cites 1 dated reference" in result.stderr,
        result.stderr.strip(),
    )


def case_dates_must_be_corroborated_by_the_record(root: Path) -> None:
    """A count is only as good as what it points at.

    The second date is stated in the row and recorded nowhere -- exactly how an
    honest-looking count gets inflated. The row alone must not be able to
    certify itself.
    """
    evidence = CONFORMING_EVIDENCE.replace(
        "| 1 - 2026-03-04 the one incident.",
        "| 2 - 2026-03-04 the one incident; 2026-09-09 an occasion nothing records.",
    ).replace(" RECURRENCE-THIN.", "")
    write_card(root, "invented-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a dated reference no other card file records is rejected",
        result.returncode != 0 and "2026-09-09" in result.stderr,
        result.stderr.strip(),
    )
    check(
        "the corroborated date is not reported",
        "2026-03-04" not in result.stderr,
        result.stderr.strip(),
    )


def case_thin_label_is_required_under_two_occasions(root: Path) -> None:
    evidence = CONFORMING_EVIDENCE.replace(" RECURRENCE-THIN.", "")
    write_card(root, "unlabelled-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "one counted occasion without the RECURRENCE-THIN label is rejected",
        result.returncode != 0 and "RECURRENCE-THIN" in result.stderr,
        result.stderr.strip(),
    )


def case_thin_label_is_refused_at_two_occasions(root: Path) -> None:
    """A stale honesty label is its own kind of dishonest."""
    evidence = CONFORMING_EVIDENCE.replace(
        "| 1 - 2026-03-04 the one incident.",
        "| 2 - 2026-03-04 the one incident; 2026-05-06 the second.",
    )
    gotchas = CONFORMING_GOTCHAS + "[OBSERVED 2026-05-06] the second.\n"
    write_card(root, "stale-label-card", evidence, gotchas)
    result = run_checker(root)
    check(
        "a card counting two occasions may not keep the thin label",
        result.returncode != 0 and "stale" in result.stderr,
        result.stderr.strip(),
    )

    (root / "skills" / "engineering" / "stale-label-card" / "EVIDENCE.md").write_text(
        evidence.replace(" RECURRENCE-THIN.", ""), encoding="utf-8"
    )
    cleared = run_checker(root)
    check(
        "dropping the stale label clears it",
        cleared.returncode == 0,
        cleared.stdout + cleared.stderr,
    )


def case_zero_cards_is_red(root: Path) -> None:
    (root / "skills").mkdir()
    result = run_checker(root)
    check(
        "a tree with zero cards is rejected",
        result.returncode != 0 and "no published cards" in result.stderr,
        f"rc={result.returncode} err={result.stderr.strip()}",
    )


def case_unpublished_buckets_owe_nothing(root: Path) -> None:
    """Only a published card owes the contract.

    AGENTS.md sanctions parking unshipped work in `in-progress/`, and
    validate_scoreboard.py already refuses to count it as admitted. A checker
    that demanded gotchas.md there would turn the linkcheck lane red for
    following the repo's own instruction, and would report a published-card
    count the front page contradicts.
    """
    write_card(root, "shipped-card", CONFORMING_EVIDENCE, CONFORMING_GOTCHAS)
    for unpublished in ("in-progress", ".scratch"):
        half_built = root / "skills" / unpublished / "half-built"
        half_built.mkdir(parents=True)
        (half_built / "SKILL.md").write_text("x\n", encoding="utf-8")

    result = run_checker(root)
    check(
        "a card in in-progress/ or a dot-bucket is not held to the contract",
        result.returncode == 0,
        f"rc={result.returncode} err={result.stderr.strip()}",
    )
    check(
        "unpublished cards are not counted as published",
        "PASS: 1 published card(s)" in result.stdout,
        result.stdout.strip(),
    )


def case_live_nine_cards_pass() -> None:
    result = run_checker(REPO_ROOT)
    check("the live tree passes", result.returncode == 0, result.stderr.strip())
    check(
        "the live run reports all nine cards",
        "PASS: 9 published card(s)" in result.stdout,
        result.stdout.strip(),
    )


def case_live_thin_labels_match_the_counts() -> None:
    """The two cards that stand carry no thin label, and the seven do.

    The live run above already refuses a mismatch. This states the split the
    S295 disposition record found, so a card quietly relabelled without a new
    dated occasion cannot pass as the record's own arithmetic.
    """
    cards = validate_card_files.find_cards(REPO_ROOT)
    labelled = {
        card.name
        for card in cards
        if "RECURRENCE-THIN"
        in (card / "EVIDENCE.md").read_text(encoding="utf-8", errors="replace")
    }
    check(
        "seven of the nine cards carry the RECURRENCE-THIN label",
        len(labelled) == 7,
        f"{len(labelled)}: {sorted(labelled)}",
    )
    check(
        "the two cards with counted recurrence carry no thin label",
        {c.name for c in cards} - labelled
        == {"parallel-review-disposition-schema", "subagent-research-reliability"},
        str({c.name for c in cards} - labelled),
    )


def case_linkcheck_lane_runs_checker() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "links.yml").read_text(
        encoding="utf-8"
    )
    linkcheck = re.search(r"(?ms)^  linkcheck:\n(.*?)(?=^  \S|\Z)", workflow)
    body = linkcheck.group(1) if linkcheck else ""
    check("links workflow has a linkcheck job", linkcheck is not None)
    check(
        "linkcheck runs the card-file suite",
        "python scripts/test_validate_card_files.py" in body,
        body,
    )
    check(
        "linkcheck runs the live card-file checker",
        "python scripts/validate_card_files.py" in body,
        body,
    )


def main() -> None:
    case_committed_poison_is_red()
    case_committed_missing_row_fixture_is_red()
    isolated = [
        case_stating_the_rows_clears_it,
        case_count_must_match_the_dated_references,
        case_dates_must_be_corroborated_by_the_record,
        case_thin_label_is_required_under_two_occasions,
        case_thin_label_is_refused_at_two_occasions,
        case_zero_cards_is_red,
        case_unpublished_buckets_owe_nothing,
    ]
    for func in isolated:
        with tempfile.TemporaryDirectory() as tmp:
            func(Path(tmp))
    case_live_nine_cards_pass()
    case_live_thin_labels_match_the_counts()
    case_linkcheck_lane_runs_checker()

    print("")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: card-file conformance suite, all cases correct")


if __name__ == "__main__":
    main()
