#!/usr/bin/env python3
"""Suite for S498 / issue #334 currency of PRODUCT.md, BRAND.md, DESIGN.md.

A currency audit (a separate research repository, docs/audit/product-definitions-currency-S498.md)
checked every factual line of these three files against origin/main and marked
rows STALE where a citation, attribution, line number or tense had drifted.
Issue #334 corrects those rows and leaves INTENT lines alone: the Users
hypothesis, the Positioning narrative, the Product Purpose claim, the Brand
Commitments and the Product Principles wait on the operator.

Each case reads the live file rather than a fixture, because the file is the
artifact under review. Citation cases resolve FILE:LINE against the file that
actually sits at that path, so a corrected number that points at the wrong text
fails the suite. Intent cases pin the sentences that must survive every fix, so
a green suite cannot mean "the STALE rows were removed by deleting the product
record with them".

Two limits. The suite is pinned to line numbers, so any edit above a cited line
in AGENTS.md, CATALOG.md, RETIRED.md or BRAND.md turns it red although the three
product files are unchanged. It is evidence for the issue #334 pull request, run
on demand, and is deliberately left out of CI. And the intent cases assert that
named phrases are present; they do not show that an INTENT section is
unchanged. A diff against main is the evidence for that.

Run: python scripts/test_product_definition_currency.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCT = REPO_ROOT / "PRODUCT.md"
BRAND = REPO_ROOT / "BRAND.md"
DESIGN = REPO_ROOT / "DESIGN.md"

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    """File text with runs of whitespace collapsed, for substring claims across wraps."""
    return re.sub(r"\s+", " ", _read(path))


def _line(path: Path, number: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if number < 1 or number > len(lines):
        raise AssertionError(f"{path.name}:{number} out of range (file has {len(lines)} lines)")
    return lines[number - 1]


def _lines(path: Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if start < 1 or end > len(lines) or start > end:
        raise AssertionError(f"{path.name}:{start}-{end} out of range")
    return "\n".join(lines[start - 1 : end])


def _resolve(cited: str, needle: str, label: str) -> None:
    """cited is 'AGENTS.md:440' or 'RETIRED.md:93-102'. needle must appear there."""
    if ":" not in cited:
        check(label, False, f"citation has no line number: {cited}")
        return
    name, _, span = cited.partition(":")
    path = REPO_ROOT / name
    if not path.is_file():
        check(label, False, f"cited file missing: {name}")
        return
    if "-" in span:
        start_s, _, end_s = span.partition("-")
        start, end = int(start_s), int(end_s)
        try:
            text = _lines(path, start, end)
        except AssertionError as exc:
            check(label, False, str(exc))
            return
    else:
        number = int(span)
        try:
            text = _line(path, number)
        except AssertionError as exc:
            check(label, False, str(exc))
            return
    check(label, needle in text, f"{cited} does not contain {needle!r}; line reads: {text[:120]!r}")


# ==========================================================================
# Criterion 1 — every STALE row corrected
# ==========================================================================
def case_product_no_counts_claim_narrowed() -> None:
    """PRODUCT.md no longer claims the file states NO counts."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md self-contradiction removed",
        "This file states NO counts" not in text,
        "PRODUCT.md still claims it states NO counts while carrying fixed artifact counts",
    )
    check(
        "PRODUCT.md still gives a derivation command for tallies",
        "git ls-files" in text and "_quarantine" in text,
        "the derivation-command guidance was deleted with the stale claim",
    )


def case_product_agents_citation_points_at_tally_rule() -> None:
    """The owner ruling against restating tallies lives at AGENTS.md:440, not :315."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites AGENTS.md:315 for the tally ruling",
        "AGENTS.md:315" not in text,
        "PRODUCT.md still points the tally ruling at AGENTS.md:315",
    )
    check(
        "PRODUCT.md cites AGENTS.md:440 for the tally ruling",
        "AGENTS.md:440" in text,
        "PRODUCT.md does not cite AGENTS.md:440",
    )
    _resolve("AGENTS.md:440", "The page states no tally", "AGENTS.md:440 holds the tally ruling")


def case_product_readme_honest_ceilings_attribution_removed() -> None:
    """README has no honest-ceilings section; the rule is PRODUCT.md's own."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer attributes the adoption-metrics rule to README",
        "README.md's honest ceilings" not in text and "README.md's\n  honest ceilings" not in text,
        "PRODUCT.md still attributes an honest-ceilings section to README.md",
    )
    check(
        "PRODUCT.md still states the no-adoption-metrics rule",
        "No verified adoption metrics" in text,
        "the no-adoption-metrics rule itself was deleted",
    )
    readme = _read(REPO_ROOT / "README.md")
    check(
        "README.md still has no honest-ceilings section (audit claim holds)",
        "honest ceiling" not in readme.lower(),
        "README gained an honest-ceilings section; re-audit before relying on this case",
    )


def case_product_coverage_quote_cites_catalog() -> None:
    """The anti-browsing quote lives at CATALOG.md:31, not README.md:226-230."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites README.md:226-230",
        "README.md:226-230" not in text,
        "PRODUCT.md still points the coverage quote at a non-existent README span",
    )
    check(
        "PRODUCT.md cites CATALOG.md:31 for the coverage quote",
        "CATALOG.md:31" in text,
        "PRODUCT.md does not cite CATALOG.md:31",
    )
    _resolve(
        "CATALOG.md:31",
        "not intended to maximize coverage",
        "CATALOG.md:31 holds the coverage sentence",
    )


def case_product_useful_enough_quote_cites_design_variants() -> None:
    """README.md:14 no longer carries the first-person collection line."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites README.md:14 for the useful-enough line",
        "README.md:14" not in text,
        "PRODUCT.md still points the first-person line at README.md:14",
    )
    check(
        "PRODUCT.md cites the design variants that still hold the line",
        "docs/design/variants/front-page/variant-1.md" in text,
        "PRODUCT.md does not cite the design-variant file that holds the retired line",
    )
    _resolve(
        "docs/design/variants/front-page/variant-1.md:20",
        "useful enough to keep developing",
        "variant-1.md:20 holds the retired first-person line",
    )
    readme = _read(REPO_ROOT / "README.md")
    check(
        "README.md:10 states any Claude Code user can hit these failures",
        "Any Claude Code user can hit these failures" in readme,
        "README.md:10 no longer carries the current public line",
    )


def case_product_brand_not_market_citation_moved() -> None:
    """The not-with-a-market line is at BRAND.md:75-76 at PR head, not BRAND.md:72."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites BRAND.md:72",
        "BRAND.md:72" not in text,
        "PRODUCT.md still points the not-with-a-market line at BRAND.md:72",
    )
    check(
        "PRODUCT.md cites BRAND.md:75-76",
        "BRAND.md:75-76" in text,
        "PRODUCT.md does not cite BRAND.md:75-76",
    )
    _resolve("BRAND.md:75-76", "not with a market", "BRAND.md:75-76 holds the not-with-a-market line")


def case_product_breadth_cost_quote_not_in_readme() -> None:
    """The breadth-cost line is not in README; it lives in a design variant."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites README.md:87-88 for the breadth-cost line",
        "README.md:87-88" not in text,
        "PRODUCT.md still points the breadth-cost line at README.md:87-88",
    )
    check(
        "PRODUCT.md cites the design variant that holds the breadth-cost line",
        "variant-5.md" in text,
        "PRODUCT.md does not cite variant-5.md for the breadth-cost line",
    )
    _resolve(
        "docs/design/variants/front-page/variant-5.md:38",
        "breadth you do not use is still paid for",
        "variant-5.md:38 holds the breadth-cost line",
    )
    readme = _read(REPO_ROOT / "README.md")
    check(
        "README.md does not carry the breadth-cost line (audit claim holds)",
        "breadth you do not use" not in readme,
        "README gained the breadth-cost line; re-audit before relying on this case",
    )


def case_product_purpose_allows_designed_cards() -> None:
    """README:10 records im-down and im-up as designed, not incident-born."""
    product = _read(PRODUCT)
    purpose = product[product.find("## Product Purpose") : product.find("## Positioning")]
    check(
        "PRODUCT.md purpose no longer says every card carries a dated origin incident",
        "each carrying a dated origin incident" not in purpose,
        "Product Purpose still claims every card is incident-born",
    )
    check(
        "Product Purpose still states the publish-for-checking claim",
        "published so the record can be checked" in purpose,
        "Product Purpose lost the publish-for-checking claim",
    )
    readme = _read(REPO_ROOT / "README.md")
    check(
        "README:10 records designed cards (im-down, im-up)",
        "`im-down` and `im-up`, were designed" in readme
        or ("im-down` and `im-up`" in readme and "designed" in readme),
        "README:10 no longer states two cards were designed",
    )


def case_product_publication_not_validation_readme_claim_removed() -> None:
    """Only BRAND.md carries the phrase; README does not."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer claims README states Publication is not validation",
        "Stated in both BRAND.md and README.md" not in text,
        "PRODUCT.md still attributes the phrase to both BRAND.md and README.md",
    )
    check(
        "PRODUCT.md still states Publication is not validation",
        "Publication is not validation" in text,
        "the Publication-is-not-validation claim itself was deleted",
    )
    readme = _read(REPO_ROOT / "README.md")
    check(
        "README.md still has no Publication-is-not-validation phrase (audit claim holds)",
        "Publication is not validation" not in readme,
        "README gained the phrase; re-audit before relying on this case",
    )


def case_product_retired_line_refs_corrected() -> None:
    """Positioning quotes cite RETIRED.md:3 and :26, not :1, 18-20."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites RETIRED.md:1, 18-20",
        "RETIRED.md:1, 18-20" not in text,
        "PRODUCT.md still points the positioning quotes at RETIRED.md:1, 18-20",
    )
    check(
        "PRODUCT.md cites RETIRED.md:3, 26",
        "RETIRED.md:3, 26" in text,
        "PRODUCT.md does not cite RETIRED.md:3, 26",
    )
    _resolve("RETIRED.md:3", "Most collections only ever grow", "RETIRED.md:3 holds the grow quote")
    _resolve(
        "RETIRED.md:26",
        "Turning away your own work costs something",
        "RETIRED.md:26 holds the cost quote",
    )


def case_product_screened_out_quote_current() -> None:
    """The July 2026 screen quote lives at RETIRED.md:93-107 with current wording."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites RETIRED.md:48-78",
        "RETIRED.md:48-78" not in text,
        "PRODUCT.md still points the screened-out quote at RETIRED.md:48-78",
    )
    check(
        "PRODUCT.md cites RETIRED.md:93-107",
        "RETIRED.md:93-107" in text,
        "PRODUCT.md does not cite RETIRED.md:93-107",
    )
    check(
        "PRODUCT.md quote matches current RETIRED wording",
        "All four returned three passes out of three" in text,
        "PRODUCT.md still quotes the old 'hit the ceiling: three passes out of three' wording",
    )
    _resolve(
        "RETIRED.md:93-107",
        "All four returned three passes out of three",
        "RETIRED.md:93-107 holds the current screen wording",
    )
    _resolve(
        "RETIRED.md:93-107",
        "personally convinced were valuable",
        "RETIRED.md:93-107 holds the last part of the screen quote",
    )


def case_product_distribution_matches_adr_0002() -> None:
    """Delivery is a version-bump merge, not every merge to main (ADR 0002)."""
    flat = _flat(PRODUCT)
    # The stale sentence wrote `main` in backticks; match it with them removed.
    check(
        "PRODUCT.md no longer claims a merge to main changes what installs",
        "a merge to main changes what installs" not in flat.replace("`", ""),
        "PRODUCT.md still states the pre-ADR-0002 delivery model",
    )
    check(
        "PRODUCT.md names ADR 0002 or states version-bump delivery",
        "ADR 0002" in flat or "version bump" in flat,
        "PRODUCT.md does not state the ADR 0002 delivery model",
    )
    adr = _flat(REPO_ROOT / "docs" / "adr" / "0002-a-release-is-a-delivery-event.md")
    check(
        "ADR 0002 still states delivery on version-bump merge",
        "version bump merges to main" in adr or "version bump merges to `main`" in adr,
        "ADR 0002 no longer states the delivery model PRODUCT.md must match",
    )


def case_product_provenance_categories_citation_corrected() -> None:
    """OBSERVED/DESIGNED/DISTILLED are not stated on README:120."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer cites README.md:120 for the origin categories",
        "README.md:120" not in text,
        "PRODUCT.md still points the origin-category claim at README.md:120",
    )
    check(
        "PRODUCT.md cites CATALOG.md:158-160 and AGENTS.md:435-436 for the origin categories",
        "CATALOG.md:158-160" in text and "AGENTS.md:435-436" in text and "OBSERVED" in text,
        "PRODUCT.md does not cite the live definitions of OBSERVED/DESIGNED/DISTILLED",
    )
    check(
        "PRODUCT.md cites CATALOG.md:151-152 for the two separate axes",
        "CATALOG.md:151-152" in text,
        "PRODUCT.md does not cite CATALOG.md:151-152",
    )
    _resolve(
        "CATALOG.md:158-160",
        "OBSERVED",
        "CATALOG.md:158-160 holds the origin-category table",
    )
    _resolve(
        "AGENTS.md:435-436",
        "OBSERVED",
        "AGENTS.md:435-436 holds the origin vocabulary",
    )
    _resolve(
        "CATALOG.md:151-152",
        "two separate axes",
        "CATALOG.md:151-152 holds the two-axes sentence",
    )
    readme = _read(REPO_ROOT / "README.md")
    check(
        "README.md does not state OBSERVED/DESIGNED/DISTILLED (audit claim holds)",
        "OBSERVED" not in readme and "DESIGNED" not in readme and "DISTILLED" not in readme,
        "README gained origin-category vocabulary; re-audit before relying on this case",
    )


def case_product_public_project_page_not_undecided() -> None:
    """site/index.html deploys; the existence question is no longer open."""
    text = _read(PRODUCT)
    undecided = text[text.find("Undecided product facts") :]
    check(
        "PRODUCT.md undecided list no longer lists the public project page as undecided",
        "Whether a public project page should exist" not in undecided.split("## ")[0],
        "PRODUCT.md still lists the public project page under undecided product facts",
    )
    site = REPO_ROOT / "site" / "index.html"
    check(
        "site/index.html exists on disk",
        site.is_file(),
        "site/index.html is missing; the audit's STALE row would be wrong",
    )


def case_product_social_preview_precedent_not_live() -> None:
    """The retired-tagline precedent closed on 2026-09-06; it is historical."""
    text = _read(PRODUCT)
    check(
        "PRODUCT.md no longer calls the retired-tagline precedent live",
        "A live cautionary precedent" not in text,
        "PRODUCT.md still calls the closed social-preview precedent live",
    )
    tokens = _read(REPO_ROOT / "assets" / "tokens.json")
    check(
        "tokens.json closed_gaps records the social-preview raster closure",
        "social_preview_raster_is_unreadable" in tokens and "2026-09-06" in tokens,
        "tokens.json no longer records the 2026-09-06 social-preview closure",
    )


def case_brand_publication_not_validation_not_readme() -> None:
    """BRAND.md must not attribute the phrase to the README."""
    text = _read(BRAND)
    check(
        "BRAND.md no longer says the phrase is in the README's own words",
        "in the README's own words" not in text,
        "BRAND.md still attributes Publication-is-not-validation to the README",
    )
    check(
        "BRAND.md still states what it declines to claim",
        "Publication is not validation" in text,
        "BRAND.md lost the Publication-is-not-validation claim",
    )


def case_brand_project_page_decision_closed() -> None:
    """BRAND.md open decisions no longer list the public project page as open."""
    text = _read(BRAND)
    open_section = text[text.find("## Open decisions") :]
    check(
        "BRAND.md open decisions no longer list the public project page",
        "Whether a public project page should exist" not in open_section,
        "BRAND.md still lists the public project page under open decisions",
    )
    check(
        "site/index.html exists (the open decision closed on the repo)",
        (REPO_ROOT / "site" / "index.html").is_file(),
        "site/index.html is missing",
    )


def case_design_scoreboard_extraction_citation_current() -> None:
    """Text-node extraction lives at scripts/validate_scoreboard.py:450-452, not :121-126."""
    text = _read(DESIGN)
    check(
        "DESIGN.md no longer cites validate_scoreboard.py:121-126",
        "validate_scoreboard.py:121-126" not in text,
        "DESIGN.md still points text extraction at validate_scoreboard.py:121-126",
    )
    check(
        "DESIGN.md cites validate_scoreboard.py around 450-452",
        "validate_scoreboard.py:450-452" in text or "validate_scoreboard.py:450" in text,
        "DESIGN.md does not cite the live extraction lines",
    )
    script_lines = (REPO_ROOT / "scripts" / "validate_scoreboard.py").read_text(
        encoding="utf-8"
    ).splitlines()
    found = False
    for number in range(448, 456):
        if number <= len(script_lines) and "re.findall" in script_lines[number - 1]:
            found = True
            break
    check(
        "scripts/validate_scoreboard.py:448-455 actually extracts <text> nodes",
        found,
        "no <text> findall on scripts/validate_scoreboard.py:448-455; re-dereference before citing",
    )


def case_design_social_preview_check_is_brand_kit_not_proposal() -> None:
    """validate_brand_kit.py already scans assets/*.svg including social-preview.svg."""
    text = _read(DESIGN)
    check(
        "DESIGN.md names validate_brand_kit.py for the social-preview SVG check",
        "validate_brand_kit.py" in text and "social-preview" in text,
        "DESIGN.md does not record that validate_brand_kit.py covers social-preview.svg",
    )
    stale_proposal = (
        "Point the same extraction at\n`social-preview.svg`" in text
        or "Point the same extraction at `social-preview.svg`" in text
    )
    check(
        "DESIGN.md no longer reads as a proposal to point extraction at social-preview.svg",
        not stale_proposal,
        "DESIGN.md still proposes the social-preview extraction that already ships",
    )
    tokens = _read(REPO_ROOT / "assets" / "tokens.json")
    check(
        "tokens.json words_to_avoid_surfaces includes assets/*.svg",
        '"glob": "assets/*.svg"' in tokens,
        "tokens.json no longer declares assets/*.svg as a banned-copy surface",
    )


# ==========================================================================
# Criterion 2 — no INTENT line changed
# ==========================================================================
def case_intent_users_hypothesis_preserved() -> None:
    text = _read(PRODUCT)
    check(
        "Users hypothesis blockquote preserved",
        "The operator of an agent rig they built themselves" in text,
        "the Users design hypothesis was edited",
    )
    check(
        "Users status line preserved",
        "derived design hypothesis. Not observed, not measured" in text,
        "the Users status line was edited",
    )
    check(
        "Users anti-trigger framing preserved",
        "Explicit anti-trigger" in text and "browsing moment" in text,
        "the Users anti-trigger framing was removed rather than re-cited",
    )


def case_intent_positioning_preserved() -> None:
    flat = _flat(PRODUCT)
    check(
        "Positioning mechanism preserved",
        "turns candidates away" in flat and "including its own author's" in flat,
        "the Positioning mechanism sentence was edited",
    )
    check(
        "Positioning credence-good framing preserved",
        "credence-good problem" in flat,
        "the credence-good framing was removed",
    )


def case_intent_purpose_governance_preserved() -> None:
    text = _read(PRODUCT)
    check(
        "Purpose governance claim preserved",
        "admission is governed and the governance is visible" in text,
        "the Product Purpose governance claim was edited",
    )
    check(
        "ADMISSION four-question quote preserved",
        "Default answer: not admitted" in text,
        "the admission-policy quote was removed",
    )


def case_intent_brand_commitments_preserved() -> None:
    text = _read(PRODUCT)
    check(
        "Brand Commitments authorship preserved",
        "Authorship of public lines is the owner's" in text,
        "the authorship Brand Commitment was edited",
    )
    check(
        "Brand Commitments voice-specimen rule preserved",
        "Voice specimens must be cited" in text,
        "the voice-specimen Brand Commitment was edited",
    )
    check(
        "Brand Commitments dressing rule preserved",
        "The one absolute visual rule" in text,
        "the dressing Brand Commitment was edited",
    )


def case_product_brand_commitment_citations_resolve() -> None:
    """Brand Commitment citations in PRODUCT.md must point at live BRAND.md text."""
    flat = _flat(PRODUCT)
    _resolve("BRAND.md:21-23", "The owner writes the public lines", "BRAND.md:21-23 authorship line")
    _resolve("BRAND.md:35-41", "reads smoother than the README", "BRAND.md:35-41 polish line")
    _resolve("BRAND.md:47-54", "where each card came from", "BRAND.md:47-54 claims line")
    check(
        "PRODUCT.md cites BRAND.md:21-23 for authorship",
        "BRAND.md:21-23" in flat,
        "PRODUCT.md authorship citation missing",
    )
    check(
        "PRODUCT.md cites BRAND.md:35-41 for polish",
        "BRAND.md:35-41" in flat,
        "PRODUCT.md polish citation missing",
    )
    check(
        "PRODUCT.md cites BRAND.md:47-54 for claims",
        "BRAND.md:47-54" in flat,
        "PRODUCT.md claims citation missing",
    )


def case_intent_product_principles_preserved() -> None:
    text = _read(PRODUCT)
    start = text.find("## Product Principles")
    assert start != -1
    rest = text[start + len("## Product Principles") :]
    end = rest.find("\n## ")
    principles = rest if end == -1 else rest[:end]
    check(
        "Principle: default answer not admitted",
        "Default answer: not admitted" in principles,
        "Product Principle 1 was edited",
    )
    check(
        "Principle: inventory is not evidence",
        "Inventory state is never rendered as evidence state" in principles,
        "Product Principle 2 was edited",
    )
    check(
        "Principle: refusal is publishable",
        "A refusal is publishable content" in principles,
        "Product Principle 3 was edited",
    )
    check(
        "Principle: every number resolves to an artifact",
        "Every number resolves to a repository artifact" in principles,
        "Product Principle 4 was edited",
    )
    check(
        "Principle: author is not an admissible source",
        "author is not an admissible source" in principles,
        "Product Principle 5 was edited",
    )


def case_intent_brand_voice_section_untouched_by_currency_fix() -> None:
    """BRAND.md Voice specimens are owner copy; currency fixes must not touch them."""
    text = _read(BRAND)
    check(
        "BRAND.md Voice section still opens with the owner question",
        "I wanted to know if you could tell if a skill was good" in text,
        "the BRAND.md Voice specimen was edited",
    )
    check(
        "BRAND.md still requires VERBATIM.md citations for specimens",
        "Source: [`VERBATIM.md`](VERBATIM.md)" in text,
        "BRAND.md voice-specimen citations were removed",
    )


def case_intent_design_open_card_line_preserved() -> None:
    text = _read(DESIGN)
    check(
        "DESIGN.md open decision: card primary line still undecided",
        "The card's primary line" in text,
        "DESIGN.md lost the open decision about the card's primary line",
    )
    check(
        "DESIGN.md dressing doctrine preserved",
        "dressing the inventory as a measurement" in text,
        "DESIGN.md lost the dressing doctrine",
    )


# ==========================================================================
# Criterion 3 — line-number citations point at the cited text
# ==========================================================================
_CITATION = re.compile(
    r"(?P<file>(?:AGENTS|README|CATALOG|BRAND|PRODUCT|DESIGN|RETIRED|CHANGELOG|CONTEXT|ADMISSION)\.md"
    r"|README(?=:)"
    r"|validate_[a-z_]+\.py"
    r"|site/index\.html"
    r"|docs/[A-Za-z0-9_./-]+\.md):(?P<span>\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)"
)


def _citation_target(name: str) -> Path:
    """Resolve a citation name the way a reader would: repo root, then scripts/."""
    direct = REPO_ROOT / name
    if direct.is_file():
        return direct
    if name == "README":
        return REPO_ROOT / "README.md"
    if name.startswith("validate_") or name.startswith("check_") or name.startswith("test_"):
        return REPO_ROOT / "scripts" / name
    return direct


def case_citations_resolve_at_pr_head() -> None:
    """Every file:line citation in the three files must exist and be in range.

    Content matching is case-specific (see the STALE-row cases above). This
    case catches a citation that points past EOF or at a file that is not in
    the tree, which is the failure mode a stale line number always becomes.
    """
    unresolved: list[str] = []
    checked = 0
    for path in (PRODUCT, BRAND, DESIGN):
        for match in _CITATION.finditer(_read(path)):
            name = match.group("file")
            span = match.group("span")
            target = _citation_target(name)
            if not target.is_file():
                unresolved.append(f"{path.name} -> {name} (file missing)")
                continue
            line_count = len(target.read_text(encoding="utf-8").splitlines())
            for part in re.split(r",\s*", span):
                if "-" in part:
                    start_s, _, end_s = part.partition("-")
                    start, end = int(start_s), int(end_s)
                else:
                    start = end = int(part)
                checked += 1
                if start < 1 or end > line_count or start > end:
                    unresolved.append(
                        f"{path.name} -> {name}:{part} (file has {line_count} lines)"
                    )
    check(
        "every file:line citation in PRODUCT/BRAND/DESIGN resolves in range",
        not unresolved,
        "; ".join(unresolved[:8]),
    )
    print(f"     ({checked} citation spans checked)")


def case_corrected_citations_match_needles() -> None:
    """The corrected citations named in this suite's STALE-row cases, re-asserted."""
    pairs = [
        ("AGENTS.md:440", "The page states no tally"),
        ("CATALOG.md:31", "not intended to maximize coverage"),
        ("RETIRED.md:3", "Most collections only ever grow"),
        ("RETIRED.md:26", "Turning away your own work costs something"),
        ("RETIRED.md:93-107", "All four returned three passes out of three"),
        ("RETIRED.md:93-107", "personally convinced were valuable"),
        ("BRAND.md:75-76", "not with a market"),
        ("CATALOG.md:158-160", "OBSERVED"),
        ("AGENTS.md:435-436", "OBSERVED"),
        ("CATALOG.md:151-152", "two separate axes"),
        ("docs/design/variants/front-page/variant-1.md:20", "useful enough to keep developing"),
        ("docs/design/variants/front-page/variant-5.md:38", "breadth you do not use is still paid for"),
        ("scripts/validate_scoreboard.py:450-452", "re.findall"),
    ]
    bad: list[str] = []
    for cited, needle in pairs:
        name, _, span = cited.partition(":")
        target = _citation_target(name)
        if not target.is_file():
            bad.append(f"{cited}: file missing")
            continue
        lines = target.read_text(encoding="utf-8").splitlines()
        if "-" in span:
            start_s, _, end_s = span.partition("-")
            text = "\n".join(lines[int(start_s) - 1 : int(end_s)])
        else:
            n = int(span)
            text = lines[n - 1] if 1 <= n <= len(lines) else ""
        if needle not in text:
            bad.append(f"{cited}: missing {needle!r}")
    check(
        "every corrected citation target contains the claimed text",
        not bad,
        "; ".join(bad),
    )


# ==========================================================================
# Runner
# ==========================================================================
CASES = (
    case_product_no_counts_claim_narrowed,
    case_product_agents_citation_points_at_tally_rule,
    case_product_readme_honest_ceilings_attribution_removed,
    case_product_coverage_quote_cites_catalog,
    case_product_useful_enough_quote_cites_design_variants,
    case_product_brand_not_market_citation_moved,
    case_product_breadth_cost_quote_not_in_readme,
    case_product_purpose_allows_designed_cards,
    case_product_publication_not_validation_readme_claim_removed,
    case_product_retired_line_refs_corrected,
    case_product_screened_out_quote_current,
    case_product_distribution_matches_adr_0002,
    case_product_provenance_categories_citation_corrected,
    case_product_public_project_page_not_undecided,
    case_product_social_preview_precedent_not_live,
    case_brand_publication_not_validation_not_readme,
    case_brand_project_page_decision_closed,
    case_design_scoreboard_extraction_citation_current,
    case_design_social_preview_check_is_brand_kit_not_proposal,
    case_intent_users_hypothesis_preserved,
    case_intent_positioning_preserved,
    case_intent_purpose_governance_preserved,
    case_intent_brand_commitments_preserved,
    case_product_brand_commitment_citations_resolve,
    case_intent_product_principles_preserved,
    case_intent_brand_voice_section_untouched_by_currency_fix,
    case_intent_design_open_card_line_preserved,
    case_citations_resolve_at_pr_head,
    case_corrected_citations_match_needles,
)


def main() -> int:
    print(f"product-definition currency suite ({len(CASES)} cases)")
    for case in CASES:
        case()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        return 1
    print(
        "\nPASS: PRODUCT.md, BRAND.md and DESIGN.md match the S498 audit's current "
        "truth; pinned INTENT phrases present; citations resolve at the PR head."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
