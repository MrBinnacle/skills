#!/usr/bin/env python3
"""Run the standing obligations (`conformance v2`) against the published tree.

SECURITY.md declares seven standing obligations a published card owes for as long
as it stays published. This script is the driver behind that section. It reports
PASS / FAIL / CANNOT-CHECK per card per obligation, and CANNOT-CHECK is a
distinct reported state -- never folded into PASS. An obligation the collection
cannot verify from inside itself is a visible count, because a green line that
quietly includes the unverifiable claims more than it measured.

Output is ASCII-only so the Windows CI cell does not die on cp1252 when printing
a status line, matching validate_scoreboard.py and validate_skill_formats.py.
Run with PYTHONUTF8=1.

WHERE THE OBLIGATIONS COME FROM
    From OBLIGATIONS below -- a structured list, not a prose scrape. The
    throwaway prototype this script is promoted from read its obligations by
    substring-matching the published sentences out of SECURITY.md, and that
    coupled the checker to the file's hard wrapping: one sentence spanning a
    newline turned two conforming cards red. The prose and the list are instead
    held together by a test (test_validate_conformance.py) asserting that the
    identifiers and the count here match the SECURITY.md section exactly, so
    drift is a red suite rather than a silent miscount.

WHAT IS DELEGATED, AND WHY
    O1's format vocabulary is validate_skill_formats.py's predicate, imported
    and called rather than restated -- one vocabulary, one place to widen it.
    O4's controlled-field names are validate_scoreboard.py's CONTROLLED_FIELDS
    for the same reason. O6 is validate_scoreboard.py's whole run. O7 reads the
    manifest directly -- it is this repository's own artifact, so there is no
    other predicate to delegate to.

SCOPE: CARD VS REPO
    Four obligations are properties of one card and are scored per card.
    Three -- O1's walk, O6's scoreboard and O7's manifest -- are repo-wide
    predicates whose subject is the tree. They are evaluated ONCE and reported
    in their own block. Copying a single repo verdict into fifteen identical
    cells would multiply one finding by the card count and make the totals lie
    about how much was checked.

Usage:
    python scripts/validate_conformance.py
    python scripts/validate_conformance.py --root <tree> --markdown
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_scoreboard as scoreboard  # noqa: E402
import validate_skill_formats as formats  # noqa: E402

PASS: Final[str] = "PASS"
FAIL: Final[str] = "FAIL"
CANT: Final[str] = "CANNOT-CHECK"

CONFORMANCE_VERSION: Final[str] = "conformance v2"

# The SECURITY.md section states this date as the trial's pre-registered exit.
# It is asserted equal by the suite so the workflow header, the policy section
# and the checker cannot state three different dates.
TRIAL_EXIT_DATE: Final[str] = "2026-11-07"

CARD = "card"
REPO = "repo"


@dataclass(frozen=True)
class Obligation:
    oid: str
    title: str
    scope: str


# The list the checker is written against. Identifiers and count are asserted
# against the SECURITY.md "Standing obligations" section by the suite.
OBLIGATIONS: Final[tuple[Obligation, ...]] = (
    Obligation("O1", "declared formats only", REPO),
    Obligation("O2", "no fetch-and-execute", CARD),
    Obligation("O3", "shipped scripts named in SKILL.md", CARD),
    Obligation("O4", "EVIDENCE.md present with all controlled fields", CARD),
    Obligation("O5", "controlled fields do not contradict a published receipt", CARD),
    Obligation("O6", "scoreboard lockstep", REPO),
    Obligation("O7", "plugin manifest and published tree agree", REPO),
)

CARD_OBLIGATIONS: Final[tuple[Obligation, ...]] = tuple(
    o for o in OBLIGATIONS if o.scope == CARD
)
REPO_OBLIGATIONS: Final[tuple[Obligation, ...]] = tuple(
    o for o in OBLIGATIONS if o.scope == REPO
)


@dataclass(frozen=True)
class Result:
    verdict: str
    detail: str


@dataclass(frozen=True)
class Card:
    name: str
    folder: Path
    root: Path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def find_cards(root: Path) -> list[Card]:
    """Published cards: a SKILL.md two levels under skills/.

    Deliberately narrower than the format gate's repo-wide SKILL.md marker
    scan. The obligations are what a PUBLISHED card owes; the fixture trees
    under scripts/fixtures/ are inputs to other validators and owe nothing.
    """
    return [
        Card(p.parent.name, p.parent, root)
        for p in sorted((root / "skills").glob("*/*/SKILL.md"))
    ]


# ------------------------------------------------------------ card obligations


# Known download-and-run shapes. This catches command lines, not English: a card
# that tells the agent to fetch a page and follow what it says ships no pattern
# at all. PASS here means "no known shape present", and the report says so.
FETCH_EXEC: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"curl[^\n|]*\|\s*(ba)?sh", re.I),
    re.compile(r"wget[^\n|]*\|\s*(ba)?sh", re.I),
    re.compile(r"iwr[^\n|]*\|\s*iex", re.I),
    re.compile(r"invoke-webrequest[^\n|]*\|\s*(iex|invoke-expression)", re.I),
    re.compile(r"eval\s*\(\s*(requests|urllib|fetch)", re.I),
    re.compile(r"pip\s+install\s+(https?|git\+)", re.I),
)

READABLE_SUFFIXES: Final[tuple[str, ...]] = (".md", ".txt", ".py", ".json")


def check_fetch_execute(card: Card) -> Result:
    hits = []
    for path in sorted(card.folder.rglob("*")):
        if not path.is_file() or path.suffix not in READABLE_SUFFIXES:
            continue
        for pattern in FETCH_EXEC:
            for match in pattern.finditer(read(path)):
                hits.append(f"{path.name}: {match.group(0)[:60]}")
    if hits:
        return Result(FAIL, "; ".join(hits))
    return Result(PASS, "no known download-and-run shape in any shipped file")


TEST_PREFIX: Final[str] = "test_"


def check_scripts_named(card: Card) -> Result:
    """O3: a SKILL.md names every script it asks the agent to run.

    SECURITY.md commitment 3 carves out the shipped test suites, which CI runs
    and no skill invokes. The carve-out is read out of SECURITY.md's own
    sentence rather than hardcoded, so a tree that drops the sentence loses the
    exemption -- that is what makes this the obligation with a demonstrated
    rejection: at the PR #47 tree the naming sentence did not exist and the
    scripts did, and this check reports the contradiction.
    """
    scripts = sorted(
        p for p in card.folder.rglob("*.py") if "__pycache__" not in p.parts
    )
    if not scripts:
        return Result(PASS, "ships no script")
    security = " ".join(read(card.root / "SECURITY.md").split())
    if "names the scripts it asks the agent to run" not in security:
        return Result(
            FAIL,
            "the tree states no script-naming obligation yet this card ships "
            + ", ".join(p.name for p in scripts),
        )
    exempt = "also ship their test suites" in security and card.name in security
    skill_md = read(card.folder / "SKILL.md")
    unnamed = [p.name for p in scripts if p.name not in skill_md]
    if not unnamed:
        return Result(PASS, f"all {len(scripts)} script(s) named in SKILL.md")
    still = [n for n in unnamed if not (exempt and n.startswith(TEST_PREFIX))]
    if still:
        return Result(FAIL, "not named in SKILL.md: " + ", ".join(sorted(still)))
    return Result(
        PASS,
        f"{len(scripts) - len(unnamed)} named; test suite(s) covered by the "
        "SECURITY.md carve-out: " + ", ".join(sorted(unnamed)),
    )


def check_evidence_fields(card: Card) -> Result:
    """O4: EVIDENCE.md present, with every controlled field stated.

    The field names come from validate_scoreboard.CONTROLLED_FIELDS so the two
    validators cannot disagree about what a controlled field is. An empty row
    is the same refusal as an absent one: the card has not said.
    """
    evidence = card.folder / "EVIDENCE.md"
    if not evidence.exists():
        return Result(FAIL, "no EVIDENCE.md")
    values = scoreboard.evidence_fields(evidence, scoreboard.CONTROLLED_FIELDS)
    missing = [
        f for f in scoreboard.CONTROLLED_FIELDS if not values.get(f, "").strip("* `")
    ]
    if missing:
        return Result(FAIL, "no stated " + " and no stated ".join(missing))
    return Result(
        PASS,
        "EVIDENCE.md states " + ", ".join(scoreboard.CONTROLLED_FIELDS),
    )


def check_receipt_agreement(card: Card, harness_root: Path | None = None) -> Result:
    """O5: controlled fields must not contradict a published harness receipt.

    Without --harness-root, returns CANNOT-CHECK as before: the measurement
    sibling's evidence store is private and single-copy, so there is nothing
    here to compare a controlled field against.

    With --harness-root, reads the receipt file the card's controlled row links
    in its Receipt clause and fails on four conditions:
    1. the linked receipt file is absent under the harness root;
    2. the receipt's subject_identity.skill_id differs from sha256 of SKILL.md;
    3. the row's opening verdict word differs from the receipt's verdict;
    4. a receipt with the same skill_id and a later source.date exists that the
       row does not link.

    A field that declares its own receipt `not current:` is a history link, which
    is what the rotation pass (AGENTS.md step 5) instructs a card to keep.
    Conditions 1 to 3 do not apply to it: a missing file, an absent
    subject_identity or a superseded verdict is what the row already says, not a
    contradiction of it. It still counts as linked for condition 4. A receipt
    that fails those conditions in a field making no such declaration stays a
    FAIL, which is the case the check exists for.
    """
    if harness_root is None:
        return Result(
            CANT,
            "no citable published receipt to compare against from inside this "
            "repository; maintainer-clock obligation",
        )

    evidence = card.folder / "EVIDENCE.md"
    if not evidence.exists():
        return Result(CANT, "no EVIDENCE.md to read controlled fields from")

    fields = scoreboard.evidence_fields(evidence, scoreboard.CONTROLLED_FIELDS)
    skill_md = card.folder / "SKILL.md"
    if not skill_md.exists():
        return Result(CANT, "no SKILL.md to compute skill_id from")
    expected_skill_id = hashlib.sha256(skill_md.read_bytes()).hexdigest()

    linked_receipts: list[Path] = []
    linked_skill_ids: list[str] = []
    history_names: list[str] = []

    for field_name in scoreboard.CONTROLLED_FIELDS:
        value = fields.get(field_name, "")
        receipt_filename = _receipt_filename(value)
        if receipt_filename is None:
            continue

        if _declares_not_current(value):
            history_names.append(Path(receipt_filename).name)
            continue

        row_verdict = _opening_verdict(value)
        receipt_path = _find_receipt(harness_root, receipt_filename)
        if receipt_path is None:
            return Result(
                FAIL,
                f"receipt file {receipt_filename!r} not found under harness root",
            )

        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return Result(FAIL, f"receipt {receipt_filename!r} unreadable: {exc}")

        si = receipt.get("subject_identity")
        if not isinstance(si, dict):
            return Result(
                FAIL,
                f"receipt {receipt_filename!r} has no subject_identity block",
            )
        receipt_skill_id = si.get("skill_id")
        if receipt_skill_id != expected_skill_id:
            return Result(
                FAIL,
                f"receipt {receipt_filename!r} skill_id {receipt_skill_id!r} "
                f"differs from sha256(SKILL.md) = {expected_skill_id!r}",
            )

        receipt_verdict = str(receipt.get("verdict") or "").strip().upper()
        if receipt_verdict != row_verdict:
            return Result(
                FAIL,
                f"receipt {receipt_filename!r} verdict {receipt_verdict!r} "
                f"differs from row verdict {row_verdict!r}",
            )

        linked_receipts.append(receipt_path)
        linked_skill_ids.append(expected_skill_id)

    if not linked_receipts:
        if history_names:
            return Result(
                PASS,
                "the only receipt link is history: "
                + ", ".join(sorted(history_names))
                + ", which its own row declares not current",
            )
        return Result(
            CANT,
            "no Receipt clause in any controlled field; rotation pass "
            "owns this case",
        )

    # Condition 4: check for a newer receipt not linked by the row. A history
    # link counts as linked here, so a row that has already moved on to a newer
    # receipt is not reported as failing to link it.
    all_receipts = _find_all_receipts(harness_root)
    linked_names = {p.name for p in linked_receipts} | set(history_names)
    for receipt_path in all_receipts:
        if receipt_path.name in linked_names:
            continue
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        si = receipt.get("subject_identity")
        if not isinstance(si, dict):
            continue
        rid = si.get("skill_id")
        if rid not in linked_skill_ids:
            continue
        receipt_date = (receipt.get("source") or {}).get("date", "")
        # Compare against the date of the linked receipt with the same skill_id
        for linked in linked_receipts:
            lr = json.loads(linked.read_text(encoding="utf-8"))
            lr_date = (lr.get("source") or {}).get("date", "")
            if receipt_date > lr_date:
                return Result(
                    FAIL,
                    f"newer receipt {receipt_path.name!r} (dated "
                    f"{receipt_date}) exists but is not linked by the row "
                    f"(linked receipt dated {lr_date})",
                )

    return Result(PASS, "controlled fields agree with the linked receipt(s)")


def _opening_verdict(value: str) -> str:
    """The row's opening verdict word, same startswith rule as the scoreboard.

    The verdict is the first thing the field says. Prose after it — a dated
    screen note, a Receipt clause — is not part of the word. Capturing
    everything up to `Receipt:` would make every real card fail condition 3
    against a matching receipt.
    """
    opening = value.lstrip("* `_").upper()
    vocabulary = scoreboard.UNMEASURED_VERDICTS + scoreboard.MEASURED_VERDICTS
    for verdict in vocabulary:
        if opening.startswith(verdict):
            return verdict
    token = opening.split()[0] if opening.strip() else ""
    return token.rstrip(".,;:")


def _declares_not_current(value: str) -> bool:
    """Whether a controlled field types its own receipt link as history.

    The rotation pass keeps a superseded receipt link and states why, in the
    shape `not current: <reason>`. A card that follows that instruction must not
    then be scored as contradicting a receipt its own row has already retired.
    """
    return "not current:" in value.lower()


def _receipt_filename(value: str) -> str | None:
    """Filename from a Receipt clause, markdown-link or backtick/quote form.

    Spec shape: `Receipt: [<file>.json](<harness blob URL>), dated ...`.
    Live cards also use backticks around a path. Both must resolve.
    """
    match = RECEIPT_CLAUSE_RE.search(value)
    if not match:
        return None
    return match.group(1) or match.group(2)


def _find_receipt(harness_root: Path, filename: str) -> Path | None:
    """Find a receipt file by relative path or basename under the harness root."""
    direct = harness_root / filename
    if direct.is_file():
        return direct
    name = Path(filename).name
    matches = [p for p in harness_root.rglob(name) if p.is_file()]
    return matches[0] if matches else None


def _find_all_receipts(harness_root: Path) -> list[Path]:
    """Find all JSON files that look like SERS receipts under the harness root."""
    results = []
    for p in harness_root.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and "sers_version" in data:
            results.append(p)
    return results


# Spec form: Receipt: [file.json](url). Also `file.json` / "file.json" as used
# on live cards today. Group 1 = markdown link text; group 2 = quoted form.
RECEIPT_CLAUSE_RE: Final[re.Pattern[str]] = re.compile(
    r"Receipt:\s*(?:"
    r"\[([^\]]+?\.json)\]\([^)]*\)"
    r"|"
    r"[`\"']([^`\"']+?\.json)[`\"']"
    r")"
)


CARD_CHECKS = {
    "O2": check_fetch_execute,
    "O3": check_scripts_named,
    "O4": check_evidence_fields,
    "O5": check_receipt_agreement,
}


# ------------------------------------------------------------ repo obligations


def check_declared_formats(root: Path) -> Result:
    """O1, delegated to the format gate's own predicate rather than restated."""
    gate_script = root / "scripts" / "validate_skill_formats.py"
    if not gate_script.exists():
        return Result(CANT, "scripts/validate_skill_formats.py absent from this tree")
    folders = formats.find_skill_folders(root)
    if not folders:
        return Result(CANT, "no skill folders found under this root")
    files = formats.guarded_files(folders)
    skipped = formats.ignored_files(root, files)
    bad = []
    for path in files:
        if path in skipped:
            continue
        reason = formats.violation(root, path)
        if reason is not None:
            bad.append(reason)
    if bad:
        return Result(FAIL, f"{len(bad)} file(s): " + "; ".join(bad[:5]))
    return Result(
        PASS,
        f"{len(files) - len(skipped)} guarded file(s) across {len(folders)} "
        "skill folder(s), all declared formats",
    )


def check_scoreboard_lockstep(root: Path) -> Result:
    """O6, delegated: the scoreboard validator's whole run over this tree."""
    script = root / "scripts" / "validate_scoreboard.py"
    if not script.exists():
        return Result(CANT, "scripts/validate_scoreboard.py absent from this tree")
    proc = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    lines = (proc.stdout + proc.stderr).strip().splitlines()
    tail = lines[-1].strip() if lines else "(no output)"
    return Result(PASS if proc.returncode == 0 else FAIL, tail)


MANIFEST_REL: Final[str] = ".claude-plugin/marketplace.json"


PUBLISHED_PREFIX: Final[str] = "skills"
# A published card sits at exactly skills/<bucket>/<card>, which is the same
# depth find_cards() globs. Checking the depth rather than only the leading
# segment closes the gap where an entry resolves to a real SKILL.md at some
# other depth under skills/: it would contribute a phantom name to `exposed`,
# match no published card, and be validated by neither direction.
PUBLISHED_DEPTH: Final[int] = 3


class ManifestShapeError(ValueError):
    """The manifest parses as JSON but is not the shape the loader reads.

    Subclasses ValueError so the caller's existing json handler reports it as
    one more unreadable-manifest FAIL. Without this, a manifest of `[]`, `null`,
    `123`, or `{"plugins": ["x"]}` raised AttributeError out of the check, past
    both handlers, and took the whole O1-O6 report down with it before a single
    obligation rendered -- while the docstring promised a FAIL.
    """


def normalised_entry(entry: object) -> tuple[str, bool]:
    """One manifest skill path as posix segments, and whether it escapes root.

    Separators are normalised and `.` segments dropped before any prefix test,
    because `./skills/x`, `././skills/x` and the backslash-separated
    spelling all resolve on disk, while only the first matches a raw
    `startswith`. The code below is the authority on which separators fold.

    Reporting a legitimately published card as "not published" is the most
    alarming label this check has, and it must not be reachable by spelling.
    """
    text = str(entry).replace("\\", "/")
    segments = [s for s in text.split("/") if s not in ("", ".")]
    return "/".join(segments), ".." in segments


def manifest_exposed_cards(root: Path) -> tuple[list[str], list[str], list[str]]:
    """Every published card the manifest names, and the two ways an entry is bad.

    Returns (exposed_names, dangling_paths, off_tree_paths).

    A path is DANGLING when no SKILL.md sits at it -- which covers a renamed
    card and a typo alike, and is the only reading that does not require the
    checker to guess intent.

    A path is OFF-TREE when a SKILL.md does sit at it but the path is outside
    `skills/`. This is its own category because it is the one breach that
    RESOLVES: `_quarantine/` candidates have real SKILL.md files, so a
    quarantine card named by the manifest is neither dangling nor missing, and
    a check built only from those two states reports PASS while shipping an
    unadmitted card to everyone who installs. Demonstrated green on this tree
    before this category existed.
    """
    data = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestShapeError(f"top level is {type(data).__name__}, not an object")
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list):
        raise ManifestShapeError(f"plugins is {type(plugins).__name__}, not an array")

    exposed: list[str] = []
    dangling: list[str] = []
    off_tree: list[str] = []
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            raise ManifestShapeError(
                f"plugins[{index}] is {type(plugin).__name__}, not an object"
            )
        entries = plugin.get("skills", [])
        if not isinstance(entries, list):
            raise ManifestShapeError(
                f"plugins[{index}].skills is {type(entries).__name__}, not an array"
            )
        for entry in entries:
            rel, escapes = normalised_entry(entry)
            segments = rel.split("/")
            if escapes or not (root / rel / "SKILL.md").is_file():
                dangling.append(str(entry))
            elif segments[0] != PUBLISHED_PREFIX or len(segments) != PUBLISHED_DEPTH:
                off_tree.append(str(entry))
            else:
                exposed.append(segments[-1])
    return exposed, dangling, off_tree


def check_plugin_manifest(root: Path) -> Result:
    """O7: the manifest and the published tree name the same cards, both ways.

    Both directions are required, and the repository has the receipt for why.
    The sibling occasions check ran forward-only -- a count could not rise
    without a record -- and an UNDERCOUNT stayed green until August 2026,
    because nothing asked the reverse question. A manifest check that validates
    only the paths it names has exactly that hole: drop a card from the
    manifest and every remaining path still resolves.

    Absent or malformed is FAIL, not CANNOT-CHECK. The manifest is this
    repository's own artifact, so its absence is a breach -- the collection
    ships no install path. CANNOT-CHECK is reserved for what this repository
    genuinely cannot see from inside itself, which is O5 and nothing else.
    """
    manifest = root / MANIFEST_REL
    if not manifest.is_file():
        return Result(
            FAIL,
            f"{MANIFEST_REL} absent: the collection declares no install path, so "
            "the native plugin route does not exist",
        )
    try:
        exposed, dangling, off_tree = manifest_exposed_cards(root)
    except ManifestShapeError as exc:
        return Result(FAIL, f"{MANIFEST_REL} is not a readable manifest: {exc}")
    except ValueError as exc:  # json.JSONDecodeError subclasses ValueError
        return Result(FAIL, f"{MANIFEST_REL} is not parseable JSON: {exc}")
    except OSError as exc:
        return Result(FAIL, f"{MANIFEST_REL} could not be read: {exc}")

    published = [c.name for c in find_cards(root)]
    duplicated = sorted({n for n in exposed if exposed.count(n) > 1})
    unexposed = sorted(set(published) - set(exposed))

    breaches = []
    if dangling:
        breaches.append("named with no card at the path: " + ", ".join(sorted(dangling)))
    if off_tree:
        breaches.append(
            "named but not published -- outside skills/: " + ", ".join(sorted(off_tree))
        )
    if unexposed:
        breaches.append("published but named by no plugin: " + ", ".join(unexposed))
    if duplicated:
        breaches.append("named by more than one plugin: " + ", ".join(duplicated))
    if breaches:
        return Result(FAIL, "; ".join(breaches))
    if not published:
        # Never CANNOT-CHECK. That state is reserved for what this repository
        # genuinely cannot see from inside itself, which is O5 and nothing else;
        # an empty published tree is something this check CAN see, and a
        # manifest check over no cards has checked nothing.
        return Result(
            FAIL,
            "no published cards under this root, so the manifest was compared "
            "against nothing. A run that checked nothing is not a pass",
        )
    return Result(
        PASS,
        f"{len(published)} published card(s), each named exactly once by the "
        "manifest, and every named path resolves",
    )


REPO_CHECKS = {
    "O1": check_declared_formats,
    "O6": check_scoreboard_lockstep,
    "O7": check_plugin_manifest,
}


# ------------------------------------------------------------------ evaluation


@dataclass(frozen=True)
class Report:
    cards: list[Card]
    per_card: dict[str, dict[str, Result]]
    repo_wide: dict[str, Result]

    def counts(self) -> dict[str, int]:
        totals = {PASS: 0, FAIL: 0, CANT: 0}
        for row in self.per_card.values():
            for result in row.values():
                totals[result.verdict] += 1
        for result in self.repo_wide.values():
            totals[result.verdict] += 1
        return totals


# An obligation with no registered check is a hole exactly where the design
# refuses one: it would be stated in the policy, counted nowhere, and silently
# absent from every report. Refused at import so it cannot reach a run.
_UNIMPLEMENTED = [
    o.oid
    for o in OBLIGATIONS
    if o.oid not in (CARD_CHECKS if o.scope == CARD else REPO_CHECKS)
]
if _UNIMPLEMENTED:
    raise SystemExit(
        "REJECTED: obligation(s) with no registered check: "
        + ", ".join(_UNIMPLEMENTED)
        + ". State it and check it, or do not state it."
    )


def evaluate(root: Path, harness_root: Path | None = None) -> Report:
    cards = find_cards(root)
    per_card = {}
    for card in cards:
        row = {}
        for o in CARD_OBLIGATIONS:
            if o.oid == "O5":
                row[o.oid] = check_receipt_agreement(card, harness_root)
            else:
                row[o.oid] = CARD_CHECKS[o.oid](card)
        per_card[card.name] = row
    repo_wide = {o.oid: REPO_CHECKS[o.oid](root) for o in REPO_OBLIGATIONS}
    return Report(cards, per_card, repo_wide)


def render(report: Report, markdown: bool) -> None:
    headers = [o.oid for o in CARD_OBLIGATIONS]
    if markdown:
        print("| Card | " + " | ".join(headers) + " |")
        print("|" + "---|" * (len(headers) + 1))
        for card in report.cards:
            row = report.per_card[card.name]
            print(
                f"| `{card.name}` | "
                + " | ".join(row[oid].verdict for oid in headers)
                + " |"
            )
    else:
        for card in report.cards:
            print(card.name)
            for obligation in CARD_OBLIGATIONS:
                result = report.per_card[card.name][obligation.oid]
                print(
                    f"  {result.verdict:<12} {obligation.oid} "
                    f"{obligation.title} -- {result.detail}"
                )
            print("")

    print("repo-wide obligations (evaluated once over the tree, not per card):")
    for obligation in REPO_OBLIGATIONS:
        result = report.repo_wide[obligation.oid]
        print(
            f"  {result.verdict:<12} {obligation.oid} {obligation.title} "
            f"-- {result.detail}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to check (default: this repository)",
    )
    parser.add_argument(
        "--harness-root",
        type=Path,
        default=None,
        help="path to a skill-harness clone; enables O5 receipt agreement checks",
    )
    parser.add_argument(
        "--markdown", action="store_true", help="emit the per-card table as markdown"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    harness_root = args.harness_root.resolve() if args.harness_root else None

    report = evaluate(root, harness_root)
    if not report.cards:
        print(
            f"REJECTED: no published cards found under {root}/skills. A run that "
            "checked nothing is not a pass.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    render(report, args.markdown)
    totals = report.counts()
    cells = sum(totals.values())
    print("")
    summary = (
        f"{len(report.cards)} card(s) x {len(CARD_OBLIGATIONS)} card obligation(s) "
        f"+ {len(REPO_OBLIGATIONS)} repo obligation(s) = {cells} cells: "
        f"{totals[PASS]} PASS, {totals[FAIL]} FAIL, {totals[CANT]} {CANT}"
    )
    if totals[FAIL]:
        print(f"REJECTED: {CONFORMANCE_VERSION}: {summary}", file=sys.stderr)
        raise SystemExit(1)
    print(
        f"PASS: {CONFORMANCE_VERSION}: {summary}. {CANT} is not a pass -- "
        f"{totals[CANT]} cell(s) were not verified by this run."
    )


if __name__ == "__main__":
    main()
