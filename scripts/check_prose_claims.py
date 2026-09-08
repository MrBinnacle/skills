#!/usr/bin/env python3
"""Refuse a README that asserts something about the tree the tree does not support.

WHY THIS EXISTS

    On 2026-09-08 three reader-facing surfaces were found asserting things that
    were false, with every gate in this repository green:

    1. `README.md` stated the card count eleven times, in prose no check
       anchored to. The same page also asserted that it "states no tally ...
       deliberately".
    2. `_quarantine/README.md` said, in bold, "No candidate in this directory
       currently carries an `EVIDENCE.md`." Three candidates carried one.
    3. `_quarantine/self-documenting-code/README.md` documented a package with
       `references/`, `assets/` and `scripts/` subdirectories and the command
       `python scripts/validate_package.py .`. The files are flat and that path
       does not exist.

    The repository already had three derive-and-compare checks: the origin-tier
    and controlled-results checks in `validate_scoreboard.py`, and
    `validate_disposition_counts.py`. Every one is a regex anchored to a known
    sentence in a known section. `validate_disposition_counts.py` guards four
    phrases inside `## Admission method` alone. All three defects sat in
    sentences no anchor reaches, which is why a fourth anchored regex is not the
    repair: it would guard the sentences already deleted and miss the next one.

WHAT IT CHECKS

    Two things, neither anchored to a sentence.

    ENUMERATION. A group README enumerates the cards in its group. The set it
    names must equal the set of directories on disk, in BOTH directions: a card
    the README omits is as much a defect as a card the README invents. This is
    the shape defect 2 had.

    DOCUMENTED PATHS. A README that draws its own layout in a fenced block is
    making a claim about the filesystem. Every path in such a block must exist
    relative to that README. This is defect 3 exactly.

    A count in prose is NOT checked here, and deliberately so. Verifying a
    stated number keeps the number on the page, where it goes stale between one
    run of CI and one reader's browser. `styles/Claims/` bans the number
    instead, and the card-evidence table CI rebuilds is the one surface where a
    number is derived on read.

POPULATION INTEGRITY

    Both checks are enumeration-driven: they discover their own inputs. Such a
    control can execute perfectly against the wrong universe and report a
    confident pass. `scripts/vendor/population.py` is a byte-equal copy of
    skill-harness's contract for exactly this, which reports a third verdict,
    UNINTERPRETABLE, when the analysed set cannot be established as the declared
    set. A refusal to answer is not a pass.

    This module is that contract's second consumer. The first is
    skill-harness's own `tests/test_receipts_index.py`.

Exit 0 on pass, 1 on refusal with the reason, 2 when the tree cannot be read.

Run: python scripts/check_prose_claims.py [--root PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vendor.population import (  # noqa: E402
    PopulationVerdict,
    build_population_record,
    interpret,
)

#: A card name as a group README writes it: bold, kebab-case.
CARD_IN_PROSE = re.compile(r"\*\*([a-z0-9]+(?:-[a-z0-9]+)+)\*\*")

#: A fenced block that draws a layout. The language tag is `text` in every
#: current instance; an untagged block is included because the claim is in the
#: content, not the tag.
FENCED = re.compile(r"^```(\w*)\n(.*?)^```", re.MULTILINE | re.DOTALL)

#: A path as a layout block writes it: a leading token ending in `/` or
#: carrying a file extension. Trailing prose after two spaces is a comment.
PATH_LINE = re.compile(r"^\s*([A-Za-z0-9_./-]+/?)(?:\s{2,}.*)?$")


class Refusal(Exception):
    """The tree cannot be read, so no verdict is available."""


def vendor_is_intact(root: Path) -> list[str]:
    """The vendored contract is byte-equal to the digest recorded for it.

    A local edit to the contract must fail rather than fork it silently, which
    is the same rule `validate_vale_style.py` applies to the vendored Vale style.

    Checked under ROOT, not under this script's own directory. The first version
    read `__file__`'s neighbour, so `--root` was ignored and the check always
    examined the live repository whatever tree it was pointed at. Its negative
    control caught that on the first run: a fixture with a deliberately edited
    contract was ACCEPTED, because the bytes being hashed were never the
    fixture's. A check no fixture can exercise cannot be shown to work.
    """
    vendor_dir = root / "scripts" / "vendor"
    manifest_path = vendor_dir / "POPULATION_SOURCE.json"
    if not manifest_path.is_file():
        raise Refusal(f"{manifest_path} is missing, so the vendored contract is unpinned")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    recorded = manifest.get("files", {})
    if not recorded:
        raise Refusal(f"{manifest_path} records no file, so it asserts nothing")
    failures = []
    for name, digest in sorted(recorded.items()):
        path = vendor_dir / name
        if not path.is_file():
            failures.append(f"vendored contract {name} is named in the manifest and is missing")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            failures.append(
                f"vendored contract {name} does not match its pinned digest "
                f"(recorded {digest[:12]}..., found {actual[:12]}...). Re-vendor from "
                f"{manifest.get('source_repo', 'the source repository')} rather than editing "
                "the copy or the digest."
            )
    return failures


def group_dirs(root: Path) -> list[Path]:
    """Every published group that carries a README enumerating its cards."""
    skills = root / "skills"
    if not skills.is_dir():
        raise Refusal(f"{skills} is not a directory, so no group can be enumerated")
    return sorted(d for d in skills.iterdir() if d.is_dir() and (d / "README.md").is_file())


def check_group_enumerations(root: Path) -> list[str]:
    """Each group README names exactly the cards its directory holds."""
    groups = group_dirs(root)
    if not groups:
        raise Refusal(
            "no group README was found under skills/, so this check examined nothing. "
            "A check that passes because it read no input is the defect it exists to catch."
        )
    failures: list[str] = []
    for group in groups:
        on_disk = sorted(d.name for d in group.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())
        named = sorted(set(CARD_IN_PROSE.findall((group / "README.md").read_text(encoding="utf-8"))))
        # Only names that ARE cards in this group can be enumeration claims; a
        # bold kebab-case phrase naming something else is prose, not a claim.
        declared = sorted(n for n in named if n in set(on_disk)) + sorted(
            n for n in named if n not in set(on_disk) and _looks_like_a_card_claim(n, group)
        )
        record = build_population_record(analyzed=on_disk, declared=declared)
        verdict = interpret(record, [])
        label = f"skills/{group.name}/README.md"
        if verdict is PopulationVerdict.UNINTERPRETABLE:
            if record.missing:
                failures.append(
                    f"{label}: enumerates a card that is not in skills/{group.name}/: "
                    + ", ".join(record.missing)
                )
            if record.unexpected:
                failures.append(
                    f"{label}: skills/{group.name}/ holds a card the README does not name: "
                    + ", ".join(record.unexpected)
                    + ". A reader of the group page is told the group is smaller than it is."
                )
    return failures


def _looks_like_a_card_claim(name: str, group: Path) -> bool:
    """Whether a bold kebab-case name is asserting a card in THIS group.

    A group README legitimately mentions a card from another group, or a tool.
    The claim under test is "this group contains this card", so a name counts
    only when the README also links it as a sibling path.
    """
    text = (group / "README.md").read_text(encoding="utf-8")
    return f"]({name}/" in text


def tracked_readmes(root: Path) -> list[Path]:
    """Every tracked README, enumerated with git rather than a filesystem walk.

    `rglob` reaches untracked working directories -- a sandcastle worktree, a
    build output -- and reports a claim in a file this repository does not
    publish. It also does not follow the Windows junctions this tree carries.
    `git ls-files` is the enumeration that matches what a reader can fetch.
    """
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "*README.md"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Refusal(
            f"git ls-files failed in {root}, so the set of published READMEs cannot be "
            f"established: {result.stderr.strip()}"
        )
    names = [line for line in result.stdout.splitlines() if line.strip()]
    return sorted(root / name for name in names if "fixtures/" not in name)


def check_documented_paths(root: Path) -> list[str]:
    """Every path a README draws in a fenced layout block exists."""
    readmes = tracked_readmes(root)
    if not readmes:
        raise Refusal(
            "git ls-files returned no tracked README.md, so this check examined nothing. "
            "A check that passes because it read no input is the defect it exists to catch."
        )
    failures: list[str] = []
    for readme in readmes:
        claimed = _paths_claimed(readme.read_text(encoding="utf-8"))
        if not claimed:
            continue
        analyzed = sorted(c for c in claimed if (readme.parent / c.rstrip("/")).exists())
        record = build_population_record(analyzed=analyzed, declared=sorted(claimed))
        if interpret(record, []) is PopulationVerdict.UNINTERPRETABLE and record.missing:
            rel = readme.relative_to(root).as_posix()
            failures.append(
                f"{rel}: draws a layout naming path(s) that do not exist beside it: "
                + ", ".join(record.missing)
                + ". The block is a claim about the filesystem, and a reader who follows "
                "it arrives nowhere."
            )
    return failures


def _paths_claimed(text: str) -> set[str]:
    """Paths a fenced layout block asserts, relative to the README beside it.

    Only blocks that look like a directory drawing are read: a block qualifies
    when at least two of its lines parse as a path and at least one names a
    directory. That keeps command blocks and code samples out, since a command
    block's paths are instructions rather than assertions about this tree.
    """
    claimed: set[str] = set()
    for _language, body in FENCED.findall(text):
        del _language  # the claim is in the block's content, not its language tag
        candidates: set[str] = set()
        # A layout block is an INDENTED TREE. A line indented under `skills/`
        # names `skills/engineering/`, not `engineering/`. Reading each line as
        # a top-level path is how the first run of this check reported the
        # repository's own README as claiming three directories that do not
        # exist -- they exist, one level down.
        stack: list[tuple[int, str]] = []
        for line in body.splitlines():
            if not line.strip():
                continue
            if line.lstrip().startswith(("#", "$", ">", "npx ", "python ", "/", "git ")):
                continue
            match = PATH_LINE.match(line)
            if not match:
                continue
            token = match.group(1)
            if token in {".", "..", "/"} or token.startswith(("http", "~")):
                continue
            if "/" not in token and "." not in token:
                continue
            indent = len(line) - len(line.lstrip())
            while stack and stack[-1][0] >= indent:
                stack.pop()
            prefix = stack[-1][1] if stack else ""
            full = prefix + token
            candidates.add(full)
            if token.endswith("/"):
                stack.append((indent, full))
        if len(candidates) >= 2 and any(c.endswith("/") for c in candidates):
            claimed |= candidates
    return claimed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.resolve()

    try:
        failures = vendor_is_intact(root)
        failures += check_group_enumerations(root)
        failures += check_documented_paths(root)
    except Refusal as refusal:
        print(f"UNINTERPRETABLE: {refusal}")
        return 2

    if failures:
        for failure in failures:
            print(f"REJECTED: {failure}")
        return 1

    groups = len(group_dirs(root))
    print(
        f"PASS: {groups} group README(s) enumerate exactly the cards on disk, both "
        "directions; every path drawn in a README layout block exists; the vendored "
        "population contract matches its pinned digest"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
