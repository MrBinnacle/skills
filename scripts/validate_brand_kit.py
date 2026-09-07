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

    3. DECLARED HEXES. Every colour appearing on a surface named in
       `color.declared_hex_surfaces` is declared as a token VALUE under
       `color`. Those surfaces are DATA for the same reason the copy surfaces
       are: until #256 the glob was hard-coded to `assets/*.svg`, so the
       landing page stylesheet drew every value from this file with nothing
       verifying it, and widening the check was an edit here rather than a
       recorded decision. Prose that merely NAMES a hex declares
       nothing - see `declared_hexes`. This is the check the ticket ordered LAST,
       and the order was a constraint rather than a preference: it would have
       failed on both banners until the two colour gaps closed, so landing it
       earlier meant landing a permanently red check that would be disabled.

WHY THE SCOPE RULE IS DATA, AND WHAT THE SCOPE NOW IS
    `copy.words_to_avoid_scope` states the rule for a human;
    `copy.words_to_avoid_surfaces` states the same rule for this script.

    The scope was public asset copy only - rendered graphics, front-page
    HEADINGS, the repository description - and this docstring argued that body
    prose belonged outside it because the repository used `load-bearing` in
    working documentation on purpose. The operator ruling of 2026-09-06 ended
    that split: one word list, all repositories, every single line of prose, the
    same rules. The `markdown_prose` surface carries it, and the rewrite it
    forced replaced 21 uses of `load-bearing` with the thing each sentence
    actually named - the check, the rule, the dependency, the constraint.

    Two exclusions survive the ruling, both declared in the token file rather
    than here: `_quarantine/**`, whose candidates are frozen and must not be
    rewritten, and `CHANGELOG.md`, whose entries record what shipped under the
    wording in force at the time. Adding a further surface is still a decision
    rather than a maintenance task.

WHY THE PROSE SURFACE OVERLAPS THE HEADINGS SURFACE, AND WHY BOTH STAY
    `markdown_prose` reads whole documents, so a README heading is inside both
    it and `markdown_headings`, and a banned word there is reported twice. The
    narrower surface is kept anyway: `.vale.ini` binds the fast Vale feedback to
    the glob `README.md`, and `validate_vale_style.py` refuses a Vale binding to
    any glob the token file does not declare. Dropping the README surface would
    make the Vale binding a widening and redden that check.

WHY THE PUBLISHED DIGEST IS OVER THE LIST AND NOT OVER THE FILE
    `copy.words_to_avoid_digest.sha256` is sha256 over
    `json.dumps(words_to_avoid, separators=(",",":")).encode()`, and this script
    recomputes it on every run. MrBinnacle/skill-harness#462 vendors the list and
    compares its copy against that value. A digest over the whole token file
    would change on every unrelated edit - a colour value, a recorded pair hash,
    a note - so the sibling would see drift it could not act on, and a contract
    that cries wolf gets muted. Rewrite it with --record-digest.

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

    CSS has one comment form and no parser here, so `css_hexes` removes
    `/* ... */` before scanning. That buys the stylesheet the same exemption
    for the same reason: a hex inside a comment paints nothing.

NON-VACUITY IS CHECKED AT RUNTIME, NOT ONLY IN THE SUITE
    Two of these three checks guard things that are ABSENT on a healthy
    repository - no banned word, no hash mismatch - which is exactly the
    condition under which a check that has gone blind is indistinguishable from
    one that is working. So this script refuses its own inputs when they could
    make it vacuous: an empty word list, a surface glob matching no file, an SVG
    scan that returns no copy at all, a declared-hex surface list that is empty
    or names a kind nothing reads, a hex scan that finds no colour, or an
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
    python scripts/validate_brand_kit.py --record-digest
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Final

SCRIPT_DIR = Path(__file__).resolve().parent

TOKENS_PATH: Final[str] = "assets/tokens.json"
COPY_ELEMENTS: Final[frozenset[str]] = frozenset({"text", "title", "desc"})
HEX_RE: Final[re.Pattern[str]] = re.compile(r"#[0-9a-fA-F]{3,8}\b")
CSS_COMMENT_RE: Final[re.Pattern[str]] = re.compile(r"/\*.*?\*/", re.DOTALL)
HEADING_RE: Final[re.Pattern[str]] = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
# Setext headings underline their text with = or - on the next line. They are
# part of the headings surface too: the repo writes ATX throughout, but a
# banned word in an H1 written setext-style would otherwise pass the very
# surface the token file claims is covered (cross-review reproduced it). A
# table separator row cannot match: its underline carries pipes.
SETEXT_RE: Final[re.Pattern[str]] = re.compile(
    r"^(\S[^\n]*)\n(?:=+|-+)[ \t]*$", re.MULTILINE
)
# The sha256 field inside the words_to_avoid_digest object and nothing else:
# asset_pairs records sha256 values too, and a looser pattern would rewrite the
# first of those instead.
DIGEST_FIELD_RE: Final[re.Pattern[str]] = re.compile(
    r'("words_to_avoid_digest"[\s\S]*?"sha256":\s*)"[0-9a-f]*"'
)
KNOWN_KINDS: Final[frozenset[str]] = frozenset(
    {"svg_copy", "markdown_headings", "markdown_prose", "json_string_field"}
)


class Refusal(Exception):
    """An input problem that makes the run itself untrustworthy."""


# --------------------------------------------------------------------------
# File selection (#267).
#
# Every surface declares a glob in the token file, and until #267 the glob was
# resolved against the FILESYSTEM. So the scanned set was whatever a working
# clone happened to hold: a scratch note, a draft, an agent hand-off file, a
# local CLAUDE.md, a vendored `node_modules/`, a sandbox worktree. Measured on
# the live tree the day this landed: 54 breaches, none of them in a tracked
# file - 48 under `.sandcastle/worktrees/`, 6 under `node_modules/`. The same
# run was green in CI, which clones only tracked content, so the local signal
# and the CI signal disagreed and the local one is the one a contributor sees.
#
# The glob still decides the PATTERN, because `validate_vale_style.py` refuses
# a Vale binding to any glob the token file does not declare, and moving
# selection out of the token file would break that binding. What changed is the
# denominator: the pattern is now intersected with the tracked set. The
# repository publishes what it tracks, and an untracked file publishes nothing.
#
# The sibling instrument made the same change for its DC-16 contract
# (MrBinnacle/skill-harness#473) after the same probe found the same defect.
GIT_LS_FILES: Final[tuple[str, ...]] = ("git", "ls-files", "-z", "--cached")


class TrackedSetUnreadable(Refusal):
    """``git ls-files`` could not name the tracked set.

    The check REFUSES here rather than falling back to a filesystem walk. A
    walk over a tree git cannot describe scans a different set of files under
    the same check name, and reports PASS for it. Reporting an empty scan is
    the same defect wearing a clean face.
    """


def tracked_paths(root: Path) -> frozenset[str]:
    """Repo-relative posix paths of every file in the index.

    ``git ls-files --cached`` reads the index. It makes no network call, needs
    no commit, and answers exactly the question the check is asking: what can a
    commit in this repository change?
    """
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user input
            [*GIT_LS_FILES],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise TrackedSetUnreadable(
            f"could not run {' '.join(GIT_LS_FILES)} under {root} to read the "
            f"tracked set: {error}. This check scans what this repository "
            "tracks, so it refuses rather than scanning something else."
        ) from error
    if result.returncode != 0:
        raise TrackedSetUnreadable(
            f"{' '.join(GIT_LS_FILES)} exited {result.returncode} under {root}, "
            f"so the tracked set is unknown: {result.stderr.strip()!r}. This "
            "check scans what this repository tracks, so it refuses rather "
            "than falling back to a filesystem walk."
        )
    return frozenset(entry for entry in result.stdout.split("\0") if entry)


def tracked_matches(root: Path, glob: str, tracked: frozenset[str]) -> list[Path]:
    """The files a glob resolves to, restricted to the tracked set."""
    return [
        path
        for path in sorted(root.glob(glob))
        if path.is_file() and path.relative_to(root).as_posix() in tracked
    ]


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


def strip_fenced_blocks(markdown: str) -> str:
    """Markdown with its fenced code removed, before any heading scan.

    A shell comment inside a fence starts with '#', and a heading regex over
    the raw file reads it as a heading -- turning fenced working documentation
    into a false breach on exactly the class the scope rule excludes
    (cross-review reproduced it with a fenced '# earn a receipt' line).
    """
    kept: list[str] = []
    fence: str | None = None
    for line in markdown.splitlines():
        stripped = line.lstrip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            continue
        if fence is not None:
            if stripped.startswith(fence):
                fence = None
            continue
        kept.append(line)
    return "\n".join(kept)


def blank_fenced_blocks(markdown: str) -> str:
    """Markdown with every fenced-code line replaced by an empty line.

    Same exclusion as strip_fenced_blocks, and the line COUNT is preserved, so a
    violation's reported line number is its line number in the file. The
    headings surface can afford to drop lines, because it reports an offset into
    the headings it collected. A whole-document surface that dropped them would
    send a reader to the wrong line of a long skill card.
    """
    kept: list[str] = []
    fence: str | None = None
    for line in markdown.splitlines():
        stripped = line.lstrip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            kept.append("")
            continue
        if fence is not None:
            kept.append("")
            if stripped.startswith(fence):
                fence = None
            continue
        kept.append(line)
    return "\n".join(kept)


def word_list_digest(words: list[str]) -> str:
    """sha256 over the canonical JSON form of the word LIST, not of the file."""
    return hashlib.sha256(json.dumps(words, separators=(",", ":")).encode()).hexdigest()


def markdown_headings(markdown: str) -> list[str]:
    """ATX and setext headings, with fenced code stripped first."""
    prose = strip_fenced_blocks(markdown)
    return HEADING_RE.findall(prose) + SETEXT_RE.findall(prose)


def normalise_hex(value: str) -> str:
    """Lowercased six-digit form; short forms expanded, alpha dropped.

    Four- and eight-digit hexes carry an alpha channel (CSS Color 4; Inkscape
    exports them). The alpha is dropped so a declared colour exported with
    alpha still matches its token -- reporting #8b949eff as an undeclared
    colour told the maintainer to declare an alpha variant of a colour the
    kit already declares. Odd lengths (5, 7) pass through unchanged and read
    as undeclared, which is the safe direction for a malformed colour.
    """
    digits = value[1:].lower()
    if len(digits) in (3, 4):
        digits = "".join(digit * 2 for digit in digits)
    if len(digits) == 8:
        digits = digits[:6]
    return "#" + digits


# --------------------------------------------------------------------------
# Surfaces.
# --------------------------------------------------------------------------
def surface_copy(
    root: Path, spec: dict[str, Any], tracked: frozenset[str]
) -> list[tuple[str, str]]:
    """(label, copy) for every TRACKED file a surface spec resolves to."""
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

    excludes = spec.get("exclude", [])
    if not isinstance(excludes, list) or not all(
        isinstance(pattern, str) and pattern for pattern in excludes
    ):
        raise Refusal(
            f"surface of kind {kind} states an exclude list that is not a list of "
            "non-empty strings."
        )

    paths = tracked_matches(root, glob, tracked)
    if not paths:
        raise Refusal(
            f"surface glob {ascii(glob)} matched no tracked file under {root}. A "
            "surface that resolves to nothing is a check that runs on nothing. "
            "Selection is the tracked set (#267), so a file that exists in the "
            "working tree and is not in the index does not count."
        )

    # fnmatch's `*` crosses `/`, which is what lets `_quarantine/**` reach a
    # candidate nested at any depth.
    matched = len(paths)
    paths = [
        path
        for path in paths
        if not any(
            fnmatch.fnmatch(path.relative_to(root).as_posix(), pattern)
            for pattern in excludes
        )
    ]
    if not paths:
        raise Refusal(
            f"surface glob {ascii(glob)} matched {matched} file(s) under {root} and "
            "the exclude list removed every one of them. A surface excluded down to "
            "nothing is a check that runs on nothing."
        )

    collected: list[tuple[str, str]] = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if kind == "svg_copy":
            collected.append((f"{relative}:svg-copy", svg_copy(text)))
        elif kind == "markdown_headings":
            collected.append((f"{relative}:headings", "\n".join(markdown_headings(text))))
        elif kind == "markdown_prose":
            collected.append((f"{relative}:prose", blank_fenced_blocks(text)))
        else:
            field = spec.get("field")
            if not isinstance(field, str) or not field:
                raise Refusal(f"json_string_field surface {ascii(glob)} names no field")
            try:
                data = json.loads(text)
            except json.JSONDecodeError as error:
                # The same wrap load_tokens applies to tokens.json: a raw
                # traceback breaks the typed-refusal output contract.
                raise Refusal(f"{relative} is not valid JSON: {error}") from error
            value = data.get(field) if isinstance(data, dict) else None
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


def css_hexes(css: str) -> list[str]:
    """Colours a stylesheet ships. A hex inside a comment ships nothing.

    The SVG scanner goes through a parser so that a hex in an XML comment is
    not read as a shipped colour (`case_hex_in_a_comment_ignored`). CSS needs
    the same exemption for the same reason, and CSS has one comment form, so
    removing `/* ... */` before scanning is the whole of it.
    """
    return HEX_RE.findall(CSS_COMMENT_RE.sub(" ", css))


def hex_surface_specs(tokens: dict[str, Any]) -> list[dict[str, Any]]:
    """The declared-hex surfaces, read as data (#256).

    Hard-coding the glob would make widening the check an invisible edit. The
    token file states which files ship colour, the same way it states which
    files carry public copy.
    """
    colour_block = tokens.get("color")
    block = colour_block.get("declared_hex_surfaces") if isinstance(colour_block, dict) else None
    if not isinstance(block, dict):
        raise Refusal("color.declared_hex_surfaces is missing")
    specs = block.get("surfaces")
    if not isinstance(specs, list) or not specs:
        raise Refusal(
            "color.declared_hex_surfaces.surfaces is empty. A declared palette "
            "with no surface to read is a check over nothing."
        )
    return [spec for spec in specs if isinstance(spec, dict)]


def undeclared_hex_violations(
    root: Path,
    declared: set[str],
    specs: list[dict[str, Any]],
    tracked: frozenset[str],
) -> tuple[list[str], int, int]:
    violations: list[str] = []
    seen: set[str] = set()
    files = 0
    for spec in specs:
        kind = spec.get("kind")
        glob = spec.get("glob")
        if not isinstance(glob, str) or not glob:
            raise Refusal("a declared_hex_surfaces entry names no glob")
        if kind not in ("svg_hex", "css_hex"):
            raise Refusal(
                f"declared_hex_surfaces kind {ascii(kind)} is not one this script "
                "implements. Kinds are svg_hex and css_hex. A surface kind nothing "
                "reads is a declared check that never runs."
            )
        paths = tracked_matches(root, glob, tracked)
        if not paths:
            raise Refusal(
                f"declared_hex_surfaces glob {ascii(glob)} matched no tracked file "
                f"under {root}. A surface that matches nothing is a check over "
                "nothing. Selection is the tracked set (#267), the same denominator "
                "the copy surfaces use."
            )
        files += len(paths)
        for path in paths:
            relative = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            raws = svg_hexes(text) if kind == "svg_hex" else css_hexes(text)
            for raw in raws:
                colour = normalise_hex(raw)
                seen.add(colour)
                if colour not in declared:
                    violations.append(
                        f"{relative}: undeclared hex {colour}. Every colour a "
                        "surface ships must be declared in assets/tokens.json. "
                        "Declare it, or change the surface to a colour that is."
                    )
    return sorted(set(violations)), len(seen), files


# --------------------------------------------------------------------------
# Entrypoint.
# --------------------------------------------------------------------------
def validate(root: Path) -> None:
    tokens = load_tokens(root)
    # Read once, after the declaration is validated and before any surface
    # resolves. A per-surface read would run git a dozen times over an index
    # that cannot change mid-run, and would let two surfaces disagree about
    # what this repository tracks. It runs AFTER load_tokens so a tree with
    # neither a token file nor an index still refuses on the token file, which
    # is the problem its reader can act on.
    tracked = tracked_paths(root)

    copy_block = tokens.get("copy")
    if not isinstance(copy_block, dict):
        raise Refusal("assets/tokens.json states no copy block")
    words = copy_block.get("words_to_avoid")
    if not isinstance(words, list) or not words or not all(isinstance(w, str) for w in words):
        raise Refusal(
            "copy.words_to_avoid is empty or not a list of strings. An empty ban "
            "list makes the copy check pass on every possible input."
        )
    digest_block = copy_block.get("words_to_avoid_digest")
    if not isinstance(digest_block, dict):
        raise Refusal(
            "copy.words_to_avoid_digest is missing. MrBinnacle/skill-harness#462 "
            "vendors this word list and compares its copy against the published "
            "digest, so an unpublished digest is a drift contract with nothing to "
            "compare against."
        )
    published = digest_block.get("sha256")
    computed = word_list_digest(words)
    if published != computed:
        raise Refusal(
            f"copy.words_to_avoid_digest.sha256 records {ascii(published)}, and the "
            f"list on disk digests to {ascii(computed)}. The word list was edited "
            "without re-recording the digest, so the sibling that vendors this list "
            "would compare against a value naming a list that no longer exists. Run: "
            "python scripts/validate_brand_kit.py --record-digest"
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
    prose_seen = 0
    prose_surfaces = 0
    for spec in specs:
        if not isinstance(spec, dict):
            raise Refusal("a surface entry is not an object")
        resolved = surface_copy(root, spec, tracked)
        if spec.get("kind") == "svg_copy":
            svg_copy_seen += sum(len(text.strip()) for _, text in resolved)
        if spec.get("kind") == "markdown_prose":
            prose_surfaces += 1
            prose_seen += sum(len(text.strip()) for _, text in resolved)
        surfaces.extend(resolved)

    if svg_copy_seen == 0:
        raise Refusal(
            "the SVG scanner saw no copy in any asset. Either no asset carries "
            "an aria-label or a text/title/desc element, or the scanner has gone "
            "blind - and a blind scanner passes everything."
        )
    if prose_surfaces and prose_seen == 0:
        raise Refusal(
            "the markdown prose scanner saw no text in any document. Either every "
            "in-scope document is fenced code end to end, or the fence remover has "
            "eaten the tree - and either way the widest surface is reading nothing."
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
    hex_specs = hex_surface_specs(tokens)
    hex_violations, distinct_hexes, hex_files = undeclared_hex_violations(
        root, declared, hex_specs, tracked
    )
    if hex_files == 0:
        raise Refusal(f"no declared-hex surface matched any file under {root}")
    if distinct_hexes == 0:
        raise Refusal(
            "no colour was found on any declared-hex surface. Either every asset "
            "inherits currentColor and the stylesheet names none, or the hex "
            "scanner has gone blind."
        )
    violations.extend(hex_violations)

    if violations:
        for line in violations:
            print(f"  - {line}", file=sys.stderr)
        print(
            f"REJECTED: {len(violations)} brand kit breach(es) across "
            f"{len(surfaces)} public copy surface(s) and {hex_files} declared-hex surface(s).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    version = tokens.get("version", "unversioned")
    print(
        f"PASS: brand kit {version} enforced - {len(surfaces)} public copy "
        f"surface(s) scanned against {len(words)} banned word(s), "
        f"{len(pairs)} asset pair(s) hash-verified, {distinct_hexes} distinct "
        f"hex(es) across {hex_files} declared-hex surface(s) all declared in the kit. "
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


def record_digest(root: Path) -> None:
    """Rewrite the published digest in place, leaving the rest of the file alone.

    A json.dumps round trip would reformat every compact array in the token file,
    so the value is replaced as text. --record-hashes rewrites the whole file
    because it has several values to set; this has one.
    """
    path = root / TOKENS_PATH
    tokens = load_tokens(root)
    copy_block = tokens.get("copy")
    words = copy_block.get("words_to_avoid") if isinstance(copy_block, dict) else None
    if not isinstance(words, list) or not words:
        raise Refusal("copy.words_to_avoid is empty or missing, so there is nothing to digest")
    digest = word_list_digest(words)
    text = path.read_text(encoding="utf-8")
    updated, count = DIGEST_FIELD_RE.subn(lambda m: f'{m.group(1)}"{digest}"', text, count=1)
    if count != 1:
        raise Refusal(
            "copy.words_to_avoid_digest.sha256 is not present as a literal field in "
            f"{TOKENS_PATH}, so it cannot be rewritten in place. Add the field first."
        )
    path.write_text(updated, encoding="utf-8")
    print(f"recorded copy.words_to_avoid_digest.sha256 = {digest}")


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
    parser.add_argument(
        "--record-digest",
        action="store_true",
        help="rewrite copy.words_to_avoid_digest.sha256 from the word list on disk",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.record_hashes:
            record_hashes(root)
            return
        if args.record_digest:
            record_digest(root)
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
