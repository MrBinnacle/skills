#!/usr/bin/env python3
"""Controls for check_eval_suite.py's trigger and containment checks."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CHECKER = SCRIPT_DIR / "check_eval_suite.py"
REPO_ROOT = SCRIPT_DIR.parent
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def run_checker(suite: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(suite)], capture_output=True, text=True
    )


def write_case(root: Path, name: str, case_type: str, skill: str, graders: list[str]) -> Path:
    case = root / "evals" / name
    graders_dir = case / "graders"
    graders_dir.mkdir(parents=True)
    (case / "prompt.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: Fixture eval case\n"
        f"tags: [{case_type}, {skill}]\n"
        'plugins: ["../.."]\n'
        "---\n\n"
        "Fixture prompt.\n",
        encoding="utf-8",
    )
    for grader_name, contents in enumerate(graders):
        (graders_dir / f"grader-{grader_name}.md").write_text(contents, encoding="utf-8")
    return case


LLM_GRADER = "---\ntype: llm\n---\n\nPASS if the answer is correct.\n"


def skill_grader(skill: str, *, containment: bool = False) -> str:
    bounds = "\nmin: 0\nmax: 0\narm: both" if containment else ""
    return (
        "---\n"
        "type: tool_used\n"
        "tool: Skill\n"
        f"input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?{skill}\"'{bounds}\n"
        "---\n\nSkill invocation check.\n"
    )


def make_plugin(root: Path) -> None:
    manifest = root / ".claude-plugin" / "plugin.json"
    manifest.parent.mkdir()
    manifest.write_text('{"name": "fixture"}\n', encoding="utf-8")


def case_live_suite_passes() -> None:
    result = run_checker(REPO_ROOT / "skills" / "orchestration" / "evals")
    check("the live orchestration eval suite passes", result.returncode == 0, result.stderr)


def case_bad_plugin_path_is_rejected(root: Path) -> None:
    make_plugin(root)
    write_case(root, "fire", "should-fire", "fixture", [LLM_GRADER, skill_grader("fixture")])
    prompt = root / "evals" / "fire" / "prompt.md"
    prompt.write_text(prompt.read_text(encoding="utf-8").replace('../..', '..'), encoding="utf-8")
    result = run_checker(root / "evals")
    check(
        "a plugin path that stops at evals is rejected",
        result.returncode != 0 and "does not resolve to a plugin root" in result.stderr,
        result.stderr,
    )


def case_missing_invocation_grader_is_rejected(root: Path) -> None:
    make_plugin(root)
    write_case(root, "fire", "should-fire", "fixture", [LLM_GRADER])
    write_case(
        root,
        "no-fire",
        "should-not-fire",
        "fixture",
        [LLM_GRADER, skill_grader("fixture", containment=True)],
    )
    result = run_checker(root / "evals")
    check(
        "a should-fire case without an invocation grader is rejected",
        result.returncode != 0 and "needs a Skill invocation grader" in result.stderr,
        result.stderr,
    )


def case_missing_containment_grader_is_rejected(root: Path) -> None:
    make_plugin(root)
    write_case(root, "fire", "should-fire", "fixture", [LLM_GRADER, skill_grader("fixture")])
    write_case(root, "no-fire", "should-not-fire", "fixture", [LLM_GRADER])
    result = run_checker(root / "evals")
    check(
        "a should-not-fire case without a containment grader is rejected",
        result.returncode != 0 and "needs a both-arm Skill containment grader" in result.stderr,
        result.stderr,
    )


def main() -> None:
    case_live_suite_passes()
    for case in (
        case_bad_plugin_path_is_rejected,
        case_missing_invocation_grader_is_rejected,
        case_missing_containment_grader_is_rejected,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            case(Path(tmp))

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): {', '.join(FAILURES)}", file=sys.stderr)
        raise SystemExit(1)
    print("PASS: eval-suite pre-flight controls, all cases correct")


if __name__ == "__main__":
    main()
