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


def planted(edit_path: str, old: str, new: str) -> tuple[int, str]:
    """Run the checker on a copy of the live tree with one replacement made."""
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        shutil.copytree(ROOT / "skills", tree / "skills")
        target = tree / edit_path
        text = target.read_text(encoding="utf-8")
        assert old in text, f"control anchor absent in {edit_path}: {old!r}"
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            code = markers.main(["--root", str(tree)])
        return code, out.getvalue()


def control(name: str, edit_path: str, old: str, new: str, expect: str) -> None:
    code, out = planted(edit_path, old, new)
    print(f"     {out.strip()}".replace("\n", "\n     "))
    check(name, code == 1 and expect in out, f"exit {code}, wanted {expect!r} in: {out}")


ENG = "skills/engineering/README.md"
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
        "halt-as-deliverable: skills/engineering/README.md has no line listing it",
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
