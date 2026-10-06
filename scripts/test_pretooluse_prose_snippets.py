#!/usr/bin/env python3
"""Run the detector this card prescribes, read straight out of SKILL.md.

The card's remedy is code a reader copies into their own guard, so a defect in
it ships to every guard built from the card. This suite executes the
``python`` fences in SKILL.md as written and checks the cases a copied guard
must get right.
"""
from __future__ import annotations

import re
from pathlib import Path

CARD = Path(__file__).resolve().parent.parent / "skills" / "engineering" / "pretooluse-prose"
FENCE = re.compile(r"^```python\n(.*?)^```", re.DOTALL | re.MULTILINE)


def load_card_detector() -> dict:
    text = (CARD / "SKILL.md").read_text(encoding="utf-8")
    namespace: dict = {"re": re}
    for block in FENCE.findall(text):
        if block.lstrip().startswith("except"):
            continue  # a fragment of a try statement, not a definition
        exec(block, namespace)  # noqa: S102 -- trusted, in-repo card text
    return namespace


def reports_create(ns: dict, shell: str) -> bool:
    """Does the card's detector find `gh issue create` in command position?"""
    if "runs" in ns:
        return bool(ns["runs"](shell, ns["CREATE_RE"]))
    return bool(ns["CREATE_RE"].search(shell))


def tab_indented_heredoc_keeps_next_command(ns: dict) -> None:
    cmd = "cat <<-EOF\n\tprose\n\tEOF\ngh issue create --title x"
    shell, body = ns["split_shell_and_body"](cmd)
    assert "gh issue create" in shell, f"real command swallowed: shell={shell!r}"
    assert "gh issue create" not in body, f"real command read as body: {body!r}"
    assert reports_create(ns, shell), "real command after <<- heredoc not detected"


def plain_heredoc_still_split(ns: dict) -> None:
    cmd = "git commit -F- <<'EOF'\nUse `gh issue create` here.\nEOF\necho done"
    shell, body = ns["split_shell_and_body"](cmd)
    assert "gh issue create" in body and "gh issue create" not in shell, (shell, body)
    assert "echo done" in shell, shell


def plain_heredoc_ignores_tab_indented_terminator(ns: dict) -> None:
    # Only `<<-` strips tabs; in a plain `<<EOF` a `\tEOF` line is body text.
    cmd = "cat <<EOF\nline\n\tEOF\ngh issue create in prose\nEOF\necho ok"
    shell, body = ns["split_shell_and_body"](cmd)
    assert "gh issue create" in body, f"plain heredoc ended early: body={body!r}"
    assert not reports_create(ns, shell), f"prose read as command: shell={shell!r}"
    assert "echo ok" in shell, shell


def quoted_separator_is_not_a_command_position(ns: dict) -> None:
    for cmd in (
        'echo "step one; gh issue create later"',
        "echo 'a && gh issue create'",
        'git commit -m "fixed it; gh issue create --title follow-up"',
    ):
        assert not reports_create(ns, cmd), f"quoted separator read as command: {cmd!r}"


def real_commands_still_detected(ns: dict) -> None:
    for cmd in (
        "gh issue create --title x",
        "cd repo && gh issue create",
        'echo "a;b"; gh issue create',
        "FOO=1 gh pr create",
        "out=$(gh issue create --title x)",
        'echo "$(gh issue create)"',
    ):
        assert reports_create(ns, cmd), f"real command missed: {cmd!r}"
    for cmd in ("gh issue list", "echo gh issue create", "ls"):
        assert not reports_create(ns, cmd), f"non-invocation reported: {cmd!r}"


CASES = (
    tab_indented_heredoc_keeps_next_command,
    plain_heredoc_still_split,
    plain_heredoc_ignores_tab_indented_terminator,
    quoted_separator_is_not_a_command_position,
    real_commands_still_detected,
)


def main() -> int:
    ns = load_card_detector()
    failed = []
    for case in CASES:
        try:
            case(ns)
        except AssertionError as exc:
            failed.append(f"{case.__name__}: {exc}")
    if failed:
        print("FAIL:\n  " + "\n  ".join(failed))
        return 1
    print("PASS: " + ", ".join(c.__name__ for c in CASES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
