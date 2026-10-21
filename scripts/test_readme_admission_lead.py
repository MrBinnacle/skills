#!/usr/bin/env python3
"""Contract tests for the README admission lead and evidence census.

THE CENSUS IS DERIVED THROUGH THE EXISTING VALIDATORS, NOT RESTATED HERE.
    Postures come from `validate_scoreboard.evidence_fields` and its closed
    verdict vocabulary; the occasions integer comes from
    `validate_card_files`'s own row regex; the cards come from
    `validate_scoreboard.iter_skill_dirs`. A second parser in this file would be
    a second copy of the two rules that function documents -- skip fenced
    blocks, first occurrence wins -- and the two copies would disagree on
    exactly the records that document their own row format.

    That is not hypothetical. The restated version this replaced read an
    `UNMEASURED` field that merely mentions `SKILL.md` as a measured result, and
    a real `KEEP` verdict written without a trailing period as no result at all.
    It also read fenced example rows as the card's values, and it walked
    `in-progress/`, so parking unshipped work -- which AGENTS.md sanctions --
    demanded a front-page row for a card that was never admitted.
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import check_load_mode_markers as markers  # noqa: E402
import validate_card_files as card_files  # noqa: E402
import validate_scoreboard as scoreboard  # noqa: E402

ROOT = SCRIPT_DIR.parent
README = ROOT / "README.md"
CATALOG = ROOT / "CATALOG.md"
ADMISSION = ROOT / "ADMISSION.md"
DISPOSITION = ROOT / "dispositions" / "2026-08-15-S295-admission-triage.md"

# The origin tier the README's `origin-trace` posture is keyed to. Checked
# against the scoreboard's closed vocabulary below, so renaming a tier fails
# here instead of silently re-bucketing every card.
ORIGIN_TRACE_TIER = "OBSERVED"
ORIGIN_ROW = "Origin"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def section(body: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", body
    )
    return match.group(1) if match else ""


def posture(rows: dict[str, str]) -> str:
    """One card's evidence posture, on the scoreboard's closed vocabulary.

    A verdict outside that vocabulary is reported as itself rather than bucketed:
    reading an unknown opening as a result would put a measurement on the front
    page that may never have happened, which is the direction that flatters the
    page.
    """
    for field in scoreboard.CONTROLLED_FIELDS:
        opening = rows.get(field, "").lstrip("* `_").upper()
        if opening.startswith(scoreboard.MEASURED_VERDICTS):
            return "measured"
        if not opening.startswith(scoreboard.UNMEASURED_VERDICTS):
            return f"unrecognised {field}: {rows.get(field, '')[:40]!r}"
    if rows.get(ORIGIN_ROW, "").upper().startswith(ORIGIN_TRACE_TIER):
        return "origin-trace"
    return "unmeasured"


def occasions(rows: dict[str, str]) -> int:
    """The integer that opens the card's occasions row, or -1 if it states none.

    -1 matches no README cell, so a row that does not open with a number fails
    the comparison instead of being silently skipped.
    """
    counted = card_files.COUNT_RE.match(rows.get(card_files.OCCASIONS_ROW, ""))
    return int(counted.group(1)) if counted else -1


def readme_table(body: str) -> dict[str, tuple[str, int]]:
    result: dict[str, tuple[str, int]] = {}
    for card, stated_posture, count in re.findall(
        r"^\| \[`([^`]+)`\]\([^\n]+/EVIDENCE\.md\) \| "
        r"(measured|origin-trace|unmeasured) \| (\d+) \|$",
        body,
        re.MULTILINE,
    ):
        result[card] = (stated_posture, int(count))
    return result


def case_admission_method_leads() -> None:
    """The three sections exist, and the policy is linked before the fold.

    RETIRED 2026-09-07 (S425 direction brief, section 7 decision 4): the H2-ORDER
    assertion. It required "## Admission method", "## Card map" and "## Card
    evidence" to be the first three H2 sections, in that order, with no other H2
    before them.

    Why it went. The order lock forced a Reference document to open on the
    collection's internal process, before a stranger had been told what a card
    is or what one costs. Two cross-family reviewers reached that finding
    independently against the shipped page (docs/audit/t1-readme-greenfield-S425/
    RESULTS.md, convergence row C1). A lock that pins section ORDER cannot be
    satisfied and also answer "what is this thing" first, so one of the two had
    to go, and the reader's question outranks the page's table of contents.

    What the lock was FOR survives here, because the reason it existed was never
    the ordering: it was that the admission material must not be buried. The
    replacement asserts the same protection without dictating sequence. All three
    sections must still exist, and the policy link must appear within the first 40
    lines, so it reaches the reader before the fold no matter where the section
    itself sits.

    What did NOT change: every other case in this file. The evidence table still
    has to match every card's EVIDENCE.md, the admission section still has to link
    ADMISSION.md and name both live instruments, the card map still has to name
    all three forms, and the disposition record still has to be linked. Retiring
    an order assertion is not a licence to loosen a fact assertion.
    """
    catalog_body = CATALOG.read_text(encoding="utf-8")
    headings = re.findall(r"^## .+$", catalog_body, re.MULTILINE)
    required = ["## Admission method", "## Card map", "## Card evidence"]
    missing = [heading for heading in required if heading not in headings]
    check(
        "admission method, card map, and card evidence sections all exist",
        not missing,
        f"missing {missing}",
    )
    readme_body = README.read_text(encoding="utf-8")
    lead = "\n".join(readme_body.splitlines()[:40])
    check(
        "the admission policy is linked within the first 40 lines",
        "(ADMISSION.md)" in lead,
        lead,
    )


def case_three_instruments_are_referenced() -> None:
    body = section(CATALOG.read_text(encoding="utf-8"), "Admission method")
    check("admission lead links ADMISSION.md", "[admission policy](ADMISSION.md)" in body)
    check(
        "admission lead names the policy and the screen",
        all(term in body for term in ("admission policy", "screen")),
        body.strip(),
    )
    policy = ADMISSION.read_text(encoding="utf-8")
    table = re.search(r"(?ms)^\| Prefer \| Means \| Lives \|.*?(?=\n\n)", policy)
    # Two instruments, not three. The gate card was the third; it retired on
    # 2026-08-31 (#178) and its row left the table with it. The count is
    # asserted rather than left open so a row cannot be dropped unnoticed.
    check(
        "the naming table remains intact",
        table is not None
        and table.group(0).count("\n|") == 3
        and all(term in table.group(0) for term in ("admission policy", "screen"))
        and "gate card" not in table.group(0),
    )


def case_card_map_names_four_types() -> None:
    body = section(CATALOG.read_text(encoding="utf-8"), "Card map")
    check(
        # Three forms, not four. "Gate" was the fourth, and skill-necessity-gate
        # was the only card of that type; both retired on 2026-08-31 (#178).
        "card map names trap, procedure, and schema",
        all(re.search(rf"\b{kind}\b", body, re.IGNORECASE) for kind in ("trap", "procedure", "schema")),
        body.strip(),
    )


def case_evidence_table_projects_the_card_rows() -> None:
    table = readme_table(section(CATALOG.read_text(encoding="utf-8"), "Card evidence"))
    check(
        "the origin-trace posture is keyed to a tier the scoreboard recognises",
        ORIGIN_TRACE_TIER in scoreboard.ORIGIN_TIERS,
        f"{ORIGIN_TRACE_TIER} not in {scoreboard.ORIGIN_TIERS}",
    )
    wanted = scoreboard.CONTROLLED_FIELDS + (ORIGIN_ROW, card_files.OCCASIONS_ROW)
    expected: dict[str, tuple[str, int]] = {}
    # Published cards only, by the same walk the scoreboard's `N admitted` uses:
    # a row for an unshipped `in-progress/` card would claim an admission that
    # never happened.
    for card in scoreboard.iter_skill_dirs(ROOT):
        evidence = card / "EVIDENCE.md"
        if not evidence.is_file():
            expected[card.name] = ("no EVIDENCE.md", -1)
            continue
        rows = scoreboard.evidence_fields(evidence, wanted)
        expected[card.name] = (posture(rows), occasions(rows))
    check(
        "per-card table matches each EVIDENCE.md posture and occasion count",
        table == expected,
        f"expected {expected}; got {table}",
    )


def case_disposition_is_linked() -> None:
    body = CATALOG.read_text(encoding="utf-8")
    target = "dispositions/2026-08-15-S295-admission-triage.md"
    check("CATALOG links the S295 disposition record", f"]({target})" in body)
    check("the linked disposition record exists", DISPOSITION.is_file())


def case_public_copy_avoids_banned_vocabulary() -> None:
    for label, path in (("README", README), ("CATALOG", CATALOG)):
        body = path.read_text(encoding="utf-8")
        banned = re.findall(
            r"\b(?:earned|grandiose|grandiosity|perhaps|possibly|arguably)\b|readers may conclude",
            body,
            re.IGNORECASE,
        )
        check(f"{label} contains no banned vocabulary", not banned, str(sorted(set(banned))))


def case_controlled_tests_paragraph_names_the_latest_read() -> None:
    """The README's controlled-tests paragraph keeps up with the paired record.

    On 2026-10-19 (#469) the paragraph still said "No second run is funded yet."
    while the card's Paired verdict row held two later reads, the latest dated
    2026-10-02. The verdict and the latest date are derived from that row, so a
    new read reopens this case without an edit here.
    """
    paragraph = next(
        (
            block
            for block in README.read_text(encoding="utf-8").split("\n\n")
            if block.startswith("Controlled tests,")
        ),
        "",
    )
    evidence = ROOT / "skills" / "engineering" / "pull-rebase" / "EVIDENCE.md"
    row = scoreboard.evidence_fields(evidence, ("Paired verdict",)).get("Paired verdict", "")
    verdict = re.match(r"[A-Z_]+", row.lstrip("* `_"))
    # Only the dates that open a read. The row also carries rotation and
    # currency-gate stamps ("checked 2026-09-30"), which are not reads.
    latest = max(
        re.findall(r"(?:ran on|readout,|dated|measured) (\d{4}-\d{2}-\d{2})", row),
        default="",
    )
    check(
        "the controlled-tests paragraph names the paired verdict",
        verdict is not None and f"`{verdict.group(0)}`" in paragraph,
        f"verdict {verdict.group(0) if verdict else None!r}; paragraph {paragraph!r}",
    )
    check(
        "the controlled-tests paragraph names the latest paired read",
        bool(latest) and latest in paragraph,
        f"latest read {latest!r}; paragraph {paragraph!r}",
    )
    denial = re.search(r"No (?:second|later|further) (?:run|read)[^.]*\.", paragraph)
    check(
        "the controlled-tests paragraph denies no read the record holds",
        denial is None,
        denial.group(0) if denial else "",
    )
    check(
        "the controlled-tests paragraph claims no measured benefit",
        "No skill claims a measured benefit yet." in paragraph,
        paragraph,
    )


README_LOADS_ROW = re.compile(
    r"^\| \[`([^`]+)`\]\(skills/([^/]+)/\1/gotchas\.md\) \| ([^|]+?) \| [^|]+ \| "
    r"(every session|by hand)\b",
    re.MULTILINE,
)


def loads_column_problems(root: Path) -> list[str]:
    """One line per card whose README Loads row disagrees with its frontmatter.

    The flag is read through `check_load_mode_markers.runs_by_hand`, the reader
    the bucket README check (#558) uses, so the two pages cannot be held to two
    readings of one fact (#553).
    """
    rows: dict[str, list[tuple[str, str, str]]] = {}
    for card, link_group, stated_group, loads in README_LOADS_ROW.findall(
        (root / "README.md").read_text(encoding="utf-8")
    ):
        rows.setdefault(card, []).append((link_group, stated_group.strip(), loads))
    problems: list[str] = []
    published = scoreboard.iter_skill_dirs(root)
    for skill_dir in published:
        card, group = skill_dir.name, skill_dir.parent.name
        want = "by hand" if markers.runs_by_hand(skill_dir / "SKILL.md") else "every session"
        stated = rows.get(card, [])
        if not stated:
            problems.append(f"{card}: README.md has no Loads row for it")
        elif len(stated) > 1:
            problems.append(f"{card}: README.md has {len(stated)} Loads rows for it, expected one")
        for link_group, stated_group, loads in stated:
            if loads != want:
                problems.append(f"{card}: README.md says it loads {loads}, its SKILL.md frontmatter says {want}")
            if (link_group, stated_group) != (group, group):
                problems.append(
                    f"{card}: README.md places it in {stated_group} (link under skills/{link_group}/), "
                    f"but it lives in skills/{group}/"
                )
    names = {skill_dir.name for skill_dir in published}
    problems.extend(
        f"{card}: README.md has a Loads row for it, but it is not a published card"
        for card in sorted(set(rows) - names)
    )
    return problems


def planted_loads_problems(edit_path: str, old: str, new: str) -> list[str]:
    """`loads_column_problems` on a copy of the live README and skills/ with one replacement."""
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        shutil.copytree(ROOT / "skills", tree / "skills")
        shutil.copy(README, tree / "README.md")
        target = tree / edit_path
        text = target.read_text(encoding="utf-8")
        assert old in text, f"control anchor absent in {edit_path}: {old!r}"
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return loads_column_problems(tree)


LOADS_CONTROLS = (
    (
        "a by-hand card's cell flipped to every session",
        "README.md", "| by hand (seen once) |\n| [`mocked-stub`]", "| every session |\n| [`mocked-stub`]",
        "stale-deploy: README.md says it loads every session, its SKILL.md frontmatter says by hand",
    ),
    (
        "an always-on card's cell flipped to by hand",
        "README.md", "| every session (seen at least twice) |\n| [`clirunner-env`]",
        "| by hand |\n| [`clirunner-env`]",
        "vacuous-check: README.md says it loads by hand, its SKILL.md frontmatter says every session",
    ),
    (
        "a by-hand card's flag removed with the README unchanged",
        "skills/engineering/clirunner-env/SKILL.md", "disable-model-invocation: true\n", "",
        "clirunner-env: README.md says it loads by hand, its SKILL.md frontmatter says every session",
    ),
    (
        "a flag added to an always-on card with the README unchanged",
        "skills/engineering/vacuous-check/SKILL.md", "---\n", "---\ndisable-model-invocation: true\n",
        "vacuous-check: README.md says it loads every session, its SKILL.md frontmatter says by hand",
    ),
    (
        "a card's row deleted",
        "README.md", "| [`im-up`](skills/engineering/im-up/gotchas.md)", "| im-up, unlinked",
        "im-up: README.md has no Loads row for it",
    ),
    (
        "a card's row repeated",
        "README.md", "| [`im-up`](skills/engineering/im-up/gotchas.md) | engineering | Checks",
        "| [`im-up`](skills/engineering/im-up/gotchas.md) | engineering | x | by hand |\n"
        "| [`im-up`](skills/engineering/im-up/gotchas.md) | engineering | Checks",
        "im-up: README.md has 2 Loads rows for it, expected one",
    ),
)


def case_loads_column_matches_each_card() -> None:
    """The README's Loads column agrees with each published card's frontmatter.

    The claims ledger (C16) forbids a roster of always-on cards that no check
    reads. The column is that roster, so every published card must have one
    row, in its own group, marked "by hand" exactly when its SKILL.md sets
    `disable-model-invocation: true`. Each control plants one drift in a temp
    copy of the live tree and requires the refusal to name the card.
    """
    problems = loads_column_problems(ROOT)
    check(
        "the README Loads column matches every published card's frontmatter",
        not problems,
        "\n  " + "\n  ".join(problems),
    )
    for name, edit_path, old, new, expect in LOADS_CONTROLS:
        planted = planted_loads_problems(edit_path, old, new)
        print("     " + "\n     ".join(planted))
        check(f"control: {name} fails, naming the card", expect in planted, f"got {planted}")


def main() -> None:
    case_loads_column_matches_each_card()
    case_controlled_tests_paragraph_names_the_latest_read()
    case_admission_method_leads()
    case_three_instruments_are_referenced()
    case_card_map_names_four_types()
    case_evidence_table_projects_the_card_rows()
    case_disposition_is_linked()
    case_public_copy_avoids_banned_vocabulary()
    print("")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        raise SystemExit(1)
    print("PASS: README admission lead matches the card ledger")


if __name__ == "__main__":
    main()
