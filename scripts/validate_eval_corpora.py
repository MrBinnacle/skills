#!/usr/bin/env python3
"""Require every published card to ship one structural eval corpus.

A card states behavioural claims and records evidence for them. Neither says
what a run against the card should ASSERT. This script is the check behind the
missing half: exactly one `evals/evals.json` per published card, naming the
card it belongs to and holding cases a runner could execute.

WHAT A CORPUS IS, AND WHAT IT IS NOT
    A corpus is a CONTRACT. It describes what a run should assert. It records
    no run, no score and no verdict, and its presence says nothing about
    whether the card earns its keep. Every card's evidence verdict is set by
    the measurement instrument, not by this file existing. Nothing here reads
    or writes an EVIDENCE.md, on purpose: a checker that could touch a verdict
    is a checker that could manufacture one.

WHY THIS IS A SEPARATE SCRIPT
    validate_skill_formats.py has one subject -- the declared readable file
    vocabulary SECURITY.md commits to -- and `.json` is already in it, so a
    corpus is admissible there as-is. Widening that gate to also carry corpus
    SEMANTICS would give one security check two unrelated meanings, and a
    security check nobody can read in one sitting is the failure this
    collection exists to refuse. The vocabulary question and the corpus
    question are checked separately because they are separate questions.

DISCOVERY, AND WHY IT IS BORROWED
    validate_card_files.find_cards, imported rather than restated. That
    function is what makes the repository's "N published card(s)" one number:
    it walks by directory, honours the unshipped buckets AGENTS.md sanctions,
    and skips dot-directories. A second walk here would eventually disagree
    with it about exactly the cards a maintainer is arguing about.

    The consequence worth stating: the fixture trees under scripts/fixtures/
    are inputs to OTHER validators, they sit outside `<root>/skills/`, and
    this check never reaches them. Requiring a corpus of them would turn every
    one of those fixtures red for a file they do not owe.

Output is ASCII-only so the Windows CI cell cannot die on cp1252 while printing
a status line, matching validate_scoreboard.py and validate_skill_formats.py.
Corpus text is quoted through ascii(), never through repr(), so a non-ASCII
byte inside a corpus is reported rather than raised at the console.

Usage:
    python scripts/validate_eval_corpora.py
    python scripts/validate_eval_corpora.py --root <tree>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Final

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_card_files as card_files  # noqa: E402

CORPUS_DIR: Final[str] = "evals"
CORPUS_FILE: Final[str] = "evals.json"
CORPUS_PATH: Final[str] = f"{CORPUS_DIR}/{CORPUS_FILE}"

# Three cases is the floor because one case is an anecdote and two cannot show
# a pattern. It is a floor, not a target.
MIN_CASES: Final[int] = 3

# Two assertions is the floor because a single assertion makes a case that
# passes on one property indistinguishable from a case that was never
# falsifiable. It is a floor, not a target.
MIN_ASSERTIONS: Final[int] = 2

# A prompt shorter than this is a label, not a situation. The number is a
# judgement and is stated here rather than buried: a runner cannot reproduce
# the situation a card fires in from "fix the build".
MIN_PROMPT_CHARS: Final[int] = 40

# The corpus vocabulary is CLOSED (cross-review finding, 2026-08-24). A
# contract file that accepts unknown keys can grow measurement-shaped keys --
# verdict, score, result, passed -- and become a self-certified measurement
# record, the exact shape the docstring above says this checker exists to
# refuse; a typo'd optional ("notes", "Note") also drifts silently. `note` is
# the one free-text optional, at both levels, because the live corpora carry
# it.
TOP_LEVEL_KEYS: Final[frozenset[str]] = frozenset({"skill_name", "cases", "note"})
CASE_KEYS: Final[frozenset[str]] = frozenset(
    {"id", "prompt", "expected_output", "assertions", "note"}
)

FRONTMATTER_NAME_RE: Final[re.Pattern[str]] = re.compile(
    r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL
)
NAME_LINE_RE: Final[re.Pattern[str]] = re.compile(r"^name:\s*(\S.*?)\s*$", re.MULTILINE)


def quote(value: object, limit: int = 60) -> str:
    """ASCII-safe, bounded rendering of untrusted corpus text."""
    rendered = ascii(value)
    return rendered if len(rendered) <= limit else rendered[: limit - 3] + "..."


def frontmatter_name(card: Path) -> tuple[bool, str | None]:
    """(skill_md_exists, live name or None).

    A card with no SKILL.md is validate_card_files.py's finding, not this
    script's, so that shape is skipped rather than reported twice in
    different words. A SKILL.md that exists but states no frontmatter name is
    NOBODY else's finding -- validate_card_files.py checks file presence and
    evidence rows only -- so the caller reports it here rather than skipping:
    a rename that drops or mangles the name line is exactly the drift the
    skill_name assertion exists to catch (cross-review reproduced the silent
    pass).
    """
    skill_md = card / "SKILL.md"
    if not skill_md.is_file():
        return (False, None)
    block = FRONTMATTER_NAME_RE.match(skill_md.read_text(encoding="utf-8", errors="replace"))
    if block is None:
        return (True, None)
    found = NAME_LINE_RE.search(block.group(1))
    return (True, found.group(1) if found else None)


def case_breaches(index: int, case: Any, seen_ids: dict[Any, int], seen_prompts: dict[str, int]) -> list[str]:
    """Contract breaches in one case, in report order.

    `index` is the case's position in the file, one-based, so a report can name
    a case whose `id` is the very thing that is wrong.
    """
    where = f"case {index}"
    if not isinstance(case, dict):
        return [f"{where} is not an object: {quote(case)}"]

    breaches: list[str] = []

    unknown = sorted(set(case) - CASE_KEYS)
    if unknown:
        breaches.append(
            f"{where} states unknown key(s) {', '.join(map(quote, unknown))}. "
            "The case vocabulary is closed, so a contract case cannot carry "
            "a verdict, score or result"
        )

    identifier = case.get("id")
    # bool is an int in Python and would silently make True and 1 the same id.
    if not isinstance(identifier, int) or isinstance(identifier, bool):
        breaches.append(f"{where} states no integer id: {quote(identifier)}")
    elif identifier in seen_ids:
        breaches.append(
            f"{where} reuses case id {identifier}, already taken by case "
            f"{seen_ids[identifier]}. An id a runner cannot resolve to one case "
            "cannot carry a result back to it"
        )
    else:
        seen_ids[identifier] = index

    prompt = case.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        breaches.append(f"{where} states an empty prompt: {quote(prompt)}")
    elif len(prompt.strip()) < MIN_PROMPT_CHARS:
        breaches.append(
            f"{where} states a prompt of {len(prompt.strip())} characters, under "
            f"the {MIN_PROMPT_CHARS} minimum: {quote(prompt)}. A runner cannot "
            "reproduce a situation from a label"
        )
    else:
        normalised = " ".join(prompt.split()).casefold()
        if normalised in seen_prompts:
            breaches.append(
                f"{where} reuses a prompt already stated by case "
                f"{seen_prompts[normalised]}. Two cases that ask the same thing "
                "measure one thing twice"
            )
        else:
            seen_prompts[normalised] = index

    expected = case.get("expected_output")
    if not isinstance(expected, str) or not expected.strip():
        breaches.append(
            f"{where} states an empty expected_output: {quote(expected)}. A case "
            "with nothing expected of it cannot fail"
        )

    assertions = case.get("assertions")
    if not isinstance(assertions, list):
        breaches.append(f"{where} states no assertions list: {quote(assertions)}")
    elif len(assertions) < MIN_ASSERTIONS:
        breaches.append(
            f"{where} states {len(assertions)} assertion(s), fewer than the "
            f"{MIN_ASSERTIONS} required. One assertion cannot separate a "
            "response that is right from one that is merely not wrong"
        )
    else:
        breaches += [
            f"{where} states an empty assertion at position {position}: "
            f"{quote(item)}"
            for position, item in enumerate(assertions, start=1)
            if not isinstance(item, str) or not item.strip()
        ]
    return breaches


def corpus_breaches(card: Path) -> list[str]:
    """Contract breaches in one card's corpus, in report order."""
    folder = card / CORPUS_DIR
    corpus = folder / CORPUS_FILE
    if not corpus.is_file():
        return [f"states no {CORPUS_PATH}"]

    # "Exactly one corpus" is enforced, not assumed. A second file beside the
    # corpus is the shape that makes the per-card count and the repository
    # count two different numbers.
    strays = sorted(
        p.relative_to(card).as_posix()
        for p in folder.rglob("*")
        if p.is_file() and p != corpus
    )
    breaches = (
        [
            f"carries {len(strays)} file(s) beside the corpus in {CORPUS_DIR}/: "
            + ", ".join(strays)
            + ". Exactly one corpus per card, so the count of corpora and the "
            "count of cards stay one number"
        ]
        if strays
        else []
    )

    try:
        data = json.loads(corpus.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return breaches + [f"{CORPUS_PATH} is not valid JSON: {error}"]

    if not isinstance(data, dict):
        return breaches + [f"{CORPUS_PATH} is not a JSON object: {quote(data)}"]

    unknown = sorted(set(data) - TOP_LEVEL_KEYS)
    if unknown:
        breaches.append(
            f"{CORPUS_PATH} states unknown key(s) {', '.join(map(quote, unknown))}. "
            "The corpus vocabulary is closed, so a contract cannot grow "
            "measurement-shaped keys or silently typo an optional one"
        )

    declared = data.get("skill_name")
    has_skill_md, live = frontmatter_name(card)
    if not isinstance(declared, str) or not declared.strip():
        breaches.append(f"{CORPUS_PATH} states no skill_name: {quote(declared)}")
    elif has_skill_md and live is None:
        breaches.append(
            "SKILL.md states no frontmatter name, so the corpus's skill_name "
            f"{quote(declared)} cannot be checked against the card. A name "
            "assertion that silently skips is a drift check that cannot fire"
        )
    elif live is not None and declared != live:
        breaches.append(
            f"{CORPUS_PATH} states skill_name {quote(declared)} but the card's "
            f"SKILL.md frontmatter name is {quote(live)}. A corpus that names a "
            "card the tree does not have is a contract against nothing"
        )

    cases = data.get("cases")
    if not isinstance(cases, list):
        return breaches + [f"{CORPUS_PATH} states no cases list: {quote(cases)}"]
    if len(cases) < MIN_CASES:
        breaches.append(
            f"{CORPUS_PATH} states {len(cases)} case(s), fewer than the "
            f"{MIN_CASES} required"
        )

    seen_ids: dict[Any, int] = {}
    seen_prompts: dict[str, int] = {}
    for position, case in enumerate(cases, start=1):
        breaches += case_breaches(position, case, seen_ids, seen_prompts)
    return breaches


def validate(root: Path) -> None:
    cards = card_files.find_cards(root)
    if not cards:
        print(
            f"REJECTED: no published cards found under {root}/skills. A run "
            "that checked nothing is not a pass.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    breaches = [
        f"  - {card.relative_to(root).as_posix()}: {detail}"
        for card in cards
        for detail in corpus_breaches(card)
    ]
    if breaches:
        for line in breaches:
            print(line, file=sys.stderr)
        print(
            f"REJECTED: {len(breaches)} eval corpus breach(es) across "
            f"{len(cards)} published card(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    corpora = sum(1 for card in cards if (card / CORPUS_DIR / CORPUS_FILE).is_file())
    cases = sum(
        len(json.loads((card / CORPUS_DIR / CORPUS_FILE).read_text(encoding="utf-8"))["cases"])
        for card in cards
    )
    print(
        f"PASS: {corpora} eval corpus/corpora for {len(cards)} published "
        f"card(s), {cases} case(s) total; every corpus names its card and "
        f"states at least {MIN_CASES} cases with {MIN_ASSERTIONS} assertions "
        "each. Corpora are structural contracts, not measurements."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the published eval corpora.")
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to validate (default: this repository)",
    )
    args = parser.parse_args()
    validate(args.root.resolve())


if __name__ == "__main__":
    main()
