#!/usr/bin/env python3
"""Suite for validate_brand_kit.py.

Every rejection runs the real entrypoint against a real temporary tree. No
poison fixture is checked in: a violating asset committed under `assets/` would
sit inside the guarded set and turn the real run permanently red, which is the
hole an exclusion list opens.

EACH FIXTURE FAILS ON ONE ASSERTION, AND THE SUITE PROVES IT
    Every tree below is a single mutation of the conforming baseline in
    `baseline_tree`, and every breach case asserts the breach COUNT as well as
    the message. The checker collects all three checks' violations before it
    reports, so a fixture red for two reasons would stay red if the check under
    test were deleted -- the count is what rules that out.

THE SCOPE BOUNDARY IS PINNED BEFORE THE CHECK THAT COULD WIDEN IT
    `case_readme_body_prose_passes` is first on purpose. The banned list holds
    words that appear legitimately in working documentation, and the cheapest
    way to make a copy check "more thorough" is to read whole files instead of
    headings. That fixture goes red the moment anyone does.

NON-VACUITY IS PROVEN TWICE
    Once against the temporary trees, where a scanner that returned nothing
    would fail every rejection case. And once against the LIVE tree, by
    `case_live_svg_scanner_sees_real_copy`, ported from the sibling
    instrument's meta-test: it asserts the scanner reads actual text out of the
    shipped assets. Two of the three checks guard an ABSENCE -- no banned word,
    no hash mismatch -- so a scanner that had gone blind would look exactly like
    a repository in good order.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "validate_brand_kit.py"
REPO_ROOT = SCRIPT_DIR.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"

sys.path.insert(0, str(SCRIPT_DIR))
import validate_brand_kit as kit  # noqa: E402

FAILURES: list[str] = []

# Anchored on "REJECTED: " so a count merely ENDING in 1 (11, 21, ...) cannot
# satisfy the single-reason guard.
ONE_BREACH = "REJECTED: 1 brand kit breach(es)"

# The sibling instrument's semantic palette. Neither banner may wear it.
INSTRUMENT_PALETTE = ("#3fb950", "#2da44e", "#d29922", "#58a6ff")

BASELINE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="40" role="img"'
    ' aria-label="skills - the inventory">\n'
    '  <text x="4" y="20" fill="#e6edf3">Every card states what it cost.</text>\n'
    "</svg>\n"
)

BASELINE_README = (
    "# The collection\n\n"
    "The apostrophe rule here is load-bearing and the retry budget is robust.\n"
    "Both sentences are working documentation, and both are out of scope.\n\n"
    "## Admission method\n\n"
    "A card is admitted by the gate.\n"
)

BASELINE_PACKAGE = {
    "name": "mrbinnacle-skills",
    "description": "A small, evidence-backed collection of agent skills.",
}


def baseline_tokens() -> dict[str, Any]:
    """The conforming baseline. Every fixture below mutates exactly one thing.

    Written out here rather than read from assets/tokens.json: a baseline taken
    from the tree under test would pass by construction and stop being evidence
    that the contract is the one the checker states.
    """
    return {
        "version": "9.9.9",
        "color": {
            "structural": {
                "repo.ink": {"value": "#E6EDF3", "role": "Primary text"},
            }
        },
        "copy": {
            "words_to_avoid": ["earn", "curated", "load-bearing", "robust", "unlock"],
            "words_to_avoid_scope": "Public asset copy only.",
            "words_to_avoid_surfaces": {
                "surfaces": [
                    {"kind": "svg_copy", "glob": "assets/*.svg"},
                    {"kind": "markdown_headings", "glob": "README.md"},
                    {
                        "kind": "json_string_field",
                        "glob": "package.json",
                        "field": "description",
                    },
                ]
            },
        },
        "asset_pairs": {
            "pairs": [],
            "pairs_pending": "No source ships yet.",
        },
    }


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True,
        text=True,
    )


def baseline_tree(
    root: Path,
    *,
    tokens: dict[str, Any] | None = None,
    svg: str = BASELINE_SVG,
    svg_name: str = "banner.svg",
    readme: str = BASELINE_README,
    package: dict[str, Any] | None = None,
    extra_assets: dict[str, bytes] | None = None,
) -> Path:
    """A conforming tree: one token file, one SVG asset, a README, a package."""
    assets = root / "assets"
    assets.mkdir(parents=True)
    (assets / "tokens.json").write_text(
        json.dumps(baseline_tokens() if tokens is None else tokens, indent=2),
        encoding="utf-8",
    )
    if svg is not None:
        (assets / svg_name).write_text(svg, encoding="utf-8")
    (root / "README.md").write_text(readme, encoding="utf-8")
    (root / "package.json").write_text(
        json.dumps(BASELINE_PACKAGE if package is None else package, indent=2),
        encoding="utf-8",
    )
    for name, blob in (extra_assets or {}).items():
        (assets / name).write_bytes(blob)
    return root


def expect_pass(name: str, root: Path) -> None:
    result = run_checker(root)
    check(
        name,
        result.returncode == 0 and result.stdout.startswith("PASS:"),
        f"rc={result.returncode} out={result.stdout.strip()!r} err={result.stderr.strip()!r}",
    )


def expect_one_breach(name: str, root: Path, *substrings: str) -> None:
    result = run_checker(root)
    missing = [item for item in substrings if item not in result.stderr]
    check(
        name,
        result.returncode == 1 and ONE_BREACH in result.stderr and not missing,
        f"rc={result.returncode} missing={missing!r} err={result.stderr.strip()!r}",
    )


def expect_refusal(name: str, root: Path, *substrings: str) -> None:
    """A refusal is an input problem, so it carries no breach count."""
    result = run_checker(root)
    missing = [item for item in substrings if item not in result.stderr]
    check(
        name,
        result.returncode == 1 and "REJECTED: " in result.stderr and not missing,
        f"rc={result.returncode} missing={missing!r} err={result.stderr.strip()!r}",
    )


# --------------------------------------------------------------------------
# The scope boundary. First, on purpose.
# --------------------------------------------------------------------------
def case_readme_body_prose_passes(tmp: Path) -> None:
    """Banned words in README BODY prose are out of scope and must pass.

    The baseline README carries two of them, in the sense the words are good
    for. This repository's AGENTS.md, SECURITY.md and skill cards do the same.
    Widening the copy check to whole files turns this red, which is the point.
    """
    expect_pass("readme body prose passes", baseline_tree(tmp))


def case_readme_heading_rejected(tmp: Path) -> None:
    readme = BASELINE_README.replace("## Admission method", "## Skills that earn their keep")
    expect_one_breach(
        "readme heading with a banned word rejected",
        baseline_tree(tmp, readme=readme),
        "README.md:headings",
        "banned word 'earn'",
    )


def case_body_prose_stays_out_when_the_heading_is_clean(tmp: Path) -> None:
    """The discriminator. A banned word two lines below a clean heading passes.

    A whole-file scan would call this a breach. The line number reported for
    the heading case above must therefore be an offset into the HEADINGS, not
    into the file.
    """
    readme = BASELINE_README + "\n### A clean heading\n\nMore curated notes here.\n"
    expect_pass("body prose below a clean heading passes", baseline_tree(tmp, readme=readme))


def case_fenced_code_is_not_a_heading(tmp: Path) -> None:
    """A shell comment inside a fence starts with '#' and is not a heading.

    Cross-review reproduced the false breach: a fenced '# earn ...' line read
    as a heading turned working documentation red -- exactly the class the
    scope rule excludes.
    """
    readme = BASELINE_README + (
        "\n```bash\n# earn a receipt for every run\necho done\n```\n"
    )
    expect_pass("a banned word in fenced code passes", baseline_tree(tmp, readme=readme))


def case_setext_heading_rejected(tmp: Path) -> None:
    """A setext heading is part of the headings surface, same as ATX.

    Cross-review reproduced the miss: 'Skills that earn their keep' underlined
    with equals signs passed while the same words behind '##' were refused.
    """
    readme = BASELINE_README + "\nSkills that earn their keep\n====\n"
    expect_one_breach(
        "setext heading with a banned word rejected",
        baseline_tree(tmp, readme=readme),
        "README.md:headings",
        "banned word 'earn'",
    )


def case_malformed_package_json_refused(tmp: Path) -> None:
    """A surface that does not parse is a typed refusal, not a traceback."""
    root = baseline_tree(tmp)
    (root / "package.json").write_text('{"description": ,}\n', encoding="utf-8")
    expect_refusal(
        "a malformed package.json is a typed refusal",
        root,
        "package.json is not valid JSON",
    )


# --------------------------------------------------------------------------
# SVG copy: the half a regex over <text> would miss.
# --------------------------------------------------------------------------
def case_aria_label_only_rejected(tmp: Path) -> None:
    """The only violation lives in an aria-label. A <text>-only check passes it."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img"'
        ' aria-label="A curated collection">\n'
        '  <text x="4" y="20" fill="#e6edf3">Every card states what it cost.</text>\n'
        "</svg>\n"
    )
    expect_one_breach(
        "banned word in an aria-label rejected",
        baseline_tree(tmp, svg=svg),
        "assets/banner.svg:svg-copy",
        "banned word 'curated'",
    )


def case_text_element_rejected(tmp: Path) -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="skills">\n'
        '  <text x="4" y="20" fill="#e6edf3">Skills that unlock the agent.</text>\n'
        "</svg>\n"
    )
    expect_one_breach(
        "banned word in a text element rejected",
        baseline_tree(tmp, svg=svg),
        "banned word 'unlock'",
    )


def case_title_and_desc_scanned(tmp: Path) -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="skills">\n'
        "  <desc>A robust inventory.</desc>\n"
        '  <text x="4" y="20" fill="#e6edf3">Every card states what it cost.</text>\n'
        "</svg>\n"
    )
    expect_one_breach(
        "banned word in a desc element rejected",
        baseline_tree(tmp, svg=svg),
        "banned word 'robust'",
    )


def case_word_split_across_tspans_rejected(tmp: Path) -> None:
    """itertext() reassembles copy a regex over element bodies reads as fragments."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="skills">\n'
        '  <text x="4" y="20" fill="#e6edf3">A <tspan>load-bearing</tspan> claim.</text>\n'
        "</svg>\n"
    )
    expect_one_breach(
        "banned word split across tspans rejected",
        baseline_tree(tmp, svg=svg),
        "banned word 'load-bearing'",
    )


def case_word_containing_a_banned_word_passes(tmp: Path) -> None:
    """Nearest-legitimate. 'learn' contains 'earn'; 'unlockable' contains 'unlock'."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" role="img"'
        ' aria-label="What the records learn">\n'
        '  <text x="4" y="20" fill="#e6edf3">An unlockable state, not load bearing.</text>\n'
        "</svg>\n"
    )
    expect_pass("a longer word containing a banned word passes", baseline_tree(tmp, svg=svg))


def case_package_description_rejected(tmp: Path) -> None:
    package = dict(BASELINE_PACKAGE, description="A curated collection of agent skills.")
    expect_one_breach(
        "banned word in the repository description rejected",
        baseline_tree(tmp, package=package),
        "package.json:description",
        "banned word 'curated'",
    )


def case_ban_list_is_data(tmp: Path) -> None:
    """Adding a word is a data edit. Nothing in the checker names any word."""
    tokens = baseline_tokens()
    tokens["copy"]["words_to_avoid"].append("inventory")
    expect_one_breach(
        "a word added only to the token file is enforced",
        baseline_tree(tmp, tokens=tokens),
        "banned word 'inventory'",
    )


# --------------------------------------------------------------------------
# Hash pairs.
# --------------------------------------------------------------------------
def _pair_tokens(source_blob: bytes, export_blob: bytes) -> dict[str, Any]:
    tokens = baseline_tokens()
    tokens["asset_pairs"] = {
        "pairs": [
            {
                "source": "assets/preview.svg",
                "export": "assets/preview.png",
                "source_sha256": hashlib.sha256(source_blob).hexdigest(),
                "export_sha256": hashlib.sha256(export_blob).hexdigest(),
            }
        ]
    }
    return tokens


PAIR_SOURCE = (
    '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="preview">\n'
    '  <text x="4" y="20" fill="#e6edf3">Admitted, measured, retired.</text>\n'
    "</svg>\n"
).encode("utf-8")
PAIR_EXPORT = b"\x89PNG\r\n\x1a\n-not-a-real-raster-"


def case_matching_pair_passes(tmp: Path) -> None:
    root = baseline_tree(
        tmp,
        tokens=_pair_tokens(PAIR_SOURCE, PAIR_EXPORT),
        extra_assets={"preview.svg": PAIR_SOURCE, "preview.png": PAIR_EXPORT},
    )
    expect_pass("a pair whose hashes match passes", root)


def case_stale_export_rejected(tmp: Path) -> None:
    """The defeat this check exists for: the source is edited, the export is not."""
    edited = PAIR_SOURCE.replace(b"Admitted", b"Admitted anew")
    root = baseline_tree(
        tmp,
        tokens=_pair_tokens(PAIR_SOURCE, PAIR_EXPORT),
        extra_assets={"preview.svg": edited, "preview.png": PAIR_EXPORT},
    )
    expect_one_breach(
        "an edited source with a stale export rejected",
        root,
        "assets/preview.svg: recorded hash disagrees",
    )


def case_edited_export_rejected(tmp: Path) -> None:
    root = baseline_tree(
        tmp,
        tokens=_pair_tokens(PAIR_SOURCE, PAIR_EXPORT),
        extra_assets={"preview.svg": PAIR_SOURCE, "preview.png": PAIR_EXPORT + b"x"},
    )
    expect_one_breach(
        "an edited export rejected",
        root,
        "assets/preview.png: recorded hash disagrees",
    )


def case_missing_pair_half_rejected(tmp: Path) -> None:
    root = baseline_tree(
        tmp,
        tokens=_pair_tokens(PAIR_SOURCE, PAIR_EXPORT),
        extra_assets={"preview.svg": PAIR_SOURCE},
    )
    expect_one_breach(
        "a pair half that does not exist rejected",
        root,
        "assets/preview.png' does not exist",
    )


def case_empty_pairs_with_no_reason_refused(tmp: Path) -> None:
    """A freshness check over zero pairs is vacuous. The emptiness is declared."""
    tokens = baseline_tokens()
    tokens["asset_pairs"] = {"pairs": []}
    expect_refusal(
        "empty pair list with no stated reason refused",
        baseline_tree(tmp, tokens=tokens),
        "records no pair and states no reason",
    )


# --------------------------------------------------------------------------
# Declared hexes.
# --------------------------------------------------------------------------
def case_undeclared_hex_rejected(tmp: Path) -> None:
    svg = BASELINE_SVG.replace("#e6edf3", "#3fb950")
    expect_one_breach(
        "an undeclared hex rejected",
        baseline_tree(tmp, svg=svg),
        "undeclared hex #3fb950",
    )


def case_prose_naming_a_hex_declares_nothing(tmp: Path) -> None:
    """The defect the CI poison control found before this suite did.

    assets/tokens.json > color.usage_rules names #3FB950 inside the sentence
    saying that colour belongs to the sibling instrument and must not be used
    here. The first version of `declared_hexes` scanned every string in the
    file, so that sentence read as a declaration and planting the instrument
    green back into a banner PASSED - the ban was its own permission. Only a
    `value` field on a token object declares a colour.
    """
    tokens = baseline_tokens()
    tokens["color"]["usage_rules"] = [
        "The instrument's #3fb950 belongs to skill-harness and is not part of this set."
    ]
    svg = BASELINE_SVG.replace("#e6edf3", "#3fb950")
    expect_one_breach(
        "a hex named in prose is not thereby declared",
        baseline_tree(tmp, tokens=tokens, svg=svg),
        "undeclared hex #3fb950",
    )


def case_declared_hex_is_case_insensitive(tmp: Path) -> None:
    """The kit writes #E6EDF3; the assets write #e6edf3. Both are the colour."""
    expect_pass("a declared hex matches regardless of case", baseline_tree(tmp))


def case_three_digit_hex_normalised(tmp: Path) -> None:
    tokens = baseline_tokens()
    tokens["color"]["structural"]["repo.ink"]["value"] = "#FFFFFF"
    svg = BASELINE_SVG.replace("#e6edf3", "#fff")
    expect_pass(
        "a three-digit hex is normalised before comparison",
        baseline_tree(tmp, tokens=tokens, svg=svg),
    )


def case_alpha_hex_of_declared_colour_passes(tmp: Path) -> None:
    """An eight-digit export of a declared colour matches its token.

    Inkscape and CSS Color 4 emit #rrggbbaa. Cross-review reproduced the
    misleading refusal: the alpha form of an already-declared colour was
    reported as an undeclared colour, telling the maintainer to declare an
    alpha variant of a token the kit already has. The alpha is dropped in
    normalisation instead.
    """
    svg = BASELINE_SVG.replace("#e6edf3", "#e6edf3ff")
    expect_pass(
        "an alpha-carrying hex of a declared colour passes",
        baseline_tree(tmp, svg=svg),
    )


def case_hex_in_a_comment_ignored(tmp: Path) -> None:
    """A comment renders nothing, and both shipped banners name the removed green."""
    svg = BASELINE_SVG.replace(
        "<text", "<!-- was #3fb950, the instrument's colour, removed -->\n  <text"
    )
    expect_pass("a hex inside an XML comment is not scanned", baseline_tree(tmp, svg=svg))


def case_style_block_hex_scanned(tmp: Path) -> None:
    """A colour set in a <style> block ships exactly like an attribute does."""
    svg = BASELINE_SVG.replace(
        "<text", "<style>.seal { stroke: #d29922; }</style>\n  <text"
    )
    expect_one_breach(
        "a hex in a style block is scanned",
        baseline_tree(tmp, svg=svg),
        "undeclared hex #d29922",
    )


# --------------------------------------------------------------------------
# Non-vacuity refusals: the checker refuses inputs that would make it blind.
# --------------------------------------------------------------------------
def case_empty_ban_list_refused(tmp: Path) -> None:
    tokens = baseline_tokens()
    tokens["copy"]["words_to_avoid"] = []
    expect_refusal(
        "an empty ban list is refused",
        baseline_tree(tmp, tokens=tokens),
        "copy.words_to_avoid is empty",
    )


def case_surface_matching_nothing_refused(tmp: Path) -> None:
    tokens = baseline_tokens()
    tokens["copy"]["words_to_avoid_surfaces"]["surfaces"][1]["glob"] = "NOTHING.md"
    expect_refusal(
        "a surface glob matching no file is refused",
        baseline_tree(tmp, tokens=tokens),
        "matched no file",
    )


def case_unknown_surface_kind_refused(tmp: Path) -> None:
    tokens = baseline_tokens()
    tokens["copy"]["words_to_avoid_surfaces"]["surfaces"][1]["kind"] = "pdf_copy"
    expect_refusal(
        "an unreadable surface kind is refused",
        baseline_tree(tmp, tokens=tokens),
        "is not one of",
    )


def case_svg_with_no_copy_refused(tmp: Path) -> None:
    """The scanner-blindness guard. No aria-label, no text, no title, no desc."""
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#e6edf3"/></svg>\n'
    expect_refusal(
        "an asset set carrying no readable copy is refused",
        baseline_tree(tmp, svg=svg),
        "scanner saw no copy",
    )


def case_missing_token_file_refused(tmp: Path) -> None:
    (tmp / "assets").mkdir()
    expect_refusal("a tree with no token file is refused", tmp, "no token file")


# --------------------------------------------------------------------------
# The live tree.
# --------------------------------------------------------------------------
def case_live_tree_passes() -> None:
    expect_pass("the live repository passes", REPO_ROOT)


def case_live_svg_scanner_sees_real_copy() -> None:
    """Non-vacuity against what ships, ported from the sibling's meta-test.

    Two of the three checks guard an ABSENCE. A scanner returning "" would pass
    every one of them and look exactly like a repository in good order. This
    asserts it reads the banner statement out of the real files -- both from an
    aria-label and from a text element.
    """
    banner = (REPO_ROOT / "assets" / "banner-dark.svg").read_text(encoding="utf-8")
    copy = kit.svg_copy(banner)
    check(
        "the live scanner reads the banner statement",
        "Claude Code skills" in copy,
        f"scanned copy was {copy!r}",
    )
    stripped = kit.svg_copy(banner.replace(' aria-label="', ' data-not-a-label="'))
    check(
        "the aria-label is a distinct source of copy",
        "Claude Code skills" in copy and copy != stripped and len(stripped) < len(copy),
        f"with label {len(copy)} chars, without {len(stripped)} chars",
    )


def case_live_banners_carry_no_instrument_palette() -> None:
    """tokens.json > color.usage_rules: that palette belongs to skill-harness."""
    for name in ("banner-dark.svg", "banner-light.svg"):
        text = (REPO_ROOT / "assets" / name).read_text(encoding="utf-8")
        shipped = {kit.normalise_hex(found) for found in kit.svg_hexes(text)}
        borrowed = sorted(shipped.intersection(INSTRUMENT_PALETTE))
        check(
            f"{name} carries no instrument palette",
            not borrowed,
            f"found {borrowed}",
        )


def case_live_light_neutrals_are_declared() -> None:
    """The gap that blocked the hex check: a light banner with no tokens."""
    tokens = json.loads((REPO_ROOT / "assets" / "tokens.json").read_text(encoding="utf-8"))
    declared = kit.declared_hexes(tokens.get("color", {}).get("structural_light", {}), set())
    light = (REPO_ROOT / "assets" / "banner-light.svg").read_text(encoding="utf-8")
    shipped = {kit.normalise_hex(found) for found in kit.svg_hexes(light)}
    check(
        "every colour the light banner ships is a declared light neutral",
        bool(shipped) and shipped.issubset(declared),
        f"shipped {sorted(shipped)}, declared light {sorted(declared)}",
    )


def case_workflow_runs_the_checker() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for fragment in (
        "scripts/test_validate_brand_kit.py",
        "scripts/validate_brand_kit.py",
        "control-brand-copy",
        "control-brand-hash",
        "control-brand-hex",
    ):
        check(f"tests.yml carries {fragment}", fragment in workflow, str(WORKFLOW))


def main() -> None:
    in_tempdir = (
        case_readme_body_prose_passes,
        case_readme_heading_rejected,
        case_body_prose_stays_out_when_the_heading_is_clean,
        case_fenced_code_is_not_a_heading,
        case_setext_heading_rejected,
        case_malformed_package_json_refused,
        case_aria_label_only_rejected,
        case_text_element_rejected,
        case_title_and_desc_scanned,
        case_word_split_across_tspans_rejected,
        case_word_containing_a_banned_word_passes,
        case_package_description_rejected,
        case_ban_list_is_data,
        case_matching_pair_passes,
        case_stale_export_rejected,
        case_edited_export_rejected,
        case_missing_pair_half_rejected,
        case_empty_pairs_with_no_reason_refused,
        case_undeclared_hex_rejected,
        case_prose_naming_a_hex_declares_nothing,
        case_declared_hex_is_case_insensitive,
        case_three_digit_hex_normalised,
        case_alpha_hex_of_declared_colour_passes,
        case_hex_in_a_comment_ignored,
        case_style_block_hex_scanned,
        case_empty_ban_list_refused,
        case_surface_matching_nothing_refused,
        case_unknown_surface_kind_refused,
        case_svg_with_no_copy_refused,
        case_missing_token_file_refused,
    )
    for case in in_tempdir:
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))

    case_live_tree_passes()
    case_live_svg_scanner_sees_real_copy()
    case_live_banners_carry_no_instrument_palette()
    case_live_light_neutrals_are_declared()
    case_workflow_runs_the_checker()

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: brand-kit checker verified across {len(in_tempdir)} temporary "
        "tree(s) plus the live tree; every breach case asserts its own message "
        "and a breach count of one, the scope boundary is pinned by its own "
        "fixture, and the SVG scanner is proven non-vacuous against what ships."
    )


if __name__ == "__main__":
    main()
