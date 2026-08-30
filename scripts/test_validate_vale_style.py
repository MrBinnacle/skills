#!/usr/bin/env python3
"""Suite for validate_vale_style.py.

WHAT THIS SUITE HAS TO PROVE, AND WHY THE ORDINARY RUN CANNOT

    Two of the three checks guard an ABSENCE: no digest mismatch, no scope
    widening. A validator that had gone blind - a digest loop over zero files, a
    scope check that never found a section - reports exactly what a repository in
    good order reports. So every check here is proven by making it FAIL on a
    single mutation, and every refusal case is proven by starving the check of
    its own input.

THE SCOPE BOUNDARY IS PINNED FIRST, ON PURPOSE

    `case_tree_wide_local_binding_rejected` runs before anything else, for the
    same reason `test_validate_brand_kit.py` puts its README-body fixture first.
    `assets/tokens.json` states that the marketing words appear in working
    documentation deliberately, and the cheapest way to make this "more
    thorough" is to bind the Local style to `[*.md]`. That fixture goes red the
    moment anyone does.

THE MARKETING RULE FIRES ZERO TIMES ON THE LIVE TREE, SO ITS PROOF LIVES HERE

    Measured on the branch that added it: `Local.Marketing-copy` reports no
    finding against README headings, which agrees with
    `copy.words_to_avoid_notes.earn` - the retired tagline survived only on a
    raster, not in heading text. A rule with no live hit is unproven by the
    ordinary run, so `case_generated_rule_matches_every_banned_word` asserts the
    rendered pattern set against the token list directly.

Every case builds a real temporary tree and calls the real entrypoint. No poison
fixture is committed: a violating file under `styles/` would sit inside the
guarded set and turn the real run permanently red.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts" / "validate_vale_style.py"

FAILURES: list[str] = []


def fail(case: str, detail: str) -> None:
    FAILURES.append(case)
    print(f"  FAIL {case}: {detail}")


def run(root: Path) -> subprocess.CompletedProcess[str]:
    """Run the checker COPY inside `root`, so the tree under test is the one read.

    The checker resolves its own repository root from `__file__`. Invoking the
    live script with `cwd=root` would therefore read the live tree and ignore
    every mutation - a control that cannot fail. Running the copy is what binds
    the fixture to the assertion.
    """
    copied = root / "scripts" / "validate_vale_style.py"
    if not copied.is_file():
        raise AssertionError(f"no checker copy in {root}; baseline_tree was not called")
    return subprocess.run(
        [sys.executable, str(copied)],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def baseline_tree(root: Path) -> None:
    """A conforming copy of the live configuration."""
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(CHECKER, root / "scripts" / "validate_vale_style.py")
    shutil.copy2(REPO_ROOT / "assets" / "tokens.json", root / "assets" / "tokens.json")
    shutil.copytree(REPO_ROOT / "styles", root / "styles")
    shutil.copy2(REPO_ROOT / ".vale.ini", root / ".vale.ini")


def expect_pass(case: str, root: Path) -> None:
    result = run(root)
    if result.returncode != 0:
        fail(case, f"expected exit 0, got {result.returncode}: {result.stderr.strip()}")


def expect_failure(case: str, root: Path, needle: str, code: int = 1) -> None:
    result = run(root)
    if result.returncode != code:
        fail(case, f"expected exit {code}, got {result.returncode}: {result.stdout}{result.stderr}")
        return
    if needle.lower() not in result.stderr.lower():
        fail(case, f"message did not name {needle!r}; got: {result.stderr.strip()}")


# --------------------------------------------------------------------------
# Scope boundary - first, deliberately.
# --------------------------------------------------------------------------


def case_tree_wide_local_binding_rejected(root: Path) -> None:
    """Binding the marketing list to every markdown file is refused."""
    baseline_tree(root)
    ini = root / ".vale.ini"
    ini.write_text(
        ini.read_text(encoding="utf-8").replace(
            "[*.md]\nBasedOnStyles = Taste",
            "[*.md]\nBasedOnStyles = Taste, Local",
        ),
        encoding="utf-8",
    )
    expect_failure(
        "case_tree_wide_local_binding_rejected", root, "widening this scope is"
    )


def case_readme_binding_without_heading_scope_rejected(root: Path) -> None:
    """README.md is declared headings-only, so the rule must scope itself."""
    baseline_tree(root)
    rule = root / "styles" / "Local" / "Marketing-copy.yml"
    rule.write_text(
        rule.read_text(encoding="utf-8").replace("scope: heading\n", ""),
        encoding="utf-8",
    )
    # The rule no longer regenerates identically either; assert the scope message
    # is present among the reported problems.
    result = run(root)
    if result.returncode != 1:
        fail(
            "case_readme_binding_without_heading_scope_rejected",
            f"expected exit 1, got {result.returncode}",
        )
        return
    if "scope: heading" not in result.stderr:
        fail(
            "case_readme_binding_without_heading_scope_rejected",
            f"did not name the missing scope; got: {result.stderr.strip()}",
        )


# --------------------------------------------------------------------------
# Vendor integrity.
# --------------------------------------------------------------------------


def case_baseline_passes(root: Path) -> None:
    baseline_tree(root)
    expect_pass("case_baseline_passes", root)


def case_one_byte_edit_to_a_vendored_rule_fails(root: Path) -> None:
    """The poison control the ticket asks for: a single byte breaks the digest."""
    baseline_tree(root)
    victim = root / "styles" / "Taste" / "Voice.yml"
    victim.write_bytes(victim.read_bytes() + b" ")
    expect_failure(
        "case_one_byte_edit_to_a_vendored_rule_fails",
        root,
        "does not match its recorded digest",
    )


def case_unrecorded_vendored_rule_fails(root: Path) -> None:
    """A rule added without a digest is outside the check, so it is refused."""
    baseline_tree(root)
    (root / "styles" / "Taste" / "Smuggled.yml").write_text(
        "extends: existence\nmessage: 'x'\nlevel: warning\ntokens:\n  - 'x'\n",
        encoding="utf-8",
    )
    expect_failure(
        "case_unrecorded_vendored_rule_fails", root, "not recorded in STYLE_SOURCE.json"
    )


def case_missing_vendored_rule_fails(root: Path) -> None:
    baseline_tree(root)
    (root / "styles" / "Taste" / "Register.yml").unlink()
    expect_failure("case_missing_vendored_rule_fails", root, "recorded but missing")


def case_empty_manifest_refused(root: Path) -> None:
    """A digest check over zero files passes trivially, so it refuses instead."""
    baseline_tree(root)
    manifest = root / "styles" / "Taste" / "STYLE_SOURCE.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["files"] = {}
    manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")
    expect_failure("case_empty_manifest_refused", root, "records no files", code=2)


# --------------------------------------------------------------------------
# Generated-rule agreement.
# --------------------------------------------------------------------------


def case_token_change_without_regeneration_fails(root: Path) -> None:
    """Editing the word list without regenerating is the drift this catches."""
    baseline_tree(root)
    tokens = root / "assets" / "tokens.json"
    data = json.loads(tokens.read_text(encoding="utf-8"))
    data["copy"]["words_to_avoid"].append("frictionless")
    tokens.write_text(json.dumps(data, indent=2), encoding="utf-8")
    expect_failure(
        "case_token_change_without_regeneration_fails",
        root,
        "disagrees with",
    )


def case_hand_edited_generated_rule_fails(root: Path) -> None:
    """Silencing a word by editing the generated file is caught."""
    baseline_tree(root)
    rule = root / "styles" / "Local" / "Marketing-copy.yml"
    rule.write_text(
        rule.read_text(encoding="utf-8").replace("  - '\\bpowerful\\b'\n", ""),
        encoding="utf-8",
    )
    expect_failure("case_hand_edited_generated_rule_fails", root, "disagrees with")


def case_empty_ban_list_refused(root: Path) -> None:
    """An empty list would ban nothing and pass every surface."""
    baseline_tree(root)
    tokens = root / "assets" / "tokens.json"
    data = json.loads(tokens.read_text(encoding="utf-8"))
    data["copy"]["words_to_avoid"] = []
    tokens.write_text(json.dumps(data, indent=2), encoding="utf-8")
    expect_failure("case_empty_ban_list_refused", root, "vacuous", code=2)


def case_no_declared_surface_refused(root: Path) -> None:
    baseline_tree(root)
    tokens = root / "assets" / "tokens.json"
    data = json.loads(tokens.read_text(encoding="utf-8"))
    data["copy"]["words_to_avoid_surfaces"]["surfaces"] = []
    tokens.write_text(json.dumps(data, indent=2), encoding="utf-8")
    expect_failure("case_no_declared_surface_refused", root, "refuses nothing", code=2)


def case_local_bound_to_nothing_refused(root: Path) -> None:
    """A rule no section enables reports on nothing."""
    baseline_tree(root)
    ini = root / ".vale.ini"
    ini.write_text(
        ini.read_text(encoding="utf-8").replace("BasedOnStyles = Taste, Local", "BasedOnStyles = Taste"),
        encoding="utf-8",
    )
    expect_failure(
        "case_local_bound_to_nothing_refused", root, "bound to nothing", code=2
    )


# --------------------------------------------------------------------------
# Live-tree assertions - non-vacuity against what actually ships.
# --------------------------------------------------------------------------


def case_live_tree_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        fail("case_live_tree_passes", f"exit {result.returncode}: {result.stderr.strip()}")


def case_generated_rule_matches_every_banned_word() -> None:
    """Non-vacuity: the rendered rule names each word, since it never fires live."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import validate_vale_style as checker  # noqa: PLC0415

    words = checker.banned_words()
    if not words:
        fail("case_generated_rule_matches_every_banned_word", "no words to check")
        return
    rendered = (REPO_ROOT / "styles" / "Local" / "Marketing-copy.yml").read_text(
        encoding="utf-8"
    )
    missing = [w for w in words if f"\\b{w}\\b".replace("-", "\\-") not in rendered]
    if missing:
        fail(
            "case_generated_rule_matches_every_banned_word",
            f"rendered rule omits {missing}",
        )


def case_vendored_digests_match_the_named_source() -> None:
    """The digests describe the files that are actually here, not a stale record."""
    manifest = json.loads(
        (REPO_ROOT / "styles" / "Taste" / "STYLE_SOURCE.json").read_text(encoding="utf-8")
    )
    for name, expected in manifest["files"].items():
        actual = hashlib.sha256(
            (REPO_ROOT / "styles" / "Taste" / name).read_bytes()
        ).hexdigest()
        if actual != expected:
            fail(
                "case_vendored_digests_match_the_named_source",
                f"{name}: recorded {expected[:12]}, found {actual[:12]}",
            )


def case_styles_are_pinned_to_lf() -> None:
    """A hash over a text file must not depend on the checkout platform.

    Without an eol rule Git hands Windows CRLF and Linux LF for the same commit,
    so every recorded digest mismatches on one runner and not the other. This
    failed exactly that way on PR #197 before .gitattributes existed, and the
    failure is invisible to anyone developing on Linux - which is why it is
    asserted here rather than left to the next Windows run to rediscover.
    """
    attributes = REPO_ROOT / ".gitattributes"
    if not attributes.is_file():
        fail("case_styles_are_pinned_to_lf", ".gitattributes is missing")
        return
    text = attributes.read_text(encoding="utf-8")
    if "styles/** text eol=lf" not in text:
        fail(
            "case_styles_are_pinned_to_lf",
            ".gitattributes does not pin styles/ to LF, so the recorded digests "
            "describe bytes that differ by platform",
        )
        return
    for path in sorted((REPO_ROOT / "styles").rglob("*.yml")):
        if b"\r\n" in path.read_bytes():
            fail(
                "case_styles_are_pinned_to_lf",
                f"{path.name} carries CRLF in the working tree; its digest will "
                "not reproduce on a LF checkout",
            )


def case_workflow_runs_the_checker() -> None:
    """A checker no workflow calls is not a gate."""
    workflows = list((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
    if not any(
        "validate_vale_style.py" in wf.read_text(encoding="utf-8") for wf in workflows
    ):
        fail(
            "case_workflow_runs_the_checker",
            "no workflow invokes scripts/validate_vale_style.py",
        )


def main() -> None:
    in_tempdir = (
        case_tree_wide_local_binding_rejected,
        case_readme_binding_without_heading_scope_rejected,
        case_baseline_passes,
        case_one_byte_edit_to_a_vendored_rule_fails,
        case_unrecorded_vendored_rule_fails,
        case_missing_vendored_rule_fails,
        case_empty_manifest_refused,
        case_token_change_without_regeneration_fails,
        case_hand_edited_generated_rule_fails,
        case_empty_ban_list_refused,
        case_no_declared_surface_refused,
        case_local_bound_to_nothing_refused,
    )
    for case in in_tempdir:
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))

    case_live_tree_passes()
    case_styles_are_pinned_to_lf()
    case_generated_rule_matches_every_banned_word()
    case_vendored_digests_match_the_named_source()
    case_workflow_runs_the_checker()

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: vale-style checker verified across {len(in_tempdir)} temporary tree(s) "
        "plus the live tree; the scope boundary is pinned by its own fixture, the "
        "digest check is proven by a one-byte edit, and the generated rule is proven "
        "non-vacuous against the token list it renders from."
    )


if __name__ == "__main__":
    main()
