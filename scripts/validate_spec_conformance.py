#!/usr/bin/env python3
"""Run the OFFICIAL Agent Skills reference validator over both card trees.

WHY THIS ONE IS DIFFERENT FROM THE OTHER SEVEN
    Every other conformance instrument in this repository was written by its
    maintainer, which means every one of them can be wrong in the same
    direction as the cards it grades. `skills-ref` is the specification's own
    reference implementation. Adopting it is the only check here whose author
    has no stake in this collection passing.

    That is not theoretical. On 2026-08-24 this validator's first run over the
    live tree rejected TWO PUBLISHED CARDS for invalid YAML frontmatter --
    `click-clirunner-env-none-deletes` and `router-skill-predicate-gap` -- each
    carrying an unquoted description scalar containing a `: ` or a `{`. Claude
    Code's own parser tolerates both and the cards work; a specification-
    conformant reader cannot load either. No local gate saw it, because no local
    gate reads frontmatter. Both were quoted in the same change that added this
    script.

DECLARED DIVERGENCES, AND WHY EACH IS ALLOWED RATHER THAN FIXED
    A blanket "ignore failures" would make this gate decorative. Instead each
    tolerated error is named, scoped to a tree, and carries its reason. Anything
    not on this list fails the run.

    published tree (`skills/`) -- ONE allowance:
      * `disable-model-invocation` is not in the specification's frontmatter
        vocabulary, and it is a real Claude Code key with load-bearing
        behaviour: it is what stops a procedure card auto-firing. Dropping it to
        satisfy the validator would change how four published cards behave in
        the product in order to satisfy a document. The key stays; the
        divergence is recorded here and in AGENTS.md.

    candidate tree (`_quarantine/`) -- the allowances promotion already closes:
      * `author` / `date` / `version` frontmatter keys. AGENTS.md step 2a
        strips these on promotion. They are spec-LEGAL under `metadata:` but are
        written bare here, and the promotion step is where that is normalised.
      * a `description` over the specification's 1024-character limit. AGENTS.md
        step 2a rewrites every candidate description to 200 characters on
        promotion, which is a stricter bar than the specification's.
      * `disable-model-invocation`, for the reason above.

    The asymmetry is the point. `skills/` is what ships and is held to the
    specification. `_quarantine/` is a queue whose entry conditions AGENTS.md
    already states, and re-stating them here as a merge blocker would stop the
    harvest rather than improve it. Measured 2026-08-24: 11 of 16 candidates
    fail on those three classes alone, so enforcing the published bar over the
    queue would have reddened the build on the day it was adopted.

    A candidate failing for ANY OTHER reason -- malformed YAML, a missing
    `name`, an unreadable file -- fails this run, which is the property that
    keeps a non-conforming card out of the promotion queue.

Output is ASCII-only so the Windows CI cell does not die on cp1252, matching
the other validators. Run with PYTHONUTF8=1.

Usage:
    python scripts/validate_spec_conformance.py
    python scripts/validate_spec_conformance.py --root <tree>
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final

SCRIPT_DIR = Path(__file__).resolve().parent

SPEC_PACKAGE: Final[str] = "skills-ref@0.1.5"

PUBLISHED_TREE: Final[str] = "skills"
CANDIDATE_TREE: Final[str] = "_quarantine"

# One entry per tolerated error, as (pattern, reason). The pattern is matched
# against a single error line from the reference validator. A tolerated error is
# still REPORTED -- it is subtracted from the failure count, never hidden.
# The reference validator appends an explanatory clause after the field list
# ("... Only allowed-tools, compatibility, ... are allowed."). The patterns stop
# at the period that ends the field list, so the FIELD LIST ITSELF must match
# exactly: a card carrying `disable-model-invocation` AND some other unexpected
# key does not match, and fails. Matching a bare prefix would have tolerated the
# unknown key riding alongside the known one.
PUBLISHED_ALLOWANCES: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    (
        re.compile(r"^Unexpected fields in frontmatter: disable-model-invocation\."),
        "live Claude Code key, load-bearing: it stops a procedure card auto-firing",
    ),
)

CANDIDATE_ALLOWANCES: Final[tuple[tuple[re.Pattern[str], str], ...]] = (
    PUBLISHED_ALLOWANCES[0],
    (
        re.compile(
            r"^Unexpected fields in frontmatter: "
            r"(?:author|date|version)(?:, (?:author|date|version))*\."
        ),
        "stripped on promotion by AGENTS.md step 2a",
    ),
    (
        re.compile(r"^Description exceeds 1024 character limit \(\d+ chars\)$"),
        "rewritten to 200 characters on promotion by AGENTS.md step 2a",
    ),
)


def allowance_for(
    line: str, allowances: tuple[tuple[re.Pattern[str], str], ...]
) -> str | None:
    """The recorded reason this error is tolerated, or None if it is not."""
    for pattern, reason in allowances:
        if pattern.match(line.strip()):
            return reason
    return None


def error_lines(output: str) -> list[str]:
    """The individual errors from a `skills-ref validate` failure.

    The CLI prints a `Validation failed for <path>:` header and then one
    `  - <error>` bullet per problem. Reading the bullets rather than the whole
    blob is what lets one card carry a tolerated error and a fatal one at once
    and still be reported as failing.
    """
    return [
        line.strip()[2:].strip()
        for line in output.splitlines()
        if line.strip().startswith("- ")
    ]


def card_dirs(root: Path, tree: str) -> list[Path]:
    """Card directories under one tree, from git rather than a filesystem walk.

    `git ls-files` is used for the same reason AGENTS.md gives elsewhere: on
    this maintainer's Windows host the published cards are junctions, and a
    plain walk silently undercounts them.
    """
    proc = subprocess.run(
        ["git", "ls-files", f"{tree}/**/SKILL.md"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return [root / line.rsplit("/", 1)[0] for line in proc.stdout.split() if line]


def spec_cli_available() -> bool:
    return shutil.which("npx") is not None


def validate_card(root: Path, card: Path) -> tuple[int, str]:
    rel = card.relative_to(root).as_posix()
    proc = subprocess.run(
        ["npx", "-y", SPEC_PACKAGE, "validate", rel],
        cwd=root,
        capture_output=True,
        text=True,
        shell=sys.platform == "win32",
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Skills spec conformance")
    parser.add_argument("--root", type=Path, default=SCRIPT_DIR.parent)
    args = parser.parse_args()
    root = args.root.resolve()

    if not spec_cli_available():
        print(
            "REJECTED: npx is not on PATH, so the reference validator could not "
            "run. A gate that silently skips is worse than no gate.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    trees = (
        (PUBLISHED_TREE, PUBLISHED_ALLOWANCES),
        (CANDIDATE_TREE, CANDIDATE_ALLOWANCES),
    )
    scanned = 0
    tolerated = 0
    breaches: list[str] = []

    for tree, allowances in trees:
        cards = card_dirs(root, tree)
        if tree == PUBLISHED_TREE and not cards:
            print(
                f"REJECTED: no cards found under {tree}/. A run that checked "
                "nothing is not a pass.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        for card in cards:
            scanned += 1
            code, output = validate_card(root, card)
            if code == 0:
                continue
            rel = card.relative_to(root).as_posix()
            errors = error_lines(output)
            if not errors:
                breaches.append(f"{rel}: nonzero exit with no parseable error: {output.strip()[:120]}")
                continue
            for line in errors:
                reason = allowance_for(line, allowances)
                if reason is None:
                    breaches.append(f"{rel}: {line}")
                else:
                    tolerated += 1
                    print(f"allowed  {rel}: {line}  [{reason}]")

    summary = (
        f"{scanned} card(s) checked against {SPEC_PACKAGE}; "
        f"{tolerated} declared divergence(s) tolerated and reported; "
        f"{len(breaches)} breach(es)"
    )
    if breaches:
        for breach in breaches:
            print(f"BREACH   {breach}", file=sys.stderr)
        print(f"REJECTED: {summary}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {summary}. A tolerated divergence is not a silent pass.")


if __name__ == "__main__":
    main()
