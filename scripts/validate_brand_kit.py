#!/usr/bin/env python3
"""Make assets/tokens.json enforceable: banned copy, hash pairs, declared hexes.

The token file described the brand and nothing read it. It said so itself, in a
`known_gaps` block that stayed an accurate description of the repository for
twelve days: the kit declared structural neutrals for dark surfaces only, both
banners carried the sibling instrument's confirmed-success green, and no check
anywhere opened the file. This script is what closes `known_gaps.not_enforced`.

THE THREE CHECKS
    1. BANNED COPY. Every surface named in `copy.words_to_avoid_surfaces` is
       read and refused if it contains a word from `copy.words_to_avoid`. The
       word list and the surface list are both DATA: adding a word is a
       one-line edit to the token file and never a change here.

    2. HASH PAIRS. Files that must change together, named in `asset_pairs`.
       Each pair records the sha256 of both halves; either half drifting from
       its recorded hash is refused. This is what stops a copy check from being
       defeated by editing a text-bearing source and shipping a stale export.

    3. DECLARED HEXES. Every colour appearing in `assets/*.svg` is declared
       as a token VALUE under `color`. Prose that merely NAMES a hex declares
       nothing - see `declared_hexes`. This is the check the ticket ordered LAST,
       and the order was a constraint rather than a preference: it would have
       failed on both banners until the two colour gaps closed, so landing it
       earlier meant landing a permanently red check that would be disabled.

WHY THE SCOPE RULE IS DATA AND WHY README BODY PROSE IS OUT OF IT
    `copy.words_to_avoid_scope` states the rule for a human;
    `copy.words_to_avoid_surfaces` states the same rule for this script. The
    scope is public asset copy - rendered graphics, front-page HEADINGS, the
    repository description. Body prose, code comments and working documentation
    are outside it, and several banned words appear there on purpose: this
    repository's own AGENTS.md, SECURITY.md and skill cards use `load-bearing`
    in exactly the sense the word is good for. A check that caught those would
    be wrong, and widening the scope is a decision rather than a maintenance
    task.

WHY SVG COPY IS PARSED AND NOT PATTERN-MATCHED
    Ported from the sibling instrument's scanner (skill-harness,
    tests/test_structural_bans.py::_svg_text), which parses with ElementTree and
    collects `aria-label` attributes together with the text content of `text`,
    `title` and `desc` elements. A regex over `<text>` alone is blind to
    `aria-label` - an accessible label is public copy a screen reader speaks,
    and both banners carry their whole statement in one. `itertext()` also
    reassembles copy split across `tspan` children, which a regex over element
    bodies reads as two unrelated fragments.

    The ban list is NOT ported. The sibling hardcodes its words; here they are
    data, which is the better half of the two designs.

WHY HEX SCANNING GOES THROUGH THE PARSER TOO
    ElementTree discards XML comments, so a hex written in a comment is not
    scanned - which is correct, because a comment renders nothing. Both banners
    now NAME the instrument green in a comment explaining why it was removed. A
    regex over the raw file would refuse them for the note recording the fix.

NON-VACUITY IS CHECKED AT RUNTIME, NOT ONLY IN THE SUITE
    Two of these three checks guard things that are ABSENT on a healthy
    repository - no banned word, no hash mismatch - which is exactly the
    condition under which a check that has gone blind is indistinguishable from
    one that is working. So this script refuses its own inputs when they could
    make it vacuous: an empty word list, a surface glob matching no file, an SVG
    scan that returns no copy at all, an asset scan that finds no colour, or an
    `asset_pairs` block recording neither a pair nor a stated reason for having
    none.

Output is ASCII-only so the Windows CI cell cannot die on cp1252 while printing
a status line, matching validate_scoreboard.py and validate_eval_corpora.py.
Surface text is quoted through ascii() for the same reason: both banner
aria-labels contain an em dash.

`main` has no branch protection and no required checks, so a nonzero exit here
is a signal, not a gate. Describe it as detecting violations, never as
preventing them.

Usage:
    python scripts/validate_brand_kit.py
    python scripts/validate_brand_kit.py --root <tree>
    python scripts/validate_brand_kit.py --record-hashes
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Final

SCRIPT_DIR = Path(__file__).resolve().parent

TOKENS_PATH: Final[str] = "assets/tokens.json"
SVG_GLOB: Final[str] = "assets/*.svg"
COPY_ELEMENTS: Final[frozenset[str]] = frozenset({"text", "title", "desc"})
HEX_RE: Final[re.Pattern[str]] = re.compile(r"#[0-9a-fA-F]{3,8}\b")
HEADING_RE: Final[re.Pattern[str]] = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
KNOWN_KINDS: Final[frozenset[str]] = frozenset(
    {"svg_copy", "markdown_headings", "json_string_field"}
)


class Refusal(Exception):
    """An input problem that makes the run itself untrustworthy."""


def load_tokens(root: Path) -> dict[str, Any]:
    path = root / TOKENS_PATH
    if not path.is_file():
        raise Refusal(f"no token file at {TOKENS_PATH} under {root}")
    try:
        tokens = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise Refusal(f"{TOKENS_PATH} is not valid JSON: {error}") from error
    if not isinstance(tokens, dict):
        raise Refusal(f"{TOKENS_PATH} is not a JSON object")
    return tokens


# --------------------------------------------------------------------------
# SVG copy, ported from the sibling instrument's scanner.
# --------------------------------------------------------------------------
def svg_copy(svg: str) -> str:
    """aria-label attributes plus the text of text/title/desc elements."""
    root = ET.fromstring(svg)
    public_copy: list[str] = []
    for element in root.iter():
        aria_label = element.get("aria-label")
        if aria_label:
            public_copy.append(aria_label)
        if element.tag.rsplit("}", 1)[-1] in COPY_ELEMENTS:
            public_copy.append("".join(element.itertext()))
    return "\n".join(public_copy)


def svg_hexes(svg: str) -> list[str]:
    """Every colour in a parsed SVG. Comments are discarded by the parser."""
    root = ET.fromstring(svg)
    found: list[str] = []
    for element in root.iter():
        for value in element.attrib.values():
            found.extend(HEX_RE.findall(value))
        for chunk in (element.text, element.tail):
            if chunk:
                found.extend(HEX_RE.findall(chunk))
    return found


def normalise_hex(value: str) -> str:
    digits = value[1:].lower()
    if len(digits) == 3:
        digits = "".join(digit * 2 for digit in digits)
    return "#" + digits


# --------------------------------------------------------------------------
# Surfaces.
# --------------------------------------------------------------------------
def surface_copy(root: Path, spec: dict[str, Any]) -> list[tuple[str, str]]:
    """(label, copy) for every file a surface spec resolves to."""
    kind = spec.get("kind")
    glob = spec.get("glob")
    if kind not in KNOWN_KINDS:
        raise Refusal(
            f"surface kind {ascii(kind)} is not one of "
            f"{sorted(KNOWN_KINDS)}. A surface this script cannot read is a "
            "surface nothing checks."
        )
    if not isinstance(glob, str) or not glob:
        raise Refusal(f"surface of kind {kind} states no glob")

    paths = sorted(root.glob(glob))
    if not paths:
        raise Refusal(
            f"surface glob {ascii(glob)} matched no file under {root}. A "
            "surface that resolves to nothing is a check that runs on nothing."
        )

    collected: list[tuple[str, str]] = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if kind == "svg_copy":
            collected.append((f"{relative}:svg-copy", svg_copy(text)))
        elif kind == "markdown_headings":
            collected.append((f"{relative}:headings", "\n".join(HEADING_RE.findall(text))))
        else:
            field = spec.get("field")
            if not isinstance(field, str) or not field:
                raise Refusal(f"json_string_field surface {ascii(glob)} names no field")
            value = json.loads(text).get(field)
            if not isinstance(value, str):
                raise Refusal(
                    f"{relative} has no string field {ascii(field)}. The surface "
                    "was named on purpose, so its absence is a breach and not a skip."
                )
            collected.append((f"{relative}:{field}", value))
    return collected


def banned_word_violations(surfaces: list[tuple[str, str]], words: list[str]) -> list[str]:
    violations: list[str] = []
    for label, text in surfaces:
        lines = text.splitlines()
        for word in words:
            pattern = re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])", re.IGNORECASE)
            match = pattern.search(text)
            if not match:
                continue
            line = text.count("\n", 0, match.start()) + 1
            context = lines[line - 1] if 0 < line <= len(lines) else ""
            violations.append(
                f"{label}: banned word {ascii(word)} at line {line} of the "
                f"scanned copy: {ascii(context.strip()[:120])}. It is listed in "
                "assets/tokens.json > copy.words_to_avoid, and this surface is in "
                "copy.words_to_avoid_surfaces."
            )
    return violations


# --------------------------------------------------------------------------
# Hash pairs.
# --------------------------------------------------------------------------
def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair_violations(root: Path, pairs: list[Any]) -> list[str]:
    violations: list[str] = []
    for position, pair in enumerate(pairs, start=1):
        if not isinstance(pair, dict):
            violations.append(f"asset_pairs[{position}] is not an object")
            continue
        for half in ("source", "export"):
            name = pair.get(half)
            recorded = pair.get(f"{half}_sha256")
            if not isinstance(name, str) or not name:
                violations.append(f"asset_pairs[{position}] names no {half}")
                continue
            if not isinstance(recorded, str) or not recorded:
                violations.append(
                    f"asset_pairs[{position}] {half} {ascii(name)} records no "
                    f"{half}_sha256. An unrecorded half cannot drift visibly."
                )
                continue
            path = root / name
            if not path.is_file():
                violations.append(
                    f"asset_pairs[{position}] {half} {ascii(name)} does not exist "
                    "under the tree being checked."
                )
                continue
            actual = sha256_of(path)
            if actual != recorded:
                violations.append(
                    f"{name}: recorded hash disagrees with the file on disk. "
                    f"assets/tokens.json records {recorded[:16]}..., the file is "
                    f"{actual[:16]}.... One half of a pair was changed without the "
                    "other, or without re-recording both."
                )
    return violations


# --------------------------------------------------------------------------
# Declared hexes.
# --------------------------------------------------------------------------
def declared_hexes(node: Any, into: set[str]) -> set[str]:
    """Colours declared as token VALUES. Prose naming a hex declares nothing.

    Scanning every string in the file was the first version of this, and the
    poison control refused it: `color.usage_rules` names #3FB950 inside the
    sentence saying that colour belongs to the sibling instrument and must not
    be used here. A whole-file scan reads that sentence as a declaration, so
    planting the instrument green back into a banner PASSED - the ban was its
    own permission. Only a `value` field on a token object declares a colour.
    """
    if isinstance(node, dict):
        value = node.get("value")
        if isinstance(value, str):
            for found in HEX_RE.findall(value):
                into.add(normalise_hex(found))
        for child in node.values():
            declared_hexes(child, into)
    elif isinstance(node, list):
        for child in node:
            declared_hexes(child, into)
    return into


def undeclared_hex_violations(root: Path, declared: set[str]) -> tuple[list[str], int, int]:
    violations: list[str] = []
    seen: set[str] = set()
    files = sorted(root.glob(SVG_GLOB))
    for path in files:
        relative = path.relative_to(root).as_posix()
        for raw in svg_hexes(path.read_text(encoding="utf-8")):
            colour = normalise_hex(raw)
            seen.add(colour)
            if colour not in declared:
                violations.append(
                    f"{relative}: undeclared hex {colour}. Every colour an asset "
                    "ships must be declared in assets/tokens.json. Declare it, or "
                    "change the asset to a colour that is."
                )
    return sorted(set(violations)), len(seen), len(files)


# --------------------------------------------------------------------------
# Entrypoint.
# --------------------------------------------------------------------------
def validate(root: Path) -> None:
    tokens = load_tokens(root)

    copy_block = tokens.get("copy")
    if not isinstance(copy_block, dict):
        raise Refusal("assets/tokens.json states no copy block")
    words = copy_block.get("words_to_avoid")
    if not isinstance(words, list) or not words or not all(isinstance(w, str) for w in words):
        raise Refusal(
            "copy.words_to_avoid is empty or not a list of strings. An empty ban "
            "list makes the copy check pass on every possible input."
        )
    surface_block = copy_block.get("words_to_avoid_surfaces")
    if not isinstance(surface_block, dict):
        raise Refusal("copy.words_to_avoid_surfaces is missing")
    specs = surface_block.get("surfaces")
    if not isinstance(specs, list) or not specs:
        raise Refusal(
            "copy.words_to_avoid_surfaces.surfaces is empty. A ban list with no "
            "surface to read is a check over nothing."
        )

    surfaces: list[tuple[str, str]] = []
    svg_copy_seen = 0
    for spec in specs:
        if not isinstance(spec, dict):
            raise Refusal("a surface entry is not an object")
        resolved = surface_copy(root, spec)
        if spec.get("kind") == "svg_copy":
            svg_copy_seen += sum(len(text.strip()) for _, text in resolved)
        surfaces.extend(resolved)

    if svg_copy_seen == 0:
        raise Refusal(
            "the SVG scanner saw no copy in any asset. Either no asset carries "
            "an aria-label or a text/title/desc element, or the scanner has gone "
            "blind - and a blind scanner passes everything."
        )

    violations = banned_word_violations(surfaces, words)

    pair_block = tokens.get("asset_pairs")
    if not isinstance(pair_block, dict):
        raise Refusal("assets/tokens.json states no asset_pairs block")
    pairs = pair_block.get("pairs")
    if not isinstance(pairs, list):
        raise Refusal("asset_pairs.pairs is not a list")
    pending = pair_block.get("pairs_pending")
    if not pairs and not (isinstance(pending, str) and pending.strip()):
        raise Refusal(
            "asset_pairs records no pair and states no reason for having none. "
            "A freshness check over zero pairs is vacuous, so the emptiness has "
            "to be declared rather than inferred."
        )
    violations.extend(pair_violations(root, pairs))

    declared = declared_hexes(tokens.get("color"), set())
    if not declared:
        raise Refusal("assets/tokens.json declares no colour at all")
    hex_violations, distinct_hexes, svg_files = undeclared_hex_violations(root, declared)
    if svg_files == 0:
        raise Refusal(f"no SVG asset found under {root}/assets")
    if distinct_hexes == 0:
        raise Refusal(
            "no colour was found in any SVG asset. Either every asset inherits "
            "currentColor, or the hex scanner has gone blind."
        )
    violations.extend(hex_violations)

    if violations:
        for line in violations:
            print(f"  - {line}", file=sys.stderr)
        print(
            f"REJECTED: {len(violations)} brand kit breach(es) across "
            f"{len(surfaces)} public copy surface(s) and {svg_files} SVG asset(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    version = tokens.get("version", "unversioned")
    print(
        f"PASS: brand kit {version} enforced - {len(surfaces)} public copy "
        f"surface(s) scanned against {len(words)} banned word(s), "
        f"{len(pairs)} asset pair(s) hash-verified, {distinct_hexes} distinct "
        f"hex(es) across {svg_files} SVG asset(s) all declared in the kit. "
        "This detects breaches; it does not prevent them."
    )


def record_hashes(root: Path) -> None:
    path = root / TOKENS_PATH
    tokens = load_tokens(root)
    pairs = tokens.get("asset_pairs", {}).get("pairs", [])
    if not pairs:
        print("nothing to record: asset_pairs.pairs is empty")
        return
    for pair in pairs:
        for half in ("source", "export"):
            name = pair.get(half)
            if isinstance(name, str) and (root / name).is_file():
                digest = sha256_of(root / name)
                pair[f"{half}_sha256"] = digest
                print(f"recorded {half} {name} = {digest[:16]}...")
    path.write_text(json.dumps(tokens, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the brand kit against what ships.")
    parser.add_argument(
        "--root",
        type=Path,
        default=SCRIPT_DIR.parent,
        help="tree to validate (default: this repository)",
    )
    parser.add_argument(
        "--record-hashes",
        action="store_true",
        help="rewrite every recorded pair hash from the files on disk",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.record_hashes:
            record_hashes(root)
            return
        validate(root)
    except Refusal as refusal:
        print(f"REJECTED: {refusal}", file=sys.stderr)
        raise SystemExit(1) from refusal
    except ET.ParseError as error:
        print(f"REJECTED: an SVG asset does not parse: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
