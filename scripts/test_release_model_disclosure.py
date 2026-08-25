#!/usr/bin/env python3
"""Contract tests for the release-model disclosure on the public surfaces.

ADR 0002 (docs/adr/0002-a-release-is-a-delivery-event.md) decided that a release
is a delivery event -- changed cards reach installed users when a version is
released -- and declared the narrow surface a version promises: the install path
and the card format, with the card set deliberately outside it. Two shipped
surfaces described the world that decision replaced: CHANGELOG.md opened by
calling tags and the file "a reading aid, not a pin", and the README offered no
disclosure that the card set is expected to change under a minor release. These
cases pin the corrected surfaces.

The scope is deliberate. Historical release notes state counts and describe the
old model; they are dated snapshots and are not rewritten here. The guarantee is
about what a reader of the preamble and the Install section is told today.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

ROOT = SCRIPT_DIR.parent
CHANGELOG = ROOT / "CHANGELOG.md"
README = ROOT / "README.md"
ADR = ROOT / "docs" / "adr" / "0002-a-release-is-a-delivery-event.md"
ADR_RELATIVE = "(docs/adr/0002-a-release-is-a-delivery-event.md)"

FAILURES: list[str] = []

PROMISE_LEAD = "**What a version promises.**"

# The disclosure this ticket adds invites exactly one rotting embellishment: a
# tally of how many cards ship today ("currently N cards"). Owner rulings retired
# page tallies twice for being maintenance taxes (2026-08-23 banner, 2026-08-24
# front page), so the disclosed surfaces carry none -- digits or spelled out.
# Historical release notes and the derived census table are other instruments'
# territory: snapshots stay snapshots, and test_readme_admission_lead owns the
# table.
_NUMBER = (
    r"(?:\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty)"
)
COUNT_RE = re.compile(
    rf"\b{_NUMBER}\s+(?:published\s+|shipped\s+|installed\s+)?(?:cards?|skills?)\b",
    re.IGNORECASE,
)


def stated_counts(text: str) -> list[str]:
    """Every count-of-cards statement in the text, as the matched spans."""
    return [match.group(0) for match in COUNT_RE.finditer(text)]


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def changelog_preamble(changelog: Path) -> str:
    """Everything in CHANGELOG.md before the first release-note heading."""
    match = re.search(r"^## ", changelog.read_text(encoding="utf-8"), re.MULTILINE)
    text = changelog.read_text(encoding="utf-8")
    return text[: match.start()] if match else text


def case_preamble_carries_no_reading_aid_claim() -> None:
    body = changelog_preamble(CHANGELOG)
    check(
        "changelog preamble no longer calls tags and the file a reading aid, not a pin",
        "reading aid" not in body and "not a pin" not in body,
        body.strip(),
    )


def case_preamble_states_the_delivery_model() -> None:
    # Collapsed: the claim is about what the preamble SAYS, not where its lines
    # wrap, so a reflow must not turn the gate red.
    body = " ".join(changelog_preamble(CHANGELOG).split())
    check(
        "changelog preamble states changed cards reach installed users "
        "when a version is released",
        "changed cards reach installed users" in body and "version is released" in body,
        body,
    )
    check(
        "changelog preamble links ADR 0002 and the record exists",
        ADR_RELATIVE in body and ADR.is_file(),
        body,
    )


def section(text: str, heading: str) -> str:
    """The body of one `## ` section, ending at the next heading."""
    match = re.search(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def promise_paragraph(install_body: str) -> str:
    """The paragraph led by the version-promise disclosure, for focused checks."""
    lines = install_body.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(PROMISE_LEAD)), None)
    if start is None:
        return ""
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].strip()), len(lines))
    return "\n".join(lines[start:end])


def case_readme_states_the_declared_surface() -> None:
    body = section(README.read_text(encoding="utf-8"), "Install")
    check(
        "install section carries the version-promise disclosure",
        PROMISE_LEAD in body,
        body.strip(),
    )
    collapsed = " ".join(promise_paragraph(body).split()).lower()
    check(
        "the promise names the install path and the card format, "
        "and excludes the card set",
        "the install path and the card format" in collapsed
        and "not the card set" in collapsed,
        collapsed,
    )
    check(
        "the promise links ADR 0002 and the record exists",
        ADR_RELATIVE in collapsed and ADR.is_file(),
        collapsed,
    )


def case_readme_states_card_moves_are_minor() -> None:
    collapsed = " ".join(
        promise_paragraph(section(README.read_text(encoding="utf-8"), "Install")).split()
    )
    check(
        "the readme states plainly that admitting or retiring a card is a minor change",
        bool(re.search(r"[Aa]dmitting or retiring a card is a minor change", collapsed)),
        collapsed,
    )


def case_disclosed_surfaces_state_no_count() -> None:
    surfaces = {
        "changelog preamble": changelog_preamble(CHANGELOG),
        "readme version-promise paragraph": promise_paragraph(
            section(README.read_text(encoding="utf-8"), "Install")
        ),
    }
    for label, text in sorted(surfaces.items()):
        matches = stated_counts(text)
        check(f"{label} states no count of cards or skills", not matches, str(matches))


def case_count_scan_can_fail() -> None:
    # A gate that cannot fail guards nothing. The refusal direction is exercised
    # against synthetic prose, because the shipped surfaces are (by design)
    # clean and would otherwise never show the scan biting.
    for sample in (
        "The collection ships 15 cards.",
        "nine skills today",
        "twelve published cards",
    ):
        check(
            f"count scan refuses a stated inventory ({sample!r})",
            bool(stated_counts(sample)),
            sample,
        )
    check(
        "count scan does not flag ordinary version prose",
        not stated_counts(
            "Changed cards reach installed users when a version is released."
        ),
    )


# ----------------------------------------------- AGENTS.md maintainer procedure
#
# ADR 0002 made the merge of the version-bump pull request the delivery event -- not a
# tag push. The maintainer instructions (AGENTS.md step 4) still described the old model:
# "tag by hand if wanted", which treats the tag as optional decoration. These cases pin
# the corrected procedure, which names the delivery model, the release-gate command, the
# immutability constraint, the token prerequisite, and the maintainer as the actor.


AGENTS = ROOT / "AGENTS.md"


def release_procedure(text: str) -> str:
    """Step 4 of the 'Every change' procedure in AGENTS.md, through its warning block,
    ending at the next top-level bold heading."""
    match = re.search(r"(?ms)^4\. .*?(?=^\*\*)", text)
    return match.group(0) if match else ""


def case_agents_procedure_describes_delivery_event_not_tag_by_hand() -> None:
    """Criterion 1: the procedure describes the delivery-event model rather than
    tagging by hand if wanted. The old text said 'tag by hand if wanted', which treats
    the tag as optional decoration; ADR 0002 made the merge the delivery, not the tag."""
    body = release_procedure(AGENTS.read_text(encoding="utf-8"))
    collapsed = " ".join(body.split())
    check(
        "AGENTS.md release procedure does not say 'tag by hand if wanted'",
        "tag by hand if wanted" not in collapsed,
        collapsed,
    )
    check(
        "AGENTS.md release procedure states the merge is the delivery event",
        "delivery event" in collapsed.lower() and "merge" in collapsed.lower(),
        collapsed,
    )


def case_agents_names_the_release_fitness_command() -> None:
    """Criterion 2: the procedure names the single command that reports release fitness
    (python scripts/release_gate.py) and states that it reports all failures at once.

    After npm run version, package.json has moved and the manifest has not. Bare
    release_gate.py then refuses G1 lockstep on every real bump. The procedure must
    name --write so the stamp and the fitness report are the same step a maintainer
    actually runs; naming the script without the flag describes a command that cannot
    pass on the tree it is supposed to clear."""
    body = release_procedure(AGENTS.read_text(encoding="utf-8"))
    collapsed = " ".join(body.split())
    check(
        "AGENTS.md names the release gate command",
        "release_gate.py" in collapsed,
        collapsed,
    )
    check(
        "AGENTS.md names --write so the post-bump gate can pass lockstep",
        "--write" in collapsed,
        collapsed,
    )
    check(
        "AGENTS.md states the gate reports all failures at once",
        "every stale surface" in collapsed.lower() and "one run" in collapsed.lower(),
        collapsed,
    )


def case_agents_states_release_immutability() -> None:
    """Criterion 3: the procedure states that release immutability is enabled and that a
    tag name cannot be reused once spent."""
    body = release_procedure(AGENTS.read_text(encoding="utf-8"))
    collapsed = " ".join(body.split())
    check(
        "AGENTS.md states release immutability is enabled",
        "release immutability" in collapsed.lower() and "enabled" in collapsed.lower(),
        collapsed,
    )
    check(
        "AGENTS.md states a tag name cannot be reused once spent",
        "tag name" in collapsed.lower() and "cannot be reused" in collapsed.lower(),
        collapsed,
    )


def case_agents_states_the_token_prerequisite() -> None:
    """Criterion 4: the procedure states the token prerequisite the changelog generator
    needs (GITHUB_TOKEN with public_repo scope)."""
    body = release_procedure(AGENTS.read_text(encoding="utf-8"))
    collapsed = " ".join(body.split())
    check(
        "AGENTS.md states the GITHUB_TOKEN prerequisite",
        "GITHUB_TOKEN" in collapsed,
        collapsed,
    )


def case_agents_names_who_performs_the_delivering_merge() -> None:
    """Criterion 5: the procedure names who performs the delivering merge. The
    maintainer holds merge authority; the delivery is the merge of the version-bump
    pull request."""
    body = release_procedure(AGENTS.read_text(encoding="utf-8"))
    collapsed = " ".join(body.split())
    check(
        "AGENTS.md names the maintainer as who performs the delivering merge",
        "maintainer" in collapsed.lower() and "merge" in collapsed.lower(),
        collapsed,
    )


def case_agents_procedure_follows_the_authoring_discipline() -> None:
    """Criterion 6: the procedure is written through the agent-document authoring
    discipline (the prose voice register). The register requires naming the mechanism
    (what the merge does), stating the consequence (what immutability means), and using
    active voice (naming the actor). The old text used a label ('manual step') and an
    imperative without an actor where the register requires the mechanism and the named
    actor."""
    body = release_procedure(AGENTS.read_text(encoding="utf-8"))
    collapsed = " ".join(body.split()).lower()
    check(
        "AGENTS.md procedure names the mechanism (the merge is the delivery event)",
        "delivery event" in collapsed,
        collapsed,
    )
    check(
        "AGENTS.md procedure states the consequence (the gate blocks before the merge)",
        "block" in collapsed and "before" in collapsed,
        collapsed,
    )
    check(
        "AGENTS.md procedure uses active voice (the maintainer merges)",
        "the maintainer merges" in collapsed,
        collapsed,
    )


def case_changeset_readme_no_longer_states_the_old_model() -> None:
    """The changesets folder README is maintainer release procedure too. It shipped
    with 'tag it by hand if you want a tag' and 'reading aid, not a pin' — the same
    pre-ADR-0002 model AGENTS.md step 4 carried. Leaving it would keep the false
    model one hop from the command the procedure names."""
    body = (ROOT / ".changeset" / "README.md").read_text(encoding="utf-8")
    collapsed = " ".join(body.split()).lower()
    check(
        ".changeset/README.md does not say tag by hand",
        "tag it by hand" not in collapsed and "tag by hand" not in collapsed,
        collapsed,
    )
    check(
        ".changeset/README.md no longer calls versions a reading aid, not a pin",
        "reading aid" not in collapsed and "not a pin" not in collapsed,
        collapsed,
    )
    check(
        ".changeset/README.md names the delivery event and the write-mode gate",
        "delivery event" in collapsed and "release_gate.py" in collapsed and "--write" in collapsed,
        collapsed,
    )


def main() -> None:
    case_preamble_carries_no_reading_aid_claim()
    case_preamble_states_the_delivery_model()
    case_readme_states_the_declared_surface()
    case_readme_states_card_moves_are_minor()
    case_disclosed_surfaces_state_no_count()
    case_count_scan_can_fail()
    case_agents_procedure_describes_delivery_event_not_tag_by_hand()
    case_agents_names_the_release_fitness_command()
    case_agents_states_release_immutability()
    case_agents_states_the_token_prerequisite()
    case_agents_names_who_performs_the_delivering_merge()
    case_agents_procedure_follows_the_authoring_discipline()
    case_changeset_readme_no_longer_states_the_old_model()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        raise SystemExit(1)
    print("PASS: release-model disclosure matches ADR 0002 on every surface that states the model")


if __name__ == "__main__":
    main()
