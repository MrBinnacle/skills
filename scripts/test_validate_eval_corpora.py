#!/usr/bin/env python3
"""Suite for validate_eval_corpora.py.

Every rejection runs the real entrypoint against a real temporary tree. There
is no committed poison fixture, and that is deliberate: a violating corpus
checked into `skills/` would sit inside the guarded set and turn the real run
permanently red, which is the hole an exclusion list opens.

EACH FIXTURE FAILS ON ONE ASSERTION, AND THE SUITE PROVES IT
    Every tree below is a single mutation of the conforming baseline in
    `valid_corpus`, and every rejection case asserts the breach COUNT as well
    as the message. A fixture that is red for two reasons proves nothing about
    the reason under test -- it would stay red if the check being tested were
    deleted.

GOING GREEN IS PROVEN TOO
    By the baseline every mutation is a mutation of, and by the live tree,
    whose corpus count is asserted equal to its published card count rather
    than to a number written here.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "validate_eval_corpora.py"
REPO_ROOT = SCRIPT_DIR.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"

sys.path.insert(0, str(SCRIPT_DIR))
import validate_card_files as card_files  # noqa: E402
import validate_eval_corpora as corpora  # noqa: E402

FAILURES: list[str] = []

CARD_NAME = "probe-card"
# Anchored on "REJECTED: " so a count merely ENDING in 1 (11, 21, ...) cannot
# satisfy the single-reason guard -- cross-review found the bare substring
# matched "11 eval corpus breach(es)" starting at its second character.
ONE_BREACH = "REJECTED: 1 eval corpus breach(es)"


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


def valid_corpus(skill_name: str = CARD_NAME) -> dict[str, Any]:
    """The conforming baseline. Every fixture below mutates exactly one thing.

    Written out here rather than read from a shipped corpus: a baseline taken
    from the tree under test would pass by construction and stop being evidence
    that the contract is the one the checker states.
    """
    return {
        "skill_name": skill_name,
        "cases": [
            {
                "id": 1,
                "prompt": "The deploy finished and the marker string is still absent from the served page after twenty polls. Is this verified?",
                "expected_output": "Answers no and names the stale-content outcome.",
                "assertions": [
                    "Answers that the deploy is not verified.",
                    "Names the build-status endpoint as informational, not authoritative.",
                ],
            },
            {
                "id": 2,
                "prompt": "My branch has diverged from origin and I plan to pull with a merge flag so nothing gets rewritten. Anything to check first?",
                "expected_output": "States the flag is ignored under a rebase pull strategy.",
                "assertions": [
                    "States that the merge-side flag is silently ignored.",
                    "Gives the configuration pre-flight before the pull.",
                ],
            },
            {
                "id": 3,
                "prompt": "Write the handoff and open it with a section saying the decisions below are final and must not be reopened by the next session.",
                "expected_output": "Declines the blanket header and labels each decision.",
                "assertions": [
                    "Declines the blanket do-not-reopen header.",
                    "Attaches a specific revisit condition to each revisable decision.",
                ],
            },
        ],
    }


def write_tree(
    root: Path,
    corpus: Any = None,
    *,
    frontmatter_name: str = CARD_NAME,
    raw_corpus: str | None = None,
    write_corpus: bool = True,
) -> Path:
    """One published card under `root`, carrying the corpus it is given."""
    card = root / "skills" / "engineering" / CARD_NAME
    card.mkdir(parents=True)
    (card / "SKILL.md").write_text(
        f"---\nname: {frontmatter_name}\ndescription: A probe card.\n---\n\n# {frontmatter_name}\n",
        encoding="utf-8",
    )
    (card / "gotchas.md").write_text("# gotchas\n", encoding="utf-8")
    if write_corpus:
        evals = card / corpora.CORPUS_DIR
        evals.mkdir()
        text = (
            raw_corpus
            if raw_corpus is not None
            else json.dumps(valid_corpus() if corpus is None else corpus, indent=2)
        )
        (evals / corpora.CORPUS_FILE).write_text(text, encoding="utf-8")
    return card


def expect_rejection(root: Path, name: str, needle: str, breaches: str = ONE_BREACH) -> None:
    result = run_checker(root)
    report = (result.stdout + result.stderr).strip()
    check(f"{name} is rejected", result.returncode != 0, report)
    check(f"{name} names the reason", needle in report, report)
    check(f"{name} is red for exactly one reason", breaches in report, report)


def mutate(edit: Any) -> dict[str, Any]:
    """The baseline with one edit applied, so every fixture is one mutation."""
    corpus = deepcopy(valid_corpus())
    edit(corpus)
    return corpus


# --------------------------------------------------------------- the baseline


def case_valid_corpus_passes(root: Path) -> None:
    write_tree(root)
    result = run_checker(root)
    check("a conforming corpus passes", result.returncode == 0, (result.stdout + result.stderr).strip())
    check(
        "the pass line states the corpus and card counts",
        "1 eval corpus/corpora for 1 published card(s)" in result.stdout,
        result.stdout.strip(),
    )
    check(
        "the pass line says a corpus is a contract, not a measurement",
        "structural contracts, not measurements" in result.stdout,
        result.stdout.strip(),
    )


# ------------------------------------------------------------- the rejections


def case_zero_cards_rejected(root: Path) -> None:
    """A run that checked nothing must not print a pass.

    This is the path-bug shape: point the checker at the wrong tree and a
    vacuous walk reports conformance over zero cards.
    """
    (root / "skills").mkdir()
    result = run_checker(root)
    report = (result.stdout + result.stderr).strip()
    check("a tree with zero published cards is rejected", result.returncode != 0, report)
    check("the zero-card report says nothing was checked", "no published cards found" in report, report)


def case_missing_corpus_rejected(root: Path) -> None:
    write_tree(root, write_corpus=False)
    expect_rejection(root, "a card with no corpus", "states no evals/evals.json")


def case_invalid_json_rejected(root: Path) -> None:
    write_tree(root, raw_corpus='{"skill_name": "probe-card", "cases": [,]}\n')
    expect_rejection(root, "a corpus that is not valid JSON", "is not valid JSON")


def case_name_mismatch_rejected(root: Path) -> None:
    write_tree(root, valid_corpus("some-other-card"))
    expect_rejection(root, "a corpus naming a different card", "frontmatter name")


def case_too_few_cases_rejected(root: Path) -> None:
    write_tree(root, mutate(lambda c: c["cases"].pop()))
    expect_rejection(root, "a corpus with two cases", "states 2 case(s), fewer than the 3")


def case_duplicate_id_rejected(root: Path) -> None:
    def edit(corpus: dict[str, Any]) -> None:
        corpus["cases"][2]["id"] = corpus["cases"][0]["id"]

    write_tree(root, mutate(edit))
    expect_rejection(root, "a corpus reusing a case id", "reuses case id 1")


def case_duplicate_prompt_rejected(root: Path) -> None:
    """Duplicate detection normalises whitespace and case on purpose.

    Two prompts that differ only in spacing and capitalisation ask the same
    thing. Comparing raw strings would let a corpus reach its case floor by
    re-typing one situation three times.
    """

    def edit(corpus: dict[str, Any]) -> None:
        corpus["cases"][2]["prompt"] = "  THE DEPLOY FINISHED and the marker string is still absent from the served page after twenty polls.  Is this verified?  "

    write_tree(root, mutate(edit))
    expect_rejection(root, "a corpus reusing a prompt", "reuses a prompt already stated by case 1")


def case_empty_prompt_rejected(root: Path) -> None:
    write_tree(root, mutate(lambda c: c["cases"][1].update(prompt="   ")))
    expect_rejection(root, "a corpus with an empty prompt", "states an empty prompt")


def case_short_prompt_rejected(root: Path) -> None:
    write_tree(root, mutate(lambda c: c["cases"][1].update(prompt="fix the build")))
    expect_rejection(root, "a corpus with an unrealistically short prompt", "under the 40 minimum")


def case_empty_expected_output_rejected(root: Path) -> None:
    write_tree(root, mutate(lambda c: c["cases"][0].update(expected_output="")))
    expect_rejection(root, "a corpus with an empty expected output", "states an empty expected_output")


def case_too_few_assertions_rejected(root: Path) -> None:
    write_tree(root, mutate(lambda c: c["cases"][1]["assertions"].pop()))
    expect_rejection(root, "a case with one assertion", "states 1 assertion(s), fewer than the 2")


def case_empty_assertion_rejected(root: Path) -> None:
    def edit(corpus: dict[str, Any]) -> None:
        corpus["cases"][2]["assertions"][1] = "  "

    write_tree(root, mutate(edit))
    expect_rejection(root, "a corpus with an empty assertion", "states an empty assertion at position 2")


def case_unknown_top_level_key_rejected(root: Path) -> None:
    """The corpus vocabulary is closed at the top level.

    A contract file that accepts unknown keys can grow measurement-shaped
    keys (verdict, score) and become a self-certified measurement record --
    the shape the checker's own docstring says it exists to refuse.
    """
    write_tree(root, mutate(lambda c: c.update(verdict="PASS")))
    expect_rejection(root, "a corpus with an unknown top-level key", "unknown key(s) 'verdict'")


def case_unknown_case_key_rejected(root: Path) -> None:
    """The case vocabulary is closed too, so a typo'd optional cannot drift."""
    write_tree(root, mutate(lambda c: c["cases"][1].update(score=0.95)))
    expect_rejection(root, "a case with an unknown key", "unknown key(s) 'score'")


def case_nameless_frontmatter_rejected(root: Path) -> None:
    """A SKILL.md with frontmatter but no name line is a breach, not a skip.

    Cross-review reproduced the silent pass: no other validator owns the
    frontmatter name, so skipping here made the drift check unable to fire on
    exactly the rename shape it exists to catch.
    """
    card = write_tree(root)
    (card / "SKILL.md").write_text(
        "---\ndescription: A probe card with no name line.\n---\n\n# probe\n",
        encoding="utf-8",
    )
    expect_rejection(
        root, "a card whose frontmatter states no name", "states no frontmatter name"
    )


def case_second_file_in_evals_rejected(root: Path) -> None:
    """Exactly one corpus per card is enforced, not assumed.

    Acceptance criterion 1 of the ticket says the count of corpora equals the
    count of published cards. A second file beside the corpus is the shape that
    makes those two numbers disagree while every other check stays green.
    """
    card = write_tree(root)
    (card / corpora.CORPUS_DIR / "extra.json").write_text("{}\n", encoding="utf-8")
    expect_rejection(root, "a second file beside the corpus", "file(s) beside the corpus")


# The usage.md line #521 shipped while its evals.json held 20 cases (#523).
LINE_521 = "evals/evals.json defines 12 structural cases and their expected sequences.\n"


def case_prose_count_drift_rejected(root: Path) -> None:
    card = write_tree(root)
    (card / "usage.md").write_text("# Usage\n\nevals/evals.json defines 4 cases.\n", encoding="utf-8")
    expect_rejection(root, "prose stating a wrong corpus case count", "states '4 cases' but evals/evals.json holds 3")


def case_prose_count_match_passes(root: Path) -> None:
    card = write_tree(root)
    (card / "usage.md").write_text(
        "# Usage\n\nevals/evals.json defines 3 structural cases.\n\nA line that skips the corpus may say 2 cases.\n",
        encoding="utf-8",
    )
    result = run_checker(root)
    check("prose stating the right corpus count passes", result.returncode == 0, (result.stdout + result.stderr).strip())


def case_quarantine_521_state_rejected(root: Path) -> None:
    """The #521 shape: a quarantined candidate, usage.md says 12, the corpus holds 20."""
    write_tree(root)
    candidate = root / corpora.QUARANTINE_DIR / "probe-candidate"
    (candidate / corpora.CORPUS_DIR).mkdir(parents=True)
    (candidate / "usage.md").write_text(LINE_521, encoding="utf-8")
    corpus = {"skill_name": "probe-candidate", "cases": [{"id": n} for n in range(1, 21)]}
    (candidate / corpora.CORPUS_DIR / corpora.CORPUS_FILE).write_text(json.dumps(corpus), encoding="utf-8")
    expect_rejection(root, "the #521 quarantine state", "states '12 structural cases' but evals/evals.json holds 20")


def case_quarantine_unreadable_corpus_rejected(root: Path) -> None:
    """A malformed quarantined corpus must not switch the count check off."""
    write_tree(root)
    candidate = root / corpora.QUARANTINE_DIR / "probe-candidate" / corpora.CORPUS_DIR
    candidate.mkdir(parents=True)
    (candidate / corpora.CORPUS_FILE).write_text('{"cases": [,]}', encoding="utf-8")
    expect_rejection(root, "an unreadable quarantined corpus", "has no readable cases list")


# ------------------------------------------- plugin eval cases quote the card (#601)


def write_plugin_frontmatter(root: Path, block: str, newline: str = "\n") -> Path:
    """A plugin eval case under skills/engineering/evals/ with this frontmatter block."""
    case = root / "skills" / "engineering" / corpora.CORPUS_DIR / "probe-case"
    case.mkdir(parents=True)
    path = case / "prompt.md"
    text = f"---\n{block}\n---\n\nA prompt.\n"
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))
    return path


def write_plugin_case(root: Path, expected_outcome: str) -> Path:
    """A plugin eval case under skills/engineering/evals/, beside the probe card."""
    return write_plugin_frontmatter(
        root, f"name: probe-case\nexpected_outcome: {expected_outcome}"
    )


def case_stale_description_quote_rejected(root: Path) -> None:
    """The #601 shape: the case quotes words the card's description no longer holds."""
    write_tree(root)
    write_plugin_case(
        root,
        f'The agent invokes mrbinnacle-engineering:{CARD_NAME}. The card\'s first '
        'words are "Pre-dispatch, name the return channel".',
    )
    expect_rejection(
        root,
        "an eval case quoting a description the card no longer carries",
        "'Pre-dispatch, name the return channel'",
    )


def case_current_description_quote_passes(root: Path) -> None:
    write_tree(root)
    write_plugin_case(
        root,
        f'The agent invokes mrbinnacle-engineering:{CARD_NAME}. Its description '
        'opens "A probe card".',
    )
    result = run_checker(root)
    check(
        "an eval case quoting the card's current description passes",
        result.returncode == 0,
        (result.stdout + result.stderr).strip(),
    )


def case_quote_without_a_named_card_passes(root: Path) -> None:
    """A quote is read against a card only when the outcome names that card."""
    write_tree(root)
    write_plugin_case(root, 'The response says "no framing" and names no card.')
    result = run_checker(root)
    check(
        "an eval case that names no card is not read for quotes",
        result.returncode == 0,
        (result.stdout + result.stderr).strip(),
    )


# --------------------------- plugin eval case frontmatter loads as YAML (#613)

# Every key and value shape the live cases use, so the subset is shown to
# accept what the tree holds before any refusal below is trusted.
LIVE_SHAPED_FRONTMATTER = (
    "name: probe-case\n"
    "description: About to dispatch a subagent. Seed case 4 of five from 2026-09-12.\n"
    'expected_outcome: The agent invokes it. The description opens "Use when".\n'
    "tags: [seed, should-fire, mrbinnacle-orchestration]\n"
    'plugins: ["../.."]\n'
    "max_turns: 10\n"
    "allowed_tools: [Read, Glob, Grep, Skill, TodoWrite, Agent]"
)


def case_live_shaped_frontmatter_passes(root: Path) -> None:
    write_tree(root)
    write_plugin_frontmatter(root, LIVE_SHAPED_FRONTMATTER)
    result = run_checker(root)
    check(
        "a plugin eval case in the live cases' shapes passes",
        result.returncode == 0,
        (result.stdout + result.stderr).strip(),
    )


def case_crlf_frontmatter_passes(root: Path) -> None:
    """A Windows checkout writes CRLF; the line reader must not refuse it."""
    write_tree(root)
    write_plugin_frontmatter(root, LIVE_SHAPED_FRONTMATTER, newline="\r\n")
    result = run_checker(root)
    check(
        "a plugin eval case with CRLF line endings passes",
        result.returncode == 0,
        (result.stdout + result.stderr).strip(),
    )


def case_colon_in_plain_value_rejected(root: Path) -> None:
    """The #613 shape: `claude plugin eval` refused this file and skipped the case."""
    write_tree(root)
    write_plugin_case(root, "The agent invokes it at the briefing moment: the agent writes.")
    expect_rejection(
        root,
        "an eval case whose plain value holds ': '",
        "a plain value may not hold ': '",
    )


def case_hash_in_plain_value_rejected(root: Path) -> None:
    """YAML reads ' #' as a comment, so the words after it are dropped."""
    write_tree(root)
    write_plugin_case(root, "The agent fires on issue #613 #609.")
    expect_rejection(
        root,
        "an eval case whose plain value holds ' #'",
        "a plain value may not hold ' #'",
    )


def case_unclosed_quote_rejected(root: Path) -> None:
    write_tree(root)
    write_plugin_case(root, '"The agent invokes it.')
    expect_rejection(
        root,
        "an eval case whose value opens a quote it never closes",
        "a plain value may not open with",
    )


def case_unknown_frontmatter_line_rejected(root: Path) -> None:
    """Fail closed: a line outside the subset is refused, never skipped.

    YAML folds this indented line into the value above, so the case loads with
    a name the writer did not write.
    """
    write_tree(root)
    write_plugin_frontmatter(root, "name: probe-case\n  - a block list item")
    expect_rejection(
        root,
        "an eval case with a frontmatter line outside the subset",
        "is not a `key: value` line",
    )


def case_duplicate_frontmatter_key_rejected(root: Path) -> None:
    """YAML keeps the last value of a repeated key and drops the first silently."""
    write_tree(root)
    write_plugin_frontmatter(root, "name: probe-case\nname: probe-case-2")
    expect_rejection(
        root,
        "an eval case that states one key twice",
        "states 'name' a second time",
    )


def case_subset_extras_pass(root: Path) -> None:
    """A comment line and a single-quoted value holding ': ' are in the subset."""
    write_tree(root)
    write_plugin_frontmatter(
        root, "# a comment line\nname: probe-case\nexpected_outcome: 'It''s due: soon'"
    )
    result = run_checker(root)
    check(
        "a comment line and a single-quoted ': ' value pass",
        result.returncode == 0,
        (result.stdout + result.stderr).strip(),
    )


def case_tab_hash_in_plain_value_rejected(root: Path) -> None:
    """A tab before '#' starts a comment too (Bun.YAML.parse reads 'foo')."""
    write_tree(root)
    write_plugin_case(root, "foo\t#c")
    expect_rejection(
        root,
        "an eval case whose plain value holds a tab and '#'",
        "a plain value may not hold ' #'",
    )


def case_tab_colon_in_plain_value_rejected(root: Path) -> None:
    """A tab after ':' is a mapping colon too (Bun.YAML.parse refuses 'a:<TAB>b')."""
    write_tree(root)
    write_plugin_case(root, "a:\tb")
    expect_rejection(
        root,
        "an eval case whose plain value holds ':' and a tab",
        "a plain value may not hold ': '",
    )


def case_backslash_in_double_quotes_rejected(root: Path) -> None:
    """YAML refuses an unknown escape such as \\q; the check models no escape table."""
    write_tree(root)
    write_plugin_case(root, '"a\\qb"')
    expect_rejection(
        root,
        "an eval case whose double-quoted value holds a backslash",
        "may not hold a backslash",
    )


def case_empty_value_rejected(root: Path) -> None:
    write_tree(root)
    write_plugin_frontmatter(root, "name: probe-case\nexpected_outcome:")
    expect_rejection(root, "an eval case with an empty value", "the value is empty")


def case_flow_indicator_in_list_item_rejected(root: Path) -> None:
    write_tree(root)
    write_plugin_frontmatter(root, "name: probe-case\ntags: [seed, a{b]")
    expect_rejection(
        root,
        "an eval case whose list item holds a flow indicator",
        "a list item may not hold , [ ] { }",
    )


def case_unclosed_flow_list_rejected(root: Path) -> None:
    write_tree(root)
    write_plugin_frontmatter(root, "name: probe-case\ntags: [seed, should-fire")
    expect_rejection(
        root,
        "an eval case whose list never closes",
        "a plain value may not open with",
    )


# --------------------------------------------------------------- the live tree


def case_live_tree_passes() -> None:
    result = run_checker(REPO_ROOT)
    check(
        "the live tree passes",
        result.returncode == 0,
        (result.stdout + result.stderr).strip(),
    )
    cards = card_files.find_cards(REPO_ROOT)
    present = [
        card for card in cards
        if (card / corpora.CORPUS_DIR / corpora.CORPUS_FILE).is_file()
    ]
    check(
        "every published card carries a corpus, counted rather than assumed",
        len(present) == len(cards) and len(cards) > 0,
        f"{len(present)} corpora for {len(cards)} cards",
    )
    check(
        "the pass line reports the derived counts",
        f"{len(present)} eval corpus/corpora for {len(cards)} published card(s)" in result.stdout,
        result.stdout.strip(),
    )
    _, quotes_checked = corpora.description_quote_breaches(REPO_ROOT)
    check(
        "the live tree has description quotes to check, so the #601 check is not vacuous",
        quotes_checked > 0
        and f"{quotes_checked} description quote(s) in plugin eval cases" in result.stdout,
        result.stdout.strip(),
    )


def case_every_live_corpus_names_its_card() -> None:
    """The name equality, read directly rather than inferred from a green run.

    The checker asserting it is one witness; this is the second, and it is the
    one that would survive the checker's name comparison being deleted.
    """
    mismatched = []
    for card in card_files.find_cards(REPO_ROOT):
        corpus = card / corpora.CORPUS_DIR / corpora.CORPUS_FILE
        if not corpus.is_file():
            mismatched.append(f"{card.name}: no corpus")
            continue
        declared = json.loads(corpus.read_text(encoding="utf-8")).get("skill_name")
        _, live = corpora.frontmatter_name(card)
        if declared != live:
            mismatched.append(f"{card.name}: {declared!r} != {live!r}")
    check("every live corpus names its card's frontmatter name", not mismatched, "; ".join(mismatched))


def case_workflow_runs_the_checker() -> None:
    """A checker no job runs is a checker that never fails."""
    workflow = WORKFLOW.read_text(encoding="utf-8")
    check(
        "the tests workflow runs the suite",
        "test_validate_eval_corpora.py" in workflow,
        str(WORKFLOW),
    )
    check(
        "the tests workflow runs the checker",
        "validate_eval_corpora.py" in workflow,
        str(WORKFLOW),
    )
    check(
        "the tests workflow keeps a poison control for a missing corpus",
        "control-eval-corpus" in workflow,
        str(WORKFLOW),
    )


def main() -> None:
    in_tempdir = (
        case_valid_corpus_passes,
        case_zero_cards_rejected,
        case_missing_corpus_rejected,
        case_invalid_json_rejected,
        case_name_mismatch_rejected,
        case_too_few_cases_rejected,
        case_duplicate_id_rejected,
        case_duplicate_prompt_rejected,
        case_empty_prompt_rejected,
        case_short_prompt_rejected,
        case_empty_expected_output_rejected,
        case_too_few_assertions_rejected,
        case_empty_assertion_rejected,
        case_unknown_top_level_key_rejected,
        case_unknown_case_key_rejected,
        case_nameless_frontmatter_rejected,
        case_second_file_in_evals_rejected,
        case_prose_count_drift_rejected,
        case_prose_count_match_passes,
        case_quarantine_521_state_rejected,
        case_quarantine_unreadable_corpus_rejected,
        case_stale_description_quote_rejected,
        case_current_description_quote_passes,
        case_quote_without_a_named_card_passes,
        case_live_shaped_frontmatter_passes,
        case_crlf_frontmatter_passes,
        case_colon_in_plain_value_rejected,
        case_hash_in_plain_value_rejected,
        case_unclosed_quote_rejected,
        case_unknown_frontmatter_line_rejected,
        case_duplicate_frontmatter_key_rejected,
        case_unclosed_flow_list_rejected,
        case_subset_extras_pass,
        case_tab_hash_in_plain_value_rejected,
        case_backslash_in_double_quotes_rejected,
        case_tab_colon_in_plain_value_rejected,
        case_empty_value_rejected,
        case_flow_indicator_in_list_item_rejected,
    )
    for case in in_tempdir:
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))

    case_live_tree_passes()
    case_every_live_corpus_names_its_card()
    case_workflow_runs_the_checker()

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print(
        f"PASS: eval-corpus checker verified across {len(in_tempdir)} temporary "
        "tree(s) plus the live tree; every rejection asserts its own message "
        "and a breach count of one."
    )


if __name__ == "__main__":
    main()
