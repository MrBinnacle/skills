#!/usr/bin/env python3
"""Suite for validate_card_files.py, including the committed poison fixtures.

Every rejection case runs the real entrypoint against a real tree rather than a
stubbed one. Going green is proven too, because a check that cannot go green is
as useless as one that cannot go red -- by the conforming baseline
(`case_stating_the_rows_clears_it`), which is the tree every mutation below is
a mutation OF, and by the two cases that re-run the same tree after correcting
it: the stale label and the count written as prose.
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
    "| **Dispatches recorded** | 5 dispatches, fixture counter, measured 2026-03-05. |\n"
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


def case_a_count_that_is_not_a_number_is_rejected(root: Path) -> None:
    """The row has to open with an integer, or nothing downstream can read it.

    Without this the row could say "one" or "several" and the arithmetic would
    have nothing to check, which is the row reverting to prose -- the state
    ADMISSION.md criterion 2 refuses. Reported once and not compounded: a row
    the checker cannot read is one defect, so it does not also collect a
    verdict on a label whose threshold is unknown.
    """
    evidence = CONFORMING_EVIDENCE.replace(
        "| 1 - 2026-03-04 the one incident.",
        "| one - 2026-03-04 the one incident.",
    )
    card = write_card(root, "prose-count-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "an Occasions counted row that does not open with an integer is rejected",
        result.returncode != 0 and "does not open with an integer" in result.stderr,
        result.stderr.strip(),
    )
    check(
        "the unreadable row is reported once, not compounded",
        "1 card contract breach(es)" in result.stderr,
        result.stderr.strip(),
    )

    (card / "EVIDENCE.md").write_text(CONFORMING_EVIDENCE, encoding="utf-8")
    cleared = run_checker(root)
    check(
        "writing the count as an integer clears it",
        cleared.returncode == 0,
        cleared.stdout + cleared.stderr,
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


def case_dispatch_row_does_not_corroborate_occasions(root: Path) -> None:
    """The dispatch row's dates are boilerplate, not records.

    Cross-review finding: the row plants its measurement date into every
    card, so leaving it in the corroboration haystack would auto-corroborate
    that date for any count a maintainer cares to write. The row is excised
    alongside the occasions row, so a cited date recorded ONLY there is
    uncorroborated.
    """
    evidence = CONFORMING_EVIDENCE.replace(
        "| 1 - 2026-03-04 the one incident. RECURRENCE-THIN.",
        "| 2 - 2026-03-04 the one incident; 2026-03-05 nothing records this.",
    )
    write_card(root, "dispatch-corroborated-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a cited date recorded only in the dispatch row is uncorroborated",
        result.returncode != 0 and "2026-03-05" in result.stderr
        and "no other" in result.stderr,
        result.stdout + result.stderr,
    )


def case_missing_dispatch_row_is_rejected(root: Path) -> None:
    """The dispatch row is contract: dropping it must not pass silently."""
    evidence = CONFORMING_EVIDENCE.replace(
        "| **Dispatches recorded** | 5 dispatches, fixture counter, "
        "measured 2026-03-05. |\n",
        "",
    )
    write_card(root, "dispatchless-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a card without the Dispatches recorded row is rejected",
        result.returncode != 0 and "no Dispatches recorded row" in result.stderr,
        result.stdout + result.stderr,
    )


def case_dispatch_row_opening_is_checked(root: Path) -> None:
    """The row opens with a nonzero count or the exact zero phrase.

    A zero written as a numeral is refused too: the counter is blind to hook
    and always-loaded firings, so its zero must read 'No recorded dispatch'
    and can never be read as 'unused'.
    """
    evidence = CONFORMING_EVIDENCE.replace(
        "| 5 dispatches, fixture counter, measured 2026-03-05.",
        "| some dispatches happened, measured 2026-03-05.",
    )
    card = write_card(root, "prose-dispatch-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a dispatch row opening with prose is rejected",
        result.returncode != 0
        and "integer count or the exact phrase" in result.stderr,
        result.stdout + result.stderr,
    )
    (card / "EVIDENCE.md").write_text(
        CONFORMING_EVIDENCE.replace(
            "| 5 dispatches, fixture counter, measured 2026-03-05.",
            "| 0 dispatches, fixture counter, measured 2026-03-05.",
        ),
        encoding="utf-8",
    )
    numeral_zero = run_checker(root)
    check(
        "a zero written as a numeral is rejected",
        numeral_zero.returncode != 0
        and "integer count or the exact phrase" in numeral_zero.stderr,
        numeral_zero.stdout + numeral_zero.stderr,
    )


def case_dispatch_row_needs_its_measurement_date(root: Path) -> None:
    """A measured figure without its 'measured <date>' clause is refused.

    Anchored on the clause, not on any date in the row: the live rows carry
    the delta-log inception date in their boilerplate, so a bare date search
    stays satisfied after the actual measurement clause is dropped
    (cross-review reproduced exactly that evasion).
    """
    evidence = CONFORMING_EVIDENCE.replace(
        "| 5 dispatches, fixture counter, measured 2026-03-05.",
        "| 5 dispatches, fixture counter, date never recorded.",
    )
    write_card(root, "undated-dispatch-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a dispatch row without a measured clause is rejected",
        result.returncode != 0 and "no 'measured <date>' clause" in result.stderr,
        result.stdout + result.stderr,
    )
    boilerplate_only = CONFORMING_EVIDENCE.replace(
        "| 5 dispatches, fixture counter, measured 2026-03-05.",
        "| 5 dispatches, fixture counter predating the log (2026-03-01).",
    )
    (root / "skills" / "engineering" / "undated-dispatch-card" / "EVIDENCE.md").write_text(
        boilerplate_only, encoding="utf-8"
    )
    evaded = run_checker(root)
    check(
        "a boilerplate date without the measured clause is still rejected",
        evaded.returncode != 0 and "no 'measured <date>' clause" in evaded.stderr,
        evaded.stdout + evaded.stderr,
    )
    zero = CONFORMING_EVIDENCE.replace(
        "| 5 dispatches, fixture counter, measured 2026-03-05.",
        "| No recorded dispatch, fixture counter, measured 2026-03-05.",
    )
    (root / "skills" / "engineering" / "undated-dispatch-card" / "EVIDENCE.md").write_text(
        zero, encoding="utf-8"
    )
    cleared = run_checker(root)
    check(
        "the No recorded dispatch form with a date passes",
        cleared.returncode == 0,
        cleared.stdout + cleared.stderr,
    )


def case_uncited_occurrence_record_is_rejected(root: Path) -> None:
    """The reverse direction: the card is checked against the row.

    Three dated occurrence records, a row citing two. Every forward check
    passes -- the row's integer matches its own citations and both are
    corroborated -- which is exactly the undercount #105 names. The reverse
    direction must refuse it, naming the uncited date.
    """
    evidence = CONFORMING_EVIDENCE.replace(
        "| 1 - 2026-03-04 the one incident. RECURRENCE-THIN.",
        "| 2 - 2026-03-04 the one incident; 2026-04-05 the second occurrence.",
    )
    gotchas = (
        "# gotchas\n\n"
        "[OBSERVED 2026-03-04] the one incident, first occurrence.\n"
        "[OBSERVED 2026-04-05] the second occurrence.\n"
        "[OBSERVED 2026-06-07] a third occurrence the row never counted.\n"
    )
    write_card(root, "undercount-card", evidence, gotchas)
    result = run_checker(root)
    check(
        "a dated occurrence record the row does not cite is rejected",
        result.returncode != 0 and "2026-06-07" in result.stderr,
        result.stderr.strip(),
    )
    check(
        "the cited occurrence dates are not reported",
        "2026-03-04" not in result.stderr and "2026-04-05" not in result.stderr,
        result.stderr.strip(),
    )


def case_plural_occurrence_record_is_rejected(root: Path) -> None:
    """A record worded in the plural must not evade the reverse direction.

    Cross-review reproduced the evasion: 'two further occurrences' with a
    singular-only pattern passed green. The plural is the natural phrasing
    when several occurrences land in one line, so it is in the rule.
    """
    gotchas = CONFORMING_GOTCHAS + (
        "[OBSERVED 2026-06-07] two further occurrences the row never counted.\n"
    )
    write_card(root, "plural-undercount-card", CONFORMING_EVIDENCE, gotchas)
    result = run_checker(root)
    check(
        "a plural-worded occurrence record the row does not cite is rejected",
        result.returncode != 0 and "2026-06-07" in result.stderr,
        result.stdout + result.stderr,
    )


def case_hyphenated_compound_is_not_an_occurrence_record(root: Path) -> None:
    """'co-occurrences' is correlational texture, not an occurrence record.

    A live card uses the term in a row that explicitly disclaims being
    occurrence evidence; matching inside the compound would red-flag it.
    """
    gotchas = CONFORMING_GOTCHAS + (
        "Strongest observed co-occurrences: 2026-07-12 three artifacts "
        "written within minutes of the invocation.\n"
    )
    write_card(root, "compound-texture-card", CONFORMING_EVIDENCE, gotchas)
    result = run_checker(root)
    check(
        "a hyphenated co-occurrences line is not demanded as a count",
        result.returncode == 0,
        result.stdout + result.stderr,
    )


def case_unmarked_prose_dates_are_not_demanded(root: Path) -> None:
    """The false-positive decision, pinned by its own fixture.

    A card records dates that are not occurrences -- a verification date, a
    methodology pin, a citation. Demanding those be counted would turn every
    published card red (measured 2026-08-24: the full-haystack scan flags all
    nine, on screen dates, methodology pins and validation-genre entries). The
    scope rule is HOW an occurrence is recorded, not a list of dates to
    ignore: only a line carrying both a date and the word 'occurrence' is an
    occurrence record.
    """
    gotchas = CONFORMING_GOTCHAS + (
        "Verified 2026-07-07 against the upstream docs.\n"
        "[OBSERVED 2026-08-08] a validation exercise, not the failure firing.\n"
        "Methodology pinned 2026-05-05 in the sibling instrument.\n"
    )
    write_card(root, "prose-dates-card", CONFORMING_EVIDENCE, gotchas)
    result = run_checker(root)
    check(
        "dated prose that is not an occurrence record is not demanded as a count",
        result.returncode == 0,
        result.stdout + result.stderr,
    )


def case_sibling_row_corroboration_still_passes(root: Path) -> None:
    """The regression protecting two live cards, built before the new check.

    A row may cite a date recorded only in a SIBLING ROW of the card's own
    evidence record -- corroborating_text() documents the two published cards
    resting on exactly that. The reverse direction must not narrow it.
    """
    evidence = CONFORMING_EVIDENCE.replace(
        "| 1 - 2026-03-04 the one incident. RECURRENCE-THIN.",
        "| 2 - 2026-03-04 the one incident; 2026-04-05 the field occurrence.",
    ) + "| **Observed in use** | 2026-04-05 field observation of the occurrence. |\n"
    write_card(root, "sibling-row-card", evidence, CONFORMING_GOTCHAS)
    result = run_checker(root)
    check(
        "a date recorded only in a sibling evidence row still passes",
        result.returncode == 0,
        result.stdout + result.stderr,
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
    # The reported count is checked against the tree, never against a number
    # written here. An earlier edition pinned the literal "9 published
    # card(s)", which turned this suite red on every admission and every
    # retirement until someone edited a digit in a test that holds no opinion
    # about how many cards there should be. Owner ruling 2026-08-24 retired
    # that class of pin, on the same reasoning that retired the banner's
    # counts on 2026-08-23. What is worth asserting is that the checker
    # counted the cards it actually walked.
    expected = len(validate_card_files.find_cards(REPO_ROOT))
    check(
        "the live run reports every card it walked",
        f"PASS: {expected} published card(s)" in result.stdout,
        result.stdout.strip(),
    )


def case_live_thin_labels_match_the_counts() -> None:
    """Three cards carry counted recurrence and no thin label; six carry it.

    The live run above already refuses a mismatch. This states the split, so a
    card quietly relabelled without a new dated occasion cannot pass as the
    record's own arithmetic.

    The 2026-08-15 S295 triage flagged seven, which is not the same as seven
    RECURRENCE-THIN verdicts: it gave six of them that verdict and gave
    git-pull-rebase-trap CEILING-LIKELY on the measurement axis, and that
    card's own row says why one counted occasion still earns the label.

    The split moved from 7/2 to 6/3 on 2026-08-23, when im-down recorded a
    second independent occurrence and dropped the label per the AGENTS.md rule
    that the label tracks the count in both directions. The number here is not
    a target and carries no preference for a smaller or larger set: it is a
    reading of the dated records, and it moves whenever one of them does. Both
    directions are ordinary. A card that earns its way out of the thin tier and
    a card that is added to the collection are the same mechanism working.
    """
    cards = validate_card_files.find_cards(REPO_ROOT)
    labelled = {
        card.name
        for card in cards
        if "RECURRENCE-THIN"
        in (card / "EVIDENCE.md").read_text(encoding="utf-8", errors="replace")
    }
    # The split is asserted as an INVARIANT over the tree, not as a roster.
    # The docstring above already says the number is a reading of the dated
    # records and moves whenever one of them does -- and the earlier edition
    # then pinned it anyway, at 6 and at a three-name set, so the suite went
    # red on exactly the events it calls ordinary. What actually has to hold
    # is AGENTS.md's rule in both directions: under two counted occasions the
    # card carries the label, at two or more it does not. That is checked
    # here against each card's own row, and it needs no maintenance when a
    # card enters, leaves, or earns its way out of the thin tier.
    counts = {}
    for card in cards:
        row = validate_card_files.scoreboard.evidence_fields(
            card / "EVIDENCE.md", (validate_card_files.OCCASIONS_ROW,)
        ).get(validate_card_files.OCCASIONS_ROW, "")
        opening = validate_card_files.COUNT_RE.match(row)
        counts[card.name] = int(opening.group(1)) if opening else None
    threshold = validate_card_files.INDEPENDENT_OCCASIONS
    mislabelled = sorted(
        n for n in labelled if counts[n] is None or counts[n] >= threshold
    )
    unlabelled = {c.name for c in cards} - labelled
    missing_label = sorted(
        n for n in unlabelled if counts[n] is None or counts[n] < threshold
    )
    check(
        "every RECURRENCE-THIN card counts fewer occasions than the threshold",
        not mislabelled,
        f"stale label on: {mislabelled}",
    )
    check(
        "every card at or above the threshold carries no thin label",
        not missing_label,
        f"label owed by: {missing_label}",
    )
    check(
        "the split is non-trivial in both directions",
        bool(labelled) and bool(unlabelled),
        f"labelled={len(labelled)} unlabelled={len(unlabelled)}",
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
        case_a_count_that_is_not_a_number_is_rejected,
        case_dates_must_be_corroborated_by_the_record,
        case_missing_dispatch_row_is_rejected,
        case_dispatch_row_opening_is_checked,
        case_dispatch_row_needs_its_measurement_date,
        case_dispatch_row_does_not_corroborate_occasions,
        case_uncited_occurrence_record_is_rejected,
        case_plural_occurrence_record_is_rejected,
        case_hyphenated_compound_is_not_an_occurrence_record,
        case_unmarked_prose_dates_are_not_demanded,
        case_sibling_row_corroboration_still_passes,
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
