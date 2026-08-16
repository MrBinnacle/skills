#!/usr/bin/env python3
"""Contract tests for the README admission lead and evidence census."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
ADMISSION = ROOT / "ADMISSION.md"
DISPOSITION = ROOT / "dispositions" / "2026-08-15-S295-admission-triage.md"

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


def evidence_rows(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| \*\*(.+?)\*\* \| (.*) \|$", line)
        if match:
            rows[match.group(1)] = match.group(2)
    return rows


def posture(rows: dict[str, str]) -> str:
    controlled = " ".join((rows["Screen result"], rows["Paired verdict"]))
    if re.search(r"\b(?!UNMEASURED\b)[A-Z][A-Z_]+\.", controlled):
        return "measured"
    if rows["Origin"].upper().startswith("OBSERVED"):
        return "origin-trace"
    return "unmeasured"


def readme_table(body: str) -> dict[str, tuple[str, int]]:
    result: dict[str, tuple[str, int]] = {}
    for card, stated_posture, occasions in re.findall(
        r"^\| \[`([^`]+)`\]\([^\n]+/EVIDENCE\.md\) \| "
        r"(measured|origin-trace|unmeasured) \| (\d+) \|$",
        body,
        re.MULTILINE,
    ):
        result[card] = (stated_posture, int(occasions))
    return result


def case_admission_method_leads() -> None:
    body = README.read_text(encoding="utf-8")
    positions = [
        body.find("## Admission method"),
        body.find("## Card map"),
        body.find("## Card evidence"),
    ]
    check(
        "admission method, card map, and card evidence are the first three H2 sections",
        positions[0] >= 0
        and positions == sorted(positions)
        and re.findall(r"^## .+$", body[: positions[2]], re.MULTILINE)
        == ["## Admission method", "## Card map"],
        str(positions),
    )


def case_three_instruments_are_referenced() -> None:
    body = section(README.read_text(encoding="utf-8"), "Admission method")
    check("admission lead links ADMISSION.md", "[admission policy](ADMISSION.md)" in body)
    check(
        "admission lead names the policy, gate card, and screen",
        all(term in body for term in ("admission policy", "gate card", "screen")),
        body.strip(),
    )
    policy = ADMISSION.read_text(encoding="utf-8")
    table = re.search(r"(?ms)^\| Prefer \| Means \| Lives \|.*?(?=\n\n)", policy)
    check(
        "the three-instrument table remains intact",
        table is not None
        and table.group(0).count("\n|") == 4
        and all(term in table.group(0) for term in ("admission policy", "gate card", "screen")),
    )


def case_card_map_names_four_types() -> None:
    body = section(README.read_text(encoding="utf-8"), "Card map")
    check(
        "card map names trap, procedure, gate, and schema",
        all(re.search(rf"\b{kind}\b", body, re.IGNORECASE) for kind in ("trap", "procedure", "gate", "schema")),
        body.strip(),
    )


def case_evidence_table_projects_the_card_rows() -> None:
    table = readme_table(section(README.read_text(encoding="utf-8"), "Card evidence"))
    expected: dict[str, tuple[str, int]] = {}
    for evidence in sorted((ROOT / "skills").glob("*/*/EVIDENCE.md")):
        rows = evidence_rows(evidence)
        count = re.match(r"(\d+)\b", rows["Occasions counted"])
        expected[evidence.parent.name] = (posture(rows), int(count.group(1)))
    check(
        "per-card table matches each EVIDENCE.md posture and occasion count",
        table == expected,
        f"expected {expected}; got {table}",
    )


def case_disposition_is_linked() -> None:
    body = README.read_text(encoding="utf-8")
    target = "dispositions/2026-08-15-S295-admission-triage.md"
    check("README links the S295 disposition record", f"]({target})" in body)
    check("the linked disposition record exists", DISPOSITION.is_file())


def case_public_copy_avoids_banned_vocabulary() -> None:
    body = README.read_text(encoding="utf-8")
    banned = re.findall(
        r"\b(?:earned|grandiose|grandiosity|perhaps|possibly|arguably)\b|readers may conclude",
        body,
        re.IGNORECASE,
    )
    check("README contains no banned vocabulary", not banned, str(sorted(set(banned))))


def main() -> None:
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
