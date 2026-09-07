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

THE SCOPE BOUNDARY MOVED, AND THE FIXTURE THAT PINNED IT IS NOW ITS CONTROL
    `case_readme_body_prose_passes` used to be first, asserting that a banned
    word in README BODY prose PASSED. The operator ruling of 2026-09-06 - one
    word list, all repositories, every single line of prose, the same rules -
    made that assertion wrong, so it was inverted rather than deleted:
    `case_markdown_prose_with_a_banned_word_rejected` now asserts the opposite,
    and it is still first. A scope boundary needs a fixture on it whichever side
    the boundary sits.

    The two exclusions the ruling left standing have a fixture each,
    `case_quarantine_document_excluded` and `case_changelog_excluded`, because an
    exclusion nothing tests is an exclusion that can widen by accident.

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
import re
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

# The baseline carries no banned word anywhere, headings or body. It used to
# carry two in its body, as the evidence that body prose was out of scope; under
# the 2026-09-06 ruling that same body is in scope, so a baseline carrying them
# would make every fixture below red for a second reason and destroy the breach
# counts the suite asserts.
BASELINE_README = (
    "# The collection\n\n"
    "The apostrophe rule here is what the parser depends on, and the retry budget is stated.\n"
    "Both sentences are working documentation, and both are now in scope.\n\n"
    "## Admission method\n\n"
    "A card is admitted by the gate.\n"
)

BASELINE_PACKAGE = {
    "name": "mrbinnacle-skills",
    "description": "A small, evidence-backed collection of agent skills.",
}


BASELINE_WORDS = ["earn", "curated", "load-bearing", "robust", "unlock"]


def word_list_digest(words: list[str]) -> str:
    """The published digest, recomputed here rather than imported from the checker.

    Calling `kit.word_list_digest` would make every fixture agree with the
    checker by construction, which is the same defect `baseline_tokens` avoids by
    not reading assets/tokens.json: the fixture would stop being evidence that
    the contract is the one the token file states.
    """
    return hashlib.sha256(json.dumps(words, separators=(",", ":")).encode()).hexdigest()


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
            "words_to_avoid": list(BASELINE_WORDS),
            "words_to_avoid_digest": {
                "algorithm": "sha256",
                "sha256": word_list_digest(BASELINE_WORDS),
            },
            "words_to_avoid_scope": "Every line of prose, and the public asset copy.",
            "words_to_avoid_surfaces": {
                "surfaces": [
                    {"kind": "svg_copy", "glob": "assets/*.svg"},
                    {"kind": "markdown_headings", "glob": "README.md"},
                    {
                        "kind": "json_string_field",
                        "glob": "package.json",
                        "field": "description",
                    },
                    {
                        "kind": "markdown_prose",
                        "glob": "**/*.md",
                        "exclude": ["_quarantine/**", "CHANGELOG.md"],
                    },
                ]
            },
        },
        "asset_pairs": {
            "pairs": [],
            "pairs_pending": "No source ships yet.",
        },
    }


# A note that reads as a grant of permission rather than as historical context
# (#265). Deliberately over-broad: a false positive costs one reworded note, a
# false negative ships a documented rule the build does not honour.
_PERMISSION_WORDING = re.compile(
    r"\b(permitted|permissible|allowed|allowable|acceptable|exempt|"
    r"may (?:be )?use[ds]?|you may|is fine|is ok)\b",
    re.IGNORECASE,
)


def _reads_as_a_permission(note: str) -> bool:
    return bool(_PERMISSION_WORDING.search(note))


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


def expect_breaches(
    name: str,
    root: Path,
    expected: int,
    *substrings: str,
    absent: tuple[str, ...] = (),
) -> None:
    """Assert an exact breach count, the messages present, and the messages absent.

    The count is the single-reason guard: a fixture red for two reasons would
    stay red if the check under test were deleted. `absent` is what separates
    two surfaces that read the same file - a banned word in README body prose
    must be reported by the prose surface and NOT by the headings surface.
    """
    result = run_checker(root)
    marker = f"REJECTED: {expected} brand kit breach(es)"
    missing = [item for item in substrings if item not in result.stderr]
    unwanted = [item for item in absent if item in result.stderr]
    check(
        name,
        result.returncode == 1
        and marker in result.stderr
        and not missing
        and not unwanted,
        f"rc={result.returncode} missing={missing!r} unwanted={unwanted!r} "
        f"err={result.stderr.strip()!r}",
    )


def expect_one_breach(name: str, root: Path, *substrings: str) -> None:
    expect_breaches(name, root, 1, *substrings)


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
# The scope boundary. First, on purpose - now on the other side of itself.
# --------------------------------------------------------------------------
def case_markdown_prose_with_a_banned_word_rejected(tmp: Path) -> None:
    """A banned word in markdown BODY prose is refused.

    THIS FIXTURE WAS INVERTED. It read `case_readme_body_prose_passes` and
    asserted that the baseline README's body, which carried `load-bearing` and
    `robust`, PASSED - because the token file declared body prose out of scope
    and the words appeared in working documentation on purpose. The operator
    ruled on 2026-09-06: one voice, one word list, all repositories, every
    single line of prose, the same rules. MrBinnacle/skills#261 carries the
    ruling and the 25-line rewrite it forced.

    It was inverted rather than deleted because the boundary still needs a
    fixture standing on it. A poison control that has never been watched fail is
    not a control, so the flip was demonstrated both ways: red against the
    checker before the markdown_prose surface was read, green after.
    """
    readme = BASELINE_README + "\nThe apostrophe rule here is load-bearing.\n"
    expect_breaches(
        "a banned word in markdown body prose rejected",
        baseline_tree(tmp, readme=readme),
        1,
        "README.md:prose",
        "banned word 'load-bearing'",
    )


def case_readme_heading_rejected(tmp: Path) -> None:
    """A README heading is inside BOTH markdown surfaces, so it reports twice.

    The prose surface reads whole documents and the headings surface reads the
    front page's headings, so this line is a breach on each. Both labels are
    asserted: deleting either check drops the count to one and reddens this.
    """
    readme = BASELINE_README.replace("## Admission method", "## Skills that earn their keep")
    expect_breaches(
        "readme heading with a banned word rejected",
        baseline_tree(tmp, readme=readme),
        2,
        "README.md:headings",
        "README.md:prose",
        "banned word 'earn'",
    )


def case_body_prose_is_reported_as_prose_not_as_a_heading(tmp: Path) -> None:
    """The discriminator between the two markdown surfaces.

    A banned word two lines below a clean heading is one breach, on the prose
    surface. If the headings surface also reported it, the heading scan would be
    reading whole files and its line numbers would be meaningless.
    """
    readme = BASELINE_README + "\n### A clean heading\n\nMore curated notes here.\n"
    expect_breaches(
        "body prose below a clean heading is a prose breach only",
        baseline_tree(tmp, readme=readme),
        1,
        "README.md:prose",
        "banned word 'curated'",
        absent=("README.md:headings",),
    )


def case_prose_line_number_is_the_line_number_in_the_file(tmp: Path) -> None:
    """A breach after a fenced block reports its real line.

    The fence remover for the prose surface blanks fenced lines instead of
    dropping them. Dropping them would shift every later line number by the
    length of the fence and send a reader to the wrong line of a long card.
    """
    readme = BASELINE_README + (
        "\n```bash\necho one\necho two\necho three\n```\n\nMore curated notes here.\n"
    )
    expected_line = readme.splitlines().index("More curated notes here.") + 1
    expect_breaches(
        "a prose breach reports its line number in the file",
        baseline_tree(tmp, readme=readme),
        1,
        "README.md:prose",
        f"at line {expected_line} of the",
    )


def case_fenced_code_is_out_of_both_markdown_surfaces(tmp: Path) -> None:
    """A banned word inside a fence passes: a fence holds code, not prose.

    Cross-review reproduced the false breach on the headings surface: a fenced
    '# earn ...' line read as a heading. The prose surface skips fences for the
    same reason and one more - inside a fence a banned word is often the name of
    a real command, field or file rather than a claim about one.
    """
    readme = BASELINE_README + (
        "\n```bash\n# earn a receipt for every run\necho done\n```\n"
    )
    expect_pass("a banned word in fenced code passes", baseline_tree(tmp, readme=readme))


def case_setext_heading_rejected(tmp: Path) -> None:
    """A setext heading is part of the headings surface, same as ATX.

    Cross-review reproduced the miss: 'Skills that earn their keep' underlined
    with equals signs passed while the same words behind '##' were refused. It
    is now a breach on the prose surface too; both labels are asserted.
    """
    readme = BASELINE_README + "\nSkills that earn their keep\n====\n"
    expect_breaches(
        "setext heading with a banned word rejected",
        baseline_tree(tmp, readme=readme),
        2,
        "README.md:headings",
        "README.md:prose",
        "banned word 'earn'",
    )


# --------------------------------------------------------------------------
# The two exclusions the ruling left standing.
# --------------------------------------------------------------------------
def case_quarantine_document_excluded(tmp: Path) -> None:
    """_quarantine/ holds frozen candidates, so a rule reddening on one would
    demand an edit the repository forbids."""
    root = baseline_tree(tmp)
    candidate = root / "_quarantine" / "a-candidate"
    candidate.mkdir(parents=True)
    (candidate / "SKILL.md").write_text("# Frozen\n\nA robust candidate.\n", encoding="utf-8")
    expect_pass("a banned word inside _quarantine passes", root)


def case_changelog_excluded(tmp: Path) -> None:
    """CHANGELOG.md records what shipped under the wording in force at the time,
    so rewriting an entry would falsify the record the file exists to keep."""
    root = baseline_tree(tmp)
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n- A curated release note.\n", encoding="utf-8"
    )
    expect_pass("a banned word inside CHANGELOG.md passes", root)


def case_exclusion_removing_every_file_refused(tmp: Path) -> None:
    """A surface excluded down to nothing is a check that runs on nothing."""
    tokens = baseline_tokens()
    tokens["copy"]["words_to_avoid_surfaces"]["surfaces"][3]["exclude"] = ["**"]
    expect_refusal(
        "an exclude list that removes every file is refused",
        baseline_tree(tmp, tokens=tokens),
        "removed every one of them",
    )


# --------------------------------------------------------------------------
# The published digest of the word list.
# --------------------------------------------------------------------------
def case_stale_word_list_digest_refused(tmp: Path) -> None:
    """The drift contract MrBinnacle/skill-harness#462 vendors this list against.

    A digest that no longer names the list on disk would have the sibling compare
    against a list that does not exist, so the disagreement is a refusal here
    rather than a breach: the token file's own inputs are wrong.
    """
    tokens = baseline_tokens()
    tokens["copy"]["words_to_avoid_digest"]["sha256"] = "0" * 64
    expect_refusal(
        "a published digest that disagrees with the list is refused",
        baseline_tree(tmp, tokens=tokens),
        "was edited without re-recording the digest",
    )


def case_missing_word_list_digest_refused(tmp: Path) -> None:
    tokens = baseline_tokens()
    del tokens["copy"]["words_to_avoid_digest"]
    expect_refusal(
        "a token file publishing no digest is refused",
        baseline_tree(tmp, tokens=tokens),
        "copy.words_to_avoid_digest is missing",
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
    """Adding a word is a data edit. Nothing in the checker names any word.

    The digest is re-recorded with it. That is the contract working, not a
    workaround: editing the list without re-recording is what
    `case_stale_word_list_digest_refused` proves is refused.
    """
    tokens = baseline_tokens()
    tokens["copy"]["words_to_avoid"].append("inventory")
    tokens["copy"]["words_to_avoid_digest"]["sha256"] = word_list_digest(
        tokens["copy"]["words_to_avoid"]
    )
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


def case_live_published_digest_matches_the_live_list() -> None:
    """The value MrBinnacle/skill-harness#462 vendors against, checked at source."""
    tokens = json.loads((REPO_ROOT / "assets" / "tokens.json").read_text(encoding="utf-8"))
    copy_block = tokens["copy"]
    published = copy_block["words_to_avoid_digest"]["sha256"]
    computed = word_list_digest(copy_block["words_to_avoid"])
    check(
        "the published digest names the shipped word list",
        published == computed,
        f"published {published}, computed {computed}",
    )


def case_live_prose_surface_reads_the_whole_tree() -> None:
    """Non-vacuity for the widest surface, against what ships.

    The prose surface resolves to one label per in-scope document. A glob that
    had stopped matching, or an exclude list that had widened, would leave the
    ruling enforced over a handful of files while the PASS line still read PASS.
    """
    tokens = json.loads((REPO_ROOT / "assets" / "tokens.json").read_text(encoding="utf-8"))
    spec = next(
        surface
        for surface in tokens["copy"]["words_to_avoid_surfaces"]["surfaces"]
        if surface["kind"] == "markdown_prose"
    )
    resolved = kit.surface_copy(REPO_ROOT, spec)
    tracked = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    ).stdout.split()
    in_scope = [
        name
        for name in tracked
        if not name.startswith("_quarantine/") and name != "CHANGELOG.md"
    ]
    check(
        "the prose surface resolves to every in-scope tracked document",
        len(resolved) == len(in_scope) and len(in_scope) > 100,
        f"surface resolved {len(resolved)} document(s), git tracks {len(in_scope)} in scope",
    )
    check(
        "the prose surface excludes the two documents the ruling left out",
        not any(
            label.startswith("_quarantine/") or label.startswith("CHANGELOG.md")
            for label, _ in resolved
        ),
        "an excluded document reached the prose surface",
    )


def case_live_notes_grant_no_permission_no_checker_implements() -> None:
    """#265: a note may not grant a permission that no checker enforces.

    `copy.words_to_avoid_notes` used to say `robust` was "Permitted only when the
    failure it resists is named in the same sentence" and `production-ready` was
    "Permitted only with proof attached". Neither checker read the object at all,
    so both words were banned flat. A contributor who read the note and wrote the
    permitted sentence was refused by a build that the documentation said would
    accept it, and then had no way to tell which of the other documented rules
    were real.

    The binding is deterministic: a note whose text reads as a grant is allowed
    only once a checker reads `words_to_avoid_notes` AND names that word. Both
    halves are greppable, so neither side can drift without this failing.

    Keys beginning with `$` are metadata by the convention `words_to_avoid_digest`
    already uses, and are not permissions.
    """
    tokens = json.loads((REPO_ROOT / "assets" / "tokens.json").read_text(encoding="utf-8"))
    notes = tokens["copy"].get("words_to_avoid_notes", {})
    checkers = {
        name: (REPO_ROOT / "scripts" / name).read_text(encoding="utf-8")
        for name in ("validate_brand_kit.py", "validate_vale_style.py")
    }

    granting = sorted(
        word
        for word, text in notes.items()
        if not word.startswith("$") and _reads_as_a_permission(text)
    )
    unenforced = [
        word
        for word in granting
        if not any(
            "words_to_avoid_notes" in source and word in source for source in checkers.values()
        )
    ]
    check(
        "no note grants a permission that no checker implements",
        not unenforced,
        f"{unenforced} read as permissions; no checker reads words_to_avoid_notes and names them",
    )

    # Non-vacuity: the detector must fire on the wording that was actually removed.
    check(
        "the permission detector fires on the removed wording",
        _reads_as_a_permission("Permitted only with proof attached.")
        and _reads_as_a_permission(
            "Permitted only when the failure it resists is named in the same sentence."
        ),
        "the detector would pass any note, including a grant",
    )
    check(
        "the permission detector does not fire on a historical note",
        not _reads_as_a_permission(notes["earn"]),
        "a historical note was misread as a grant",
    )


def case_workflow_runs_the_checker() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for fragment in (
        "scripts/test_validate_brand_kit.py",
        "scripts/validate_brand_kit.py",
        "control-brand-copy",
        "control-brand-prose",
        "control-brand-hash",
        "control-brand-hex",
    ):
        check(f"tests.yml carries {fragment}", fragment in workflow, str(WORKFLOW))


def main() -> None:
    in_tempdir = (
        case_markdown_prose_with_a_banned_word_rejected,
        case_readme_heading_rejected,
        case_body_prose_is_reported_as_prose_not_as_a_heading,
        case_prose_line_number_is_the_line_number_in_the_file,
        case_fenced_code_is_out_of_both_markdown_surfaces,
        case_setext_heading_rejected,
        case_quarantine_document_excluded,
        case_changelog_excluded,
        case_exclusion_removing_every_file_refused,
        case_stale_word_list_digest_refused,
        case_missing_word_list_digest_refused,
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
    case_live_published_digest_matches_the_live_list()
    case_live_prose_surface_reads_the_whole_tree()
    case_live_svg_scanner_sees_real_copy()
    case_live_banners_carry_no_instrument_palette()
    case_live_light_neutrals_are_declared()
    case_live_notes_grant_no_permission_no_checker_implements()
    case_workflow_runs_the_checker()

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: brand-kit checker verified across {len(in_tempdir)} temporary "
        "tree(s) plus the live tree; every breach case asserts its own message and "
        "an exact breach count, the scope boundary is pinned by the fixture that "
        "was inverted when it moved, both exclusions have a fixture, the published "
        "word-list digest is checked against the shipped list, and the SVG and "
        "prose scanners are proven non-vacuous against what ships."
    )


if __name__ == "__main__":
    main()
