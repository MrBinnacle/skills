#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validator", HERE / "validate_packet.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

PASSING_COMMAND = "git rev-parse HEAD"
FAILING_COMMAND = "exit 1"


def expect_structure(name: str, valid: bool):
    data, text = validator.extract(HERE / name)
    errors = validator.validate_structure(data, text)
    assert (not errors) == valid, (name, errors)


def placeholder_cases():
    """TODO in prose is content. TODO alone on a line is unfinished work."""
    data, text = validator.extract(HERE / "fixture-clean.md")

    prose = text + "\nClosed the ticket titled 'sweep the remaining TODO comments'.\n"
    assert not validator.placeholder_tokens(data, prose), "prose mention must pass"
    assert not validator.validate_structure(data, prose)

    for line in ("TODO", "  TBD  ", "- TODO:", "**TODO**"):
        candidate = text + f"\n{line}\n"
        assert validator.placeholder_tokens(data, candidate), f"must reject: {line!r}"

    unfinished = copy.deepcopy(data)
    unfinished["objective"] = "TBD"
    assert "TBD" in validator.placeholder_tokens(unfinished, text), "manifest value must reject"

    assert validator.validate_structure(data, text + "\n__REQUIRED__\n")


def lint_cases():
    """A check that always exits zero must be named as unfailable."""
    vacuous = {"receiver_checks": [{"name": "git-status", "command": "git status --porcelain"}]}
    assert validator.lint_receiver_checks(vacuous), "always-zero check must be flagged"

    failable = {"receiver_checks": [
        {"name": "clean-tree", "command": "git diff --quiet && git diff --cached --quiet"}
    ]}
    assert not validator.lint_receiver_checks(failable), "fail-able check must not be flagged"


def repository_cases():
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        (repo / "README.md").write_text("fixture", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
        head = validator.git(repo, "rev-parse", "HEAD")
        branch = validator.git(repo, "branch", "--show-current")

        clean, _ = validator.extract(HERE / "fixture-clean.md")
        clean["repository"]["head"] = head
        clean["repository"]["branch"] = branch
        errors, _ = validator.validate_repository(clean, repo)
        assert not errors, errors

        stale, _ = validator.extract(HERE / "fixture-stale.md")
        errors, _ = validator.validate_repository(stale, repo)
        assert any("stale HEAD" in e for e in errors), errors

        failed, _ = validator.extract(HERE / "fixture-failed-probe.md")
        failed["repository"]["head"] = head
        failed["repository"]["branch"] = branch
        errors, _ = validator.validate_repository(failed, repo)
        assert any("path probe failed" in e for e in errors), errors

        command_probe_cases(clean, repo)


def command_probe_cases(clean: dict, repo: Path):
    """A command probe supports 'verified' only when the owner authorised it."""
    def with_probe(command: str) -> dict:
        packet = copy.deepcopy(clean)
        packet["claims"] = [{
            "id": "C001", "text": "the suite passes", "status": "verified",
            "probe": {"kind": "command", "value": command},
            "evidence": "observed",
        }]
        return packet

    errors, _ = validator.validate_repository(with_probe(FAILING_COMMAND), repo)
    assert any("absent from the trusted" in e for e in errors), errors

    allowed = {FAILING_COMMAND}
    errors, _ = validator.validate_repository(with_probe(FAILING_COMMAND), repo, allowed)
    assert any("command probe failed" in e for e in errors), errors

    allowed = {PASSING_COMMAND}
    errors, notes = validator.validate_repository(with_probe(PASSING_COMMAND), repo, allowed)
    assert not errors, errors
    assert any("command probe passed" in n for n in notes), notes


def cli_cases():
    """Receive mode must not degrade to silent acceptance without a config."""
    result = subprocess.run(
        ["python", str(HERE / "validate_packet.py"), str(HERE / "fixture-clean.md"),
         "--mode", "receive"],
        text=True, capture_output=True,
    )
    assert result.returncode == 2, result.stdout
    assert "requires --config and --repo-root" in result.stdout, result.stdout


def duplication_case():
    """The pair ships one validator in two directories. They must not drift."""
    names = ("im-down", "im-up")
    for name in names:
        if name == HERE.name:
            continue
        sibling = HERE.parent / name / "validate_packet.py"
        if sibling.exists():
            assert sibling.read_bytes() == (HERE / "validate_packet.py").read_bytes(), \
                f"validator has drifted from {name}"


if __name__ == "__main__":
    expect_structure("fixture-clean.md", True)
    expect_structure("fixture-missing-field.md", False)
    expect_structure("fixture-stale.md", True)
    expect_structure("fixture-failed-probe.md", True)
    placeholder_cases()
    lint_cases()
    repository_cases()
    cli_cases()
    duplication_case()
    print("PASS: clean, stale, incomplete, failed-probe, placeholder, "
          "unfailable-check, command-probe, receive-mode-config, no-drift")
