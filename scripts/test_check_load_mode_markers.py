#!/usr/bin/env python3
"""check_load_mode_markers.py goes red on each way a by-hand marker can drift.

Every control copies the live skills/ tree into a temp dir and plants one
breach in the copy, so the poison is the real README and the real cards with a
single change. Each control asserts the change landed before running the check,
and asserts the refusal names the card, not merely that something failed.
"""
from __future__ import annotations

import io
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import check_load_mode_markers as markers  # noqa: E402

ROOT = SCRIPT_DIR.parent
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_on_copy(plant: Callable[[Path], None]) -> tuple[int, str]:
    """Run the checker on a copy of the live tree after `plant` changes the copy."""
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        shutil.copytree(ROOT / "skills", tree / "skills")
        plant(tree)
        out = io.StringIO()
        with redirect_stdout(out):
            code = markers.main(["--root", str(tree)])
        return code, out.getvalue()


def planted(edit_path: str, old: str, new: str) -> tuple[int, str]:
    """Run the checker on a copy of the live tree with one replacement made."""

    def replace(tree: Path) -> None:
        target = tree / edit_path
        text = target.read_text(encoding="utf-8")
        assert old in text, f"control anchor absent in {edit_path}: {old!r}"
        target.write_bytes(text.replace(old, new, 1).encode("utf-8"))

    return run_on_copy(replace)


def control(name: str, edit_path: str, old: str, new: str, expect: str) -> None:
    code, out = planted(edit_path, old, new)
    print(f"     {out.strip()}".replace("\n", "\n     "))
    check(name, code == 1 and expect in out, f"exit {code}, wanted {expect!r} in: {out}")


ENG = "skills/engineering/README.md"
ORCH = "skills/orchestration/README.md"
CLIRUNNER_LINE = "- [**clirunner-env**](clirunner-env/SKILL.md) *(by hand)*"
VACUOUS_LINE = "- [**vacuous-check**](vacuous-check/SKILL.md)"
HALT_LINE = "- [**halt-as-deliverable**](halt-as-deliverable/SKILL.md)"
FLAG = "disable-model-invocation: true"


def main() -> None:
    cards, problems = markers.check(ROOT)
    check(
        f"the live tree passes ({len(cards)} cards)",
        bool(cards) and not problems,
        "\n  " + "\n  ".join(problems),
    )
    check(
        "a value after the key is read from the frontmatter only",
        markers.frontmatter("---\nname: x\ndisable-model-invocation: 'true'\n---\nbody\n")
        == {"name": "x", "disable-model-invocation": "true"},
    )
    check(
        "an unterminated frontmatter block reads as no frontmatter",
        markers.frontmatter("---\ndisable-model-invocation: true\n") == {},
    )
    control(
        "control: a by-hand card whose README line drops the marker fails, naming it",
        ENG, CLIRUNNER_LINE, "- [**clirunner-env**](clirunner-env/SKILL.md)",
        "clirunner-env: its SKILL.md frontmatter sets disable-model-invocation: true",
    )
    control(
        "control: a marker on a card without the flag fails, naming it",
        ENG, VACUOUS_LINE, VACUOUS_LINE + " *(by hand)*",
        "vacuous-check: skills/engineering/README.md marks it *(by hand)*",
    )
    control(
        "control: a published card missing from its bucket README fails",
        ENG, HALT_LINE, "- halt-as-deliverable, unlinked",
        "halt-as-deliverable: skills/engineering/ holds a card the README does not name",
    )
    control(
        "control: a by-hand marker placed later in the line fails, naming the position rule",
        ENG, CLIRUNNER_LINE, "- [**clirunner-env**](clirunner-env/SKILL.md) late *(by hand)*",
        "clirunner-env: its SKILL.md frontmatter sets disable-model-invocation: true, but "
        "skills/engineering/README.md does not mark it *(by hand)* right after the link",
    )
    control(
        "control: a card listed twice fails",
        ENG, HALT_LINE, HALT_LINE + " first\n" + HALT_LINE,
        "halt-as-deliverable: skills/engineering/README.md lists it on 2 lines",
    )
    control(
        "control: the flag removed from a by-hand card's frontmatter fails",
        "skills/engineering/clirunner-env/SKILL.md", FLAG + "\n", "",
        "clirunner-env: skills/engineering/README.md marks it *(by hand)*",
    )
    control(
        "control: a quoted flag the standing-cost regex cannot read fails",
        "skills/engineering/clirunner-env/SKILL.md", FLAG, 'disable-model-invocation: "true"',
        "clirunner-env: the frontmatter reads disable-model-invocation=true, but the "
        "standing-cost check's DISABLE_MODEL_INVOCATION_RE reads it the other way",
    )
    bucket_cards = sorted(p.parent.name for p in (ROOT / ORCH).parent.glob("*/SKILL.md"))

    def remove_readme(tree: Path) -> None:
        (tree / ORCH).unlink()
        assert not (tree / ORCH).exists(), f"{ORCH} still present in the copy"

    code, out = run_on_copy(remove_readme)
    print(f"     {out.strip()}".replace("\n", "\n     "))
    missing = [c for c in bucket_cards if f"{c}: {ORCH} does not exist" not in out]
    check(
        f"control: a removed bucket README fails for each of its {len(bucket_cards)} cards",
        code == 1 and bool(bucket_cards) and not missing,
        f"exit {code}, no refusal for {missing} in: {out}",
    )
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "skills").mkdir()
        with redirect_stdout(io.StringIO()):
            code = markers.main(["--root", tmp])
    check("control: a tree with no published card is refused, not passed", code == 1)
    print("")
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}")
        raise SystemExit(1)
    print("PASS: every by-hand marker drift goes red and the live tree is green")


if __name__ == "__main__":
    main()
