"""Validate this repository's Vale configuration against its two sources of truth.

WHY THIS EXISTS

    This repository CONSUMES a prose style it does not own. The six Taste rules are
    authored in `skill-harness` (MrBinnacle/skill-harness#304) and vendored here as a
    byte-equal copy. A vendored file with no digest check is a fork waiting to happen:
    someone edits a rule locally to silence a finding, both repositories keep reporting
    "the Taste style", and the two stop meaning the same thing with nothing to notice.

    A SEVENTH rule is different in kind and is generated here rather than vendored.
    `assets/tokens.json > copy.words_to_avoid` is a BANNED-MARKETING-COPY list owned by
    this repository's brand kit. It is disjoint from the vendored `Generic-ness` rule,
    which bans VAGUENESS (`various`, `several`, `stuff`). The two lists answer different
    questions and neither is a version of the other.

THE SCOPE RULE, AND WHY THIS SCRIPT REFUSES TO WIDEN IT

    `assets/tokens.json > copy.words_to_avoid_surfaces.$note` states the constraint:

        "Widening the scope is a decision, not a maintenance task ... README BODY prose
        is deliberately absent - banned words appear there and in working documentation
        on purpose."

    So the generated rule is NOT applied to the tree. `.vale.ini` binds it to the same
    globs `copy.words_to_avoid_surfaces` declares, and this script asserts that binding.
    Running the marketing list over working documentation would report as findings the
    very words that file says appear there deliberately, and would put Vale and
    `scripts/validate_brand_kit.py` on opposite sides of one word list - the failure this
    repository has already recorded once, where a renderer emitted the split its own
    guard banned.

    `validate_brand_kit.py` remains the GATE for those surfaces. The generated Vale rule
    is an editor-and-CI convenience that reports the same list at the same scope. This
    script's agreement check is what keeps the convenience honest: if the two ever
    disagree, the run fails rather than letting the weaker one drift.

WHAT IT CHECKS

    1. VENDOR INTEGRITY. Every file named in `styles/Taste/STYLE_SOURCE.json` exists and
       its SHA-256 matches. An unlisted `.yml` in that directory is also a failure - a
       new rule vendored without a digest is exactly the ungoverned case.
    2. GENERATED-RULE AGREEMENT. `styles/Local/Marketing-copy.yml` regenerates byte-for-
       byte from the current `tokens.json` word list.
    3. SCOPE BINDING. `.vale.ini` applies `Local` only to the declared surface globs, and
       applies `Taste` without the marketing rule.

VACUITY REFUSALS

    Each check refuses rather than passes when its own input is empty: no vendored files,
    an empty word list, or no declared surfaces. A check that passes because it examined
    nothing is the defect this repository exists to detect.

Usage:
    python scripts/validate_vale_style.py            # verify
    python scripts/validate_vale_style.py --write    # regenerate the derived rule
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STYLE_DIR = REPO_ROOT / "styles" / "Taste"
LOCAL_DIR = REPO_ROOT / "styles" / "Local"
MANIFEST = STYLE_DIR / "STYLE_SOURCE.json"
TOKENS = REPO_ROOT / "assets" / "tokens.json"
VALE_INI = REPO_ROOT / ".vale.ini"
GENERATED_RULE = LOCAL_DIR / "Marketing-copy.yml"

GENERATED_HEADER = (
    "# GENERATED FILE - do not edit.\n"
    "# Rendered from assets/tokens.json > copy.words_to_avoid by\n"
    "# scripts/validate_vale_style.py --write. Edit the token file, then regenerate.\n"
    "#\n"
    "# Scope: this rule is bound in .vale.ini to the globs declared in\n"
    "# copy.words_to_avoid_surfaces. It is deliberately NOT applied to the tree - the\n"
    "# token file states that banned words appear in working documentation on purpose.\n"
)


class Refusal(Exception):
    """The check cannot run, so it reports nothing rather than a false pass."""


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise Refusal(f"{path.relative_to(REPO_ROOT)} is missing")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Refusal(f"{path.relative_to(REPO_ROOT)} is not valid JSON: {exc}") from exc


def banned_words() -> list[str]:
    """The marketing word list, refusing an empty list rather than banning nothing."""
    copy_block = _load_json(TOKENS).get("copy")
    if not isinstance(copy_block, dict):
        raise Refusal("assets/tokens.json has no copy block")
    words = copy_block.get("words_to_avoid")
    if not isinstance(words, list) or not words:
        raise Refusal(
            "copy.words_to_avoid is empty or not a list. An empty ban list would make "
            "the generated rule vacuous: it would pass every surface by banning nothing."
        )
    if not all(isinstance(w, str) and w.strip() for w in words):
        raise Refusal("copy.words_to_avoid contains a non-string or blank entry")
    return list(words)


def declared_surface_globs() -> list[str]:
    """The globs the token file binds the marketing list to."""
    copy_block = _load_json(TOKENS).get("copy", {})
    block = copy_block.get("words_to_avoid_surfaces")
    if not isinstance(block, dict):
        raise Refusal("copy.words_to_avoid_surfaces is missing")
    specs = block.get("surfaces")
    if not isinstance(specs, list) or not specs:
        raise Refusal(
            "copy.words_to_avoid_surfaces.surfaces is empty. A ban list bound to no "
            "surface refuses nothing."
        )
    globs: list[str] = []
    for spec in specs:
        glob = spec.get("glob") if isinstance(spec, dict) else None
        if not isinstance(glob, str) or not glob:
            raise Refusal("a declared surface states no glob")
        globs.append(glob)
    return sorted(set(globs))


def render_rule(words: list[str]) -> str:
    """Render the marketing rule. Deterministic: same list in, same bytes out."""
    lines = [
        GENERATED_HEADER,
        "extends: existence",
        'message: "Marketing copy: %s is banned on public asset copy '
        '(assets/tokens.json > copy.words_to_avoid)."',
        "level: warning",
        "ignorecase: true",
        "scope: heading",
        "tokens:",
    ]
    for word in words:
        lines.append(f"  - '\\b{re.escape(word)}\\b'")
    return "\n".join(lines) + "\n"


def check_vendor_integrity() -> list[str]:
    """Every vendored rule is byte-equal to its recorded digest, and none is unlisted."""
    manifest = _load_json(MANIFEST)
    recorded = manifest.get("files")
    if not isinstance(recorded, dict) or not recorded:
        raise Refusal(
            "STYLE_SOURCE.json records no files. A digest check over zero files passes "
            "trivially and certifies nothing."
        )
    problems: list[str] = []
    for name, expected in sorted(recorded.items()):
        path = STYLE_DIR / name
        if not path.is_file():
            problems.append(f"vendored rule {name} is recorded but missing")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            problems.append(
                f"vendored rule {name} does not match its recorded digest. "
                f"expected {expected}, found {actual}. The style is authored in "
                f"{manifest.get('source_repo')}; re-vendor rather than editing here."
            )
    on_disk = {p.name for p in STYLE_DIR.glob("*.yml")}
    for extra in sorted(on_disk - set(recorded)):
        problems.append(
            f"vendored rule {extra} is present but not recorded in STYLE_SOURCE.json. "
            "An unrecorded rule is outside the digest check."
        )
    return problems


def check_generated_rule() -> list[str]:
    """The committed rule equals what the current word list renders."""
    expected = render_rule(banned_words())
    if not GENERATED_RULE.is_file():
        return [f"{GENERATED_RULE.relative_to(REPO_ROOT)} is missing; run --write"]
    actual = GENERATED_RULE.read_text(encoding="utf-8")
    if actual != expected:
        return [
            f"{GENERATED_RULE.relative_to(REPO_ROOT)} disagrees with "
            "assets/tokens.json > copy.words_to_avoid. Run "
            "'python scripts/validate_vale_style.py --write' and commit the result."
        ]
    return []


def check_scope_binding() -> list[str]:
    """.vale.ini binds the marketing rule to the declared surfaces and nowhere else."""
    if not VALE_INI.is_file():
        raise Refusal(".vale.ini is missing")
    text = VALE_INI.read_text(encoding="utf-8")
    sections = re.findall(r"^\[([^\]]+)\]", text, flags=re.MULTILINE)
    if not sections:
        raise Refusal(".vale.ini declares no sections, so no scope is asserted")

    problems: list[str] = []
    globs = declared_surface_globs()
    enabling = [
        section
        for section in sections
        if "Local" in text.split(f"[{section}]", 1)[1].split("\n[", 1)[0]
    ]

    # Vacuity: a rule bound to no section reports on nothing.
    if not enabling:
        raise Refusal(
            "no .vale.ini section enables the Local style, so the generated marketing "
            "rule is bound to nothing and would pass every run without reading a file."
        )

    # No widening: every binding sits on a surface the token file declares.
    for section in enabling:
        if section not in globs:
            problems.append(
                f".vale.ini section [{section}] enables the Local style, which carries "
                "the marketing word list. assets/tokens.json > "
                "copy.words_to_avoid_surfaces.$note states that widening this scope is "
                f"a decision, not a maintenance task. Declared surfaces: {globs}."
            )

    # README.md is declared as HEADINGS only, so the rule must say so itself.
    if "README.md" in enabling:
        rule = GENERATED_RULE.read_text(encoding="utf-8") if GENERATED_RULE.is_file() else ""
        if "scope: heading" not in rule:
            problems.append(
                "the marketing rule is bound to README.md but does not declare "
                "'scope: heading'. assets/tokens.json restricts this surface to "
                "'README headers only ... its body prose is working documentation and "
                "out of scope'. Without the scope the rule reads the whole body."
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate styles/Local/Marketing-copy.yml from assets/tokens.json",
    )
    args = parser.parse_args(argv)

    try:
        if args.write:
            LOCAL_DIR.mkdir(parents=True, exist_ok=True)
            # newline="" keeps the rendered "\n" bytes as written. Without it
            # Python translates to CRLF on Windows, so the same word list would
            # render different bytes on different platforms - the defect the
            # .gitattributes eol rule exists to prevent one layer down.
            GENERATED_RULE.write_text(
                render_rule(banned_words()), encoding="utf-8", newline=""
            )
            print(f"wrote {GENERATED_RULE.relative_to(REPO_ROOT)}")
            return 0

        problems = check_vendor_integrity()
        problems += check_generated_rule()
        problems += check_scope_binding()
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    if problems:
        print("Vale style validation FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    manifest = _load_json(MANIFEST)
    print(
        f"PASS: {len(manifest['files'])} vendored rules match "
        f"{manifest['source_repo']}@{manifest['source_commit'][:7]}; "
        f"the generated marketing rule agrees with assets/tokens.json "
        f"({len(banned_words())} words) and is bound to "
        f"{len(declared_surface_globs())} declared surfaces."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
