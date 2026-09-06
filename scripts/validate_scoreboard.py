#!/usr/bin/env python3
"""Assert the front page carries the ruled banner line, that every card's
record is derivable, and that ADMISSION.md declares exactly one canonical
admission-policy version.

A test, not a generator: banners and the README alt stay hand-edited; this
script only refuses drift. Output is ASCII-only so the Windows CI cell does
not die on cp1252 when printing a status line.

The live counts left the banner by owner ruling (2026-08-23, skill-harness
#216): a static graphic that must track repository state is a maintenance tax.
The count DERIVATIONS below survived the ruling on purpose -- they are the
record-conformance discipline (a card that cannot answer is refused, not
guessed at), and the derived numbers are still printed so drift in the records
themselves stays loud.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NoReturn

# The sentence is ruled verbatim (owner ruling 2026-08-23, with the earlier
# scoreboard's own doctrine carried forward): it is matched byte-identically at
# every site, because a check that accepted a paraphrase would let a softened
# or salesier restatement ship. Sites may prefix it (the aria-label and README
# alt lead with "skills -- ") but may not alter a byte of the sentence itself.
RULED_LINE = "These aren't the Claude Code skills you're looking for."
CONTROLLED_FIELDS = ("Screen result", "Paired verdict")

# The origin tier is the other number the front page states about the cards, and
# it drifts the same way the scoreboard does: a card is added, retired, or
# re-tiered and the prose keeps the old arithmetic. The page stated `seven
# OBSERVED, two DESIGNED` while the records read six, two, and one that is
# neither -- inside the sentence explaining why the tiers are kept distinct.
#
# The vocabulary is closed for the same reason the verdict vocabulary is: an
# Origin field opening with a word this file has never seen is not a tier to
# guess at. DISTILLED is a real tier, not a catch-all -- it names a card written
# from research rather than from an incident, which is a weaker provenance claim
# than OBSERVED and must not be folded into it.
ORIGIN_FIELD = "Origin"
ORIGIN_TIERS = ("OBSERVED", "DESIGNED", "DISTILLED")
# Matched on one line, without DOTALL, so the three numbers have to be stated
# together as one claim. A cross-line match would happily pair one passage's
# `6 OBSERVED` with another passage's `1 DISTILLED` and call the page consistent.
ORIGIN_TIER_RE = re.compile(
    r"(\d+)\s+`?OBSERVED`?\b[^\n]*?(\d+)\s+`?DESIGNED`?\b[^\n]*?(\d+)\s+`?DISTILLED`?\b"
)
# The page states the tiering twice, in two sections that are read independently
# ("Where these came from" and "What the receipts are worth"). Both are checked,
# and the count is pinned: silently dropping a site would narrow the guarantee
# without anything going red, which is the partial-edit failure the scoreboard
# check already refuses across its five sites.
ORIGIN_TIER_SITES = 2

# A controlled field opens with its verdict, and the vocabulary is closed. An
# open test ("anything that is not UNMEASURED counts as a result") reads `n/a`,
# `TBD`, `Not yet run.` and an italicised `_UNMEASURED_` as measurements, and
# every one of those errs toward claiming a measurement that did not happen --
# the direction that flatters the page. So: recognised-unmeasured, recognised-
# measured, or refuse. A verdict this file has never seen is not a number to
# guess at.
UNMEASURED_VERDICTS = ("UNMEASURED",)
# CANT_TELL_YET counts as measured on purpose: a screen ran and declined to
# conclude, which is a controlled result. Folding it in with UNMEASURED would
# hide that the run happened.
MEASURED_VERDICTS = ("KEEP", "CUT", "CANT_TELL_YET")

# Buckets whose cards are not part of the collection. AGENTS.md sanctions
# parking unshipped work in `in-progress/`; counting it would make the page
# claim a card was admitted when it never was.
UNSHIPPED_BUCKETS = frozenset({"in-progress"})
POLICY_VERSION_RE = re.compile(r"admission-policy\s+v\d+")
DECLARED_VERSION_RE = re.compile(
    r"\*\*Declared version:\*\*\s*`?(admission-policy\s+v\d+)`?"
)
# The gate card's normative-status header used to pin a policy edition, which this
# module cross-checked against ADMISSION.md. The card retired on 2026-08-31 (#178);
# see check_policy_version for what that removed.


def fail(msg: str) -> NoReturn:
    # ASCII only: no em dash, curly quotes, or middle dots.
    # NoReturn is not decoration: it tells a type checker that every `m.group()`
    # after a `if not m: fail(...)` is reachable only when m is not None, which is
    # what makes the guard clauses below type-safe without redundant asserts.
    print(f"REJECTED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def iter_skill_dirs(root: Path) -> list[Path]:
    skills = root / "skills"
    if not skills.is_dir():
        fail(f"missing skills directory at {skills}")
    found = []
    for bucket in sorted(skills.iterdir()):
        if not bucket.is_dir() or bucket.name.startswith("."):
            continue
        if bucket.name in UNSHIPPED_BUCKETS:
            continue
        for skill in sorted(bucket.iterdir()):
            if skill.is_dir() and (skill / "SKILL.md").is_file():
                found.append(skill)
    return found


def count_admitted(root: Path) -> int:
    return len(iter_skill_dirs(root))


def evidence_fields(evidence: Path, wanted: tuple[str, ...]) -> dict[str, str]:
    """Return the named evidence-table values, keyed by field name.

    Reads the `| **Field** | Value |` rows of the evidence table. A caller that
    asks for the controlled fields needs both present: a card that states neither
    has not been measured *and has not said so*, which is a different thing, and
    the difference is the whole point of the record.

    Two parsing rules keep the derivation pinned to the card's real record:
    rows inside a fenced block are skipped, so a record that documents the row
    format by example cannot become the value; and the FIRST occurrence wins,
    so an illustrative or historical second table appended later cannot silently
    overwrite the canonical one.
    """
    values: dict[str, str] = {}
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
        if name in wanted:
            values.setdefault(name, cells[1])
    return values


def count_measured(root: Path) -> int:
    """Count cards carrying a controlled result, read from their own records.

    A card counts as measured when either controlled field OPENS with a verdict
    from the measured vocabulary. The test is on the start of the value because
    the verdict is the first thing the field says; prose further along may
    discuss an earlier UNMEASURED run without the field itself being one.

    Every path that cannot answer refuses rather than guesses: a missing record,
    a missing or empty controlled field, or a verdict outside the closed
    vocabulary. Deriving `0 measured` from an absent record, or `1 measured`
    from an unrecognised one, would invent the number this line exists to keep
    honest.
    """
    n = 0
    for skill in iter_skill_dirs(root):
        evidence = skill / "EVIDENCE.md"
        if not evidence.is_file():
            fail(
                f"{skill.name}: no EVIDENCE.md, so the measured count cannot be "
                f"derived. The front page states how many cards carry a controlled "
                f"result; a card with no record cannot answer that either way, and "
                f"counting it as unmeasured would invent the answer."
            )
        values = evidence_fields(evidence, CONTROLLED_FIELDS)
        # An absent row and a present-but-empty one are the same refusal: the
        # card has not said. Only the blank case is worth calling out separately,
        # because "not UNMEASURED" would otherwise read a blank as a result and
        # silently inflate the count in the direction that flatters the page.
        missing = [f for f in CONTROLLED_FIELDS if not values.get(f, "").strip("* `")]
        if missing:
            fail(
                f"{skill.name}: EVIDENCE.md has no stated {' and no stated '.join(missing)}, "
                f"so the measured count cannot be derived from it. An empty controlled "
                f"field is not a result."
            )
        verdicts = {}
        for f in CONTROLLED_FIELDS:
            opening = values[f].lstrip("* `_").upper()
            if opening.startswith(UNMEASURED_VERDICTS):
                verdicts[f] = False
            elif opening.startswith(MEASURED_VERDICTS):
                verdicts[f] = True
            else:
                fail(
                    f"{skill.name}: {f} opens with an unrecognised verdict "
                    f"({values[f][:40]!r}). The vocabulary is closed - "
                    f"{', '.join(UNMEASURED_VERDICTS + MEASURED_VERDICTS)} - because "
                    f"reading an unknown opening as a result claims a measurement "
                    f"that may never have happened. Say which it is, or extend the "
                    f"vocabulary deliberately."
                )
        if any(verdicts.values()):
            n += 1
    return n


def measured_card_names(root: Path) -> set[str]:
    """The cards whose own records carry a controlled result.

    Same derivation as `count_measured`, returning identities instead of a
    count, so the page can be checked against WHICH cards rather than how many.
    """
    names = set()
    for skill in iter_skill_dirs(root):
        values = evidence_fields(skill / "EVIDENCE.md", CONTROLLED_FIELDS)
        for field in CONTROLLED_FIELDS:
            if values.get(field, "").lstrip("* `_").upper().startswith(MEASURED_VERDICTS):
                names.add(skill.name)
                break
    return names


CONTROLLED_SECTION_RE = re.compile(
    r"^### Controlled results$(.*?)(?=^#{2,3} )", re.MULTILINE | re.DOTALL
)


def check_controlled_section_restates_nothing(root: Path) -> None:
    """The page may name which cards are measured. It may not restate their values.

    Two rules, and the second is the one drift needs.

    1. The cards named in the section are exactly the cards whose records carry
       a controlled result. Naming a card that is not measured, or omitting one
       that is, is the count-drift this file already refuses, at card identity.

    2. No measured verdict appears in the section at all. A verdict, a date or a
       receipt restated in prose is a SECOND COPY of a value the card's own
       EVIDENCE.md owns, and a second copy drifts from the first with nothing
       going red. That is not hypothetical: the section carried
       `paired verdict: not yet established` for three days after the card
       recorded `CANT_TELL_YET` with a dated receipt, and every check in this
       file passed throughout, because none of them read the prose.

    The rule is therefore "point at the record", not "keep the copy accurate".
    An accurate copy is still a copy, and the next edit to the card desynchronises
    it again.

    UNMEASURED is deliberately allowed: it is the section's residual statement
    about every OTHER card ("every other card is UNMEASURED"), it is derivable
    from the absence of a measured verdict, and it cannot drift toward claiming
    a measurement that did not happen -- which is the direction this whole file
    guards.
    """
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    match = CONTROLLED_SECTION_RE.search(text)
    if match is None:
        fail(
            "README.md has no '### Controlled results' section. The section is where "
            "the page states which cards carry a controlled result; if it moved or "
            "was renamed, this check stopped guarding it and must be repointed rather "
            "than left to pass vacuously."
        )
    section = match.group(1)

    measured = measured_card_names(root)
    named = {skill.name for skill in iter_skill_dirs(root) if skill.name in section}
    if named != measured:
        fail(
            f"README.md 'Controlled results' names {sorted(named)} but the cards' own "
            f"records carry a controlled result for {sorted(measured)}. The page and "
            f"the records disagree about which cards are measured."
        )

    restated = [v for v in MEASURED_VERDICTS if v in section]
    if restated:
        fail(
            f"README.md 'Controlled results' restates the verdict(s) {restated}. "
            f"A verdict belongs in the card's EVIDENCE.md, and the page points at it. "
            f"A copy on the page drifts from the record with nothing going red - which "
            f"is exactly how 'paired verdict: not yet established' outlived the "
            f"CANT_TELL_YET it contradicted. Link the record instead of quoting it."
        )


def derive_origin_tiers(root: Path) -> tuple[int, int, int]:
    """Count the cards in each origin tier, read from their own records.

    Same refusal discipline as the measured count: a missing record, a missing
    Origin row, or an opening word outside the closed vocabulary is a refusal,
    not a zero. The front page tells a reader how many cards trace to a real
    incident; deriving that from a card that has not said would invent exactly
    the number the line exists to keep honest.
    """
    counts = dict.fromkeys(ORIGIN_TIERS, 0)
    for skill in iter_skill_dirs(root):
        evidence = skill / "EVIDENCE.md"
        if not evidence.is_file():
            fail(
                f"{skill.name}: no EVIDENCE.md, so its origin tier cannot be derived. "
                f"The front page states how many cards came from a real incident; a "
                f"card with no record cannot answer that either way."
            )
        value = evidence_fields(evidence, (ORIGIN_FIELD,)).get(ORIGIN_FIELD, "")
        opening = value.lstrip("* `_").upper()
        for tier in ORIGIN_TIERS:
            if opening.startswith(tier):
                counts[tier] += 1
                break
        else:
            fail(
                f"{skill.name}: Origin opens with an unrecognised tier "
                f"({value[:40]!r}). The vocabulary is closed - "
                f"{', '.join(ORIGIN_TIERS)} - because reading an unknown opening as "
                f"an incident claims a provenance the card may not have. Say which "
                f"tier it is, or extend the vocabulary deliberately."
            )
    return tuple(counts[t] for t in ORIGIN_TIERS)  # type: ignore[return-value]


def check_origin_tiers(root: Path) -> None:
    expected = derive_origin_tiers(root)
    readme = root / "README.md"
    if not readme.is_file():
        fail(f"missing {readme}")
    found = ORIGIN_TIER_RE.findall(readme.read_text(encoding="utf-8"))
    # Stating a tally is optional; stating a wrong one is not. An earlier
    # edition demanded exactly ORIGIN_TIER_SITES statements, which made the
    # page's arithmetic mandatory: a card entering or leaving turned this
    # check red until someone re-derived two numbers by hand. Owner ruling
    # 2026-08-24 retired the page's counts for that reason, which is the same
    # reason the banner's counts were retired on 2026-08-23 - a surface that
    # must track repository state is a maintenance tax, and this one had no
    # reader on the other end. The guarantee that survives is the one worth
    # keeping: EVERY tally the page does state must agree with the records,
    # so a figure here can be wrong but cannot be wrong quietly. Zero is a
    # legal number of tallies; one is legal; ten are legal and all ten are
    # checked. ORIGIN_TIER_SITES is retained as the count the page carried
    # when the requirement was dropped, so the history is readable.
    for i, site in enumerate(found, start=1):
        got = tuple(int(n) for n in site)
        if got == expected:
            continue
        disagreements = [
            f"{tier} {g} != {w}"
            for tier, g, w in zip(ORIGIN_TIERS, got, expected)
            if g != w
        ]
        fail(
            f"README.md origin-tier statement {i}: disagrees with the cards' Origin "
            f"fields - " + "; ".join(disagreements)
        )


def table_row_count(text: str, heading_prefix: str) -> int:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith(heading_prefix):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith("|"):
            j += 1
        if j >= len(lines):
            fail(f"no table under heading starting {heading_prefix!r}")
        # header row
        j += 1
        if j < len(lines) and re.match(r"^\|[\s|:-]+$", lines[j]):
            j += 1
        count = 0
        while j < len(lines) and lines[j].startswith("|"):
            count += 1
            j += 1
        return count
    fail(f"heading not found: {heading_prefix!r}")


def derive_counts(root: Path) -> tuple[int, int, int, int]:
    retired_md = root / "RETIRED.md"
    if not retired_md.is_file():
        fail(f"missing {retired_md}")
    text = retired_md.read_text(encoding="utf-8")
    admitted = count_admitted(root)
    measured = count_measured(root)
    retired = table_row_count(text, "## Retired from the collection")
    turned = table_row_count(text, "## Screened out at the gate")
    return admitted, measured, retired, turned


def assert_site(label: str, text: str) -> None:
    # Byte-identical containment, not a pattern: the sentence's judgement is
    # deliberate, and a match that tolerated an "are not", a dropped period, or
    # a straightened apostrophe would let the softening ship. HTML entities are
    # not decoded on purpose -- a site that encodes the apostrophe has changed
    # the bytes a reader's tooling sees, and the fix is to say so at the site.
    if RULED_LINE in text:
        return
    fail(
        f"{label}: does not carry the ruled banner line verbatim "
        f"({RULED_LINE!r}). The wording is ruled (2026-08-23); a site may "
        f"prefix it but not alter it."
    )


def check_banner_line_sites(root: Path) -> None:
    sites = [
        ("assets/banner-light.svg aria-label", root / "assets" / "banner-light.svg", True),
        ("assets/banner-light.svg text", root / "assets" / "banner-light.svg", False),
        ("assets/banner-dark.svg aria-label", root / "assets" / "banner-dark.svg", True),
        ("assets/banner-dark.svg text", root / "assets" / "banner-dark.svg", False),
        ("README.md img alt", root / "README.md", False),
    ]
    for label, path, aria_only in sites:
        if not path.is_file():
            fail(f"{label}: missing file {path}")
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".svg" and aria_only:
            m = re.search(r'aria-label="([^"]*)"', text)
            if not m:
                fail(f"{label}: no aria-label")
            assert_site(label, m.group(1))
        elif path.suffix == ".svg":
            # Rendered text element(s), not the aria-label. The two-element
            # minimum is kept from the scoreboard era: texts[-1] is the banner
            # line only while the wordmark is still a separate element, and a
            # banner collapsed to one <text> would silently point this check at
            # the wrong string.
            texts = re.findall(r"<text\b[^>]*>(.*?)</text>", text, flags=re.DOTALL)
            if len(texts) < 2:
                fail(f"{label}: expected a banner-line <text> element")
            assert_site(label, texts[-1])
        elif path.name == "README.md":
            m = re.search(r'<img\b[^>]*\balt="([^"]*)"', text)
            if not m:
                fail(f"{label}: no img alt on banner")
            assert_site(label, m.group(1))
        else:
            assert_site(label, text)


def policy_version(root: Path) -> str:
    """Return the ONE authoritative version declared in ADMISSION.md.

    Two properties are asserted here, and both are load-bearing:

      1. The canonical declaration EXISTS. There is deliberately no fallback to
         "any version string in the file". A fallback makes the check pass after
         the canonical line is deleted, which is a silent downgrade to a weaker
         guarantee than the one this function claims to provide.
      2. It is the ONLY occurrence. The governing decision on this was that
         fewer declaration sites beat a smarter checker: with one site, a partial
         bump cannot be expressed, so it cannot be missed. Restating the string
         elsewhere in the file re-creates exactly the drift this guards against.

    Tradeoff, stated because it is real: this refuses a legitimate quotation of a
    historical version inside ADMISSION.md (a migration example, or "what v1 used
    to say"). That failure is loud and self-explaining rather than silent, and the
    fix is to reference the declaration instead of restating the string.
    """
    path = root / "ADMISSION.md"
    if not path.is_file():
        fail(f"missing {path}")
    text = path.read_text(encoding="utf-8")
    m = DECLARED_VERSION_RE.search(text)
    if not m:
        fail(
            "ADMISSION.md: no canonical '**Declared version:** `admission-policy vN`' "
            "line. That line is the single authoritative declaration, and the only "
            "place this policy states its edition."
        )
    declared = m.group(1)
    occurrences = POLICY_VERSION_RE.findall(text)
    if len(occurrences) != 1:
        fail(
            f"ADMISSION.md: expected exactly 1 admission-policy version string, "
            f"found {len(occurrences)} ({', '.join(sorted(set(occurrences)))}). "
            f"Keep one canonical declaration and reference it in prose elsewhere "
            f"rather than restating the version, so a partial bump cannot happen."
        )
    return declared


def check_policy_version(root: Path) -> None:
    """Assert ADMISSION.md declares exactly one canonical policy version.

    This check used to have a second half. It read the gate card's
    normative-status header and required that pin to equal ADMISSION.md's
    declaration, so a partial version bump across the two files was caught.
    `skill-necessity-gate` was retired on 2026-08-31 (issue #178) and that half
    went with it.

    The lost guarantee is named here rather than left to be discovered: the
    collection no longer asserts that a policy edition and its reference method
    agree, because there is no longer a reference method to disagree. This is a
    smaller assurance surface than before. What survives is the stronger half --
    `policy_version` refuses any ADMISSION.md that does not carry exactly one
    canonical declaration, so a partial bump still cannot be expressed in the
    file that binds.

    Restore the card half if a future card is ever named the policy's reference
    method and pins an edition of its own.
    """
    policy_version(root)


def validate(root: Path) -> None:
    # The counts are derived but no longer asserted against a page site: the
    # derivation IS the check now (a card that cannot answer is refused), and
    # printing the numbers keeps them observable without a graphic to rot.
    admitted, measured, retired, turned = derive_counts(root)
    check_banner_line_sites(root)
    check_policy_version(root)
    check_origin_tiers(root)
    check_controlled_section_restates_nothing(root)
    observed, designed, distilled = derive_origin_tiers(root)
    print(
        f"PASS: ruled banner line pinned at 5 sites; records derive "
        f"{admitted} admitted, {measured} measured, {retired} retired, "
        f"{turned} solutions looking for a problem; admission policy declares one "
        f"canonical version; "
        f"origin tiers {observed} OBSERVED, {designed} DESIGNED, {distilled} DISTILLED agree"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root to validate (default: two levels above this script)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parent.parent
    validate(root)


if __name__ == "__main__":
    main()
