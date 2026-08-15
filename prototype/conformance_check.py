#!/usr/bin/env python3
"""THROWAWAY conformance prototype. Not the implementation. Do not package.

Question it exists to answer: are the obligations this collection has ALREADY
STATED expressible as checks over the tree, and can such a check reject a tree
that is actually in breach?

It invents no obligations. Every check below quotes the sentence it encodes from
SECURITY.md / README.md as they stand in the tree being checked. Where a stated
obligation cannot be turned into a predicate, the check reports CANNOT-CHECK
rather than a green -- that outcome is the point of the experiment, not a gap in
it.

Format vocabulary (commitment 3) is NOT re-implemented here: scripts/
validate_skill_formats.py already ships that predicate, and this prototype
shells out to it rather than around it.

ASCII only. Run with PYTHONUTF8=1.

Usage:
    python prototype/conformance_check.py --root <tree>
    python prototype/conformance_check.py --root <tree> --markdown
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PASS = "PASS"
FAIL = "FAIL"
CANT = "CANNOT-CHECK"

# The few-minutes bar in commitment 1 has no stated number. 1500 words is this
# prototype's own proxy, so a result from it is reported as a proxy, never as
# conformance with the published sentence.
READABLE_WORD_PROXY = 1500


@dataclass
class Result:
    verdict: str
    detail: str


@dataclass
class Card:
    name: str
    folder: Path


def find_cards(root: Path) -> list[Card]:
    """Published cards only: a SKILL.md under skills/, fixtures excluded."""
    out = []
    base = root / "skills"
    for skill_md in sorted(base.glob("*/*/SKILL.md")):
        out.append(Card(skill_md.parent.name, skill_md.parent))
    return out


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# ---------------------------------------------------------------- obligations


def claim_plaintext_only(security_text: str) -> bool:
    """True when the tree still makes the pre-#76 blanket plain-text claim.

    The claim being encoded is literal: "A skill is a plain-text markdown file."
    If a tree says that, every file in every skill folder must be markdown or
    text. If the tree carries the ruled post-#76 wording instead ("Everything
    this repository ships inside a skill folder is source you can read"), the
    obligation is the format vocabulary, which commitment 3 owns.
    """
    return "plain-text markdown file" in security_text


def check_plaintext(card: Card, security_text: str) -> Result:
    if not claim_plaintext_only(security_text):
        return Result(
            PASS,
            "tree carries the ruled readable-source wording; format vocabulary "
            "is checked by commitment 3",
        )
    bad = [
        p.relative_to(card.folder).as_posix()
        for p in sorted(card.folder.rglob("*"))
        if p.is_file() and p.suffix not in (".md", ".txt")
    ]
    if bad:
        return Result(
            FAIL,
            "SECURITY.md says a skill IS a plain-text markdown file; this card "
            "ships " + ", ".join(bad),
        )
    return Result(PASS, "every file is .md or .txt")


def check_readable_proxy(card: Card) -> Result:
    words = len(read(card.folder / "SKILL.md").split())
    verdict = PASS if words <= READABLE_WORD_PROXY else FAIL
    return Result(verdict, f"SKILL.md is {words} words (proxy bar {READABLE_WORD_PROXY})")


FETCH_EXEC = [
    re.compile(r"curl[^\n|]*\|\s*(ba)?sh", re.I),
    re.compile(r"wget[^\n|]*\|\s*(ba)?sh", re.I),
    re.compile(r"iwr[^\n|]*\|\s*iex", re.I),
    re.compile(r"eval\s*\(\s*(requests|urllib|fetch)", re.I),
    re.compile(r"pip\s+install\s+(https?|git\+)", re.I),
]


def check_fetch_execute(card: Card) -> Result:
    hits = []
    for path in sorted(card.folder.rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".txt", ".py"):
            continue
        text = read(path)
        for pattern in FETCH_EXEC:
            for match in pattern.finditer(text):
                hits.append(f"{path.name}: {match.group(0)[:60]}")
    if hits:
        return Result(FAIL, "; ".join(hits))
    return Result(PASS, "no download-and-run pattern in any shipped file")


SECRET_WORDS = re.compile(
    r"\b(api[_ -]?key|access[_ -]?token|credential|password|secret|\.env)\b", re.I
)


def check_secrets(card: Card) -> Result:
    """Commitment 4 forbids INSTRUCTING the agent to read/move/transmit secrets.

    A textual scan cannot separate that from a card that merely mentions the
    word. So this reports mentions and the verdict is CANNOT-CHECK either way:
    a clean scan is real evidence of nothing, and a hit is not a breach. The
    mention count is carried so the false-positive cost is measurable.
    """
    hits = []
    for path in sorted(card.folder.rglob("*.md")):
        for match in SECRET_WORDS.finditer(read(path)):
            hits.append(f"{path.name}:{match.group(0)}")
    if hits:
        return Result(CANT, f"{len(hits)} mention(s), semantics undecidable: " + hits[0])
    return Result(CANT, "no mention; absence of the word is not compliance")


DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


def check_evidence(card: Card) -> Result:
    """Commitment 6: skills with a real-incident origin carry a dated EVIDENCE.md.

    The antecedent ("has a real-incident origin") is not machine-decidable, so
    absence can never be scored. Presence plus a parseable date can be, and is.
    """
    path = card.folder / "EVIDENCE.md"
    if not path.exists():
        return Result(CANT, "no EVIDENCE.md; the origin condition is not decidable here")
    text = read(path)
    dates = DATE.findall(text)
    if not dates:
        return Result(FAIL, "EVIDENCE.md present but carries no ISO date")
    return Result(PASS, f"EVIDENCE.md dated {dates[0]}")


def check_scripts_named(card: Card, security_text: str) -> Result:
    """Commitment 3: "A skill's own SKILL.md names the scripts it asks the agent
    to run", with an explicit carve-out for the im-down / im-up test suites.

    The carve-out is read out of SECURITY.md rather than hardcoded, so a tree
    that drops the sentence loses the exemption.
    """
    scripts = sorted(p for p in card.folder.rglob("*.py") if "__pycache__" not in p.parts)
    if not scripts:
        return Result(PASS, "ships no script")
    if "names the scripts it asks the agent to run" not in security_text:
        return Result(
            FAIL,
            "tree states no naming obligation yet ships "
            + ", ".join(p.name for p in scripts),
        )
    exempt = "also ship their test suites" in security_text and card.name in security_text
    skill_md = read(card.folder / "SKILL.md")
    unnamed = [p.name for p in scripts if p.name not in skill_md]
    if not unnamed:
        return Result(PASS, f"all {len(scripts)} script(s) named in SKILL.md")
    still = [n for n in unnamed if not (exempt and n.startswith("test_"))]
    if still:
        return Result(FAIL, "not named in SKILL.md: " + ", ".join(still))
    return Result(
        PASS,
        "named: " + str(len(scripts) - len(unnamed)) + "; test suite(s) covered by the "
        "SECURITY.md carve-out: " + ", ".join(unnamed),
    )


def check_explicit_updates(card: Card) -> Result:
    """Commitment 5 is a property of the distribution channel, not of a card.

    Nothing in the tree can witness "nothing self-updates" -- the tree is what
    would be updated. Recorded as CANNOT-CHECK by construction, not by effort.
    """
    return Result(CANT, "property of the installer/channel; no per-card witness exists")


# ------------------------------------------------------------- repo-wide check


def run_format_walker(root: Path) -> Result:
    """Delegate commitment 3's format vocabulary to the predicate already shipped."""
    script = root / "scripts" / "validate_skill_formats.py"
    if not script.exists():
        return Result(CANT, "scripts/validate_skill_formats.py absent from this tree")
    proc = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    output = (proc.stdout + proc.stderr).strip().splitlines()
    tail = output[-1] if output else "(no output)"
    return Result(PASS if proc.returncode == 0 else FAIL, tail)


OBLIGATIONS = [
    ("plain-text/readable-source scope", "SECURITY.md opening claim (#51/#76)"),
    ("readable in a few minutes (PROXY)", "commitment 1"),
    ("no fetch-and-execute", "commitment 2"),
    ("shipped scripts named in SKILL.md", "commitment 3"),
    ("no secrets handling", "commitment 4"),
    ("explicit updates only", "commitment 5"),
    ("dated EVIDENCE.md", "commitment 6 / provenance"),
]


def evaluate(root: Path) -> tuple[list[Card], dict, Result]:
    # Whitespace-normalized: the published sentences are hard-wrapped, so a raw
    # substring match against the file misses them and every scripted card goes
    # red on a tree that states the obligation perfectly well. That was this
    # prototype's first false positive and it is worth leaving the note.
    security_text = " ".join(read(root / "SECURITY.md").split())
    cards = find_cards(root)
    table = {}
    for card in cards:
        table[card.name] = [
            check_plaintext(card, security_text),
            check_readable_proxy(card),
            check_fetch_execute(card),
            check_scripts_named(card, security_text),
            check_secrets(card),
            check_explicit_updates(card),
            check_evidence(card),
        ]
    return cards, table, run_format_walker(root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    cards, table, walker = evaluate(root)

    if not cards:
        print("REJECTED: no published cards found under skills/", file=sys.stderr)
        raise SystemExit(2)

    names = [o[0] for o in OBLIGATIONS]
    if args.markdown:
        print("| Card | " + " | ".join(names) + " |")
        print("|" + "---|" * (len(names) + 1))
        for card in cards:
            print(
                "| `"
                + card.name
                + "` | "
                + " | ".join(r.verdict for r in table[card.name])
                + " |"
            )
    else:
        for card in cards:
            print(card.name)
            for (label, source), result in zip(OBLIGATIONS, table[card.name]):
                print(f"  {result.verdict:<12} {label} [{source}] -- {result.detail}")
            print()

    counts = {PASS: 0, FAIL: 0, CANT: 0}
    for card in cards:
        for result in table[card.name]:
            counts[result.verdict] += 1
    total = sum(counts.values())
    print(
        f"\n{len(cards)} card(s) x {len(OBLIGATIONS)} obligation(s) = {total} cells: "
        f"{counts[PASS]} PASS, {counts[FAIL]} FAIL, {counts[CANT]} CANNOT-CHECK"
    )
    print(f"repo-wide format vocabulary (commitment 3): {walker.verdict} -- {walker.detail}")
    raise SystemExit(1 if counts[FAIL] or walker.verdict == FAIL else 0)


if __name__ == "__main__":
    main()
