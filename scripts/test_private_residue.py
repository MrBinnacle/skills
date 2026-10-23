#!/usr/bin/env python3
"""Suite for private_residue.py: a private term is refused without being printed.

The term here is synthetic. The real terms never enter the tree (#580), so the
suite plants a made-up two-word term through the environment and builds every
poison tree in a temp directory. `RESIDUE_PRIVATE_OVERLAY` points at a missing
file in every run, so a maintainer's own overlay never decides a result.

    Cases:
      - the hyphenated, spaced, underscored, mixed-case and run-together forms
        of the term in a file's contents are each refused;
      - a word that only contains the term's first word passes;
      - a tracked path that carries the term is refused, with clean contents;
      - the overlay file supplies terms the same way the environment does;
      - no refusal prints the term in any form;
      - with no term loaded, `--require` exits 2 and a plain run passes.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "private_residue.py"
TERM = "quokka lantern"
FORMS = ("quokka-lantern", "quokka lantern", "Quokka_Lantern", "QUOKKA LANTERN", "quokkalantern")
FAILURES: list[str] = []


def check(case: str, ok: bool, detail: str = "") -> None:
    if ok:
        print(f"  ok   {case}")
    else:
        FAILURES.append(case)
        print(f"  FAIL {case}: {detail}")


def env(terms: str | None, overlay: Path) -> dict[str, str]:
    out = {k: v for k, v in os.environ.items() if k != "RESIDUE_PRIVATE_TERMS"}
    out["RESIDUE_PRIVATE_OVERLAY"] = str(overlay)
    if terms is not None:
        out["RESIDUE_PRIVATE_TERMS"] = terms
    return out


def run(repo: Path, environ: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", env=environ,
    )


def leaks(result: subprocess.CompletedProcess[str]) -> bool:
    output = (result.stdout + result.stderr).lower()
    return any(form.lower() in output for form in FORMS) or "quokka" in output


def make_repo(root: Path, files: dict[str, str]) -> Path:
    root.mkdir()
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    for name, text in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        missing = tmp / "no-overlay"
        with_term = env(TERM, missing)

        for i, form in enumerate(FORMS):
            repo = make_repo(tmp / f"form{i}", {"notes.md": f"line one\nsee the {form} notes\n"})
            result = run(repo, with_term, "--all")
            check(
                f"contents form {form!r} is refused at its line",
                result.returncode == 1 and "notes.md:2: private term 1" in result.stdout,
                result.stdout + result.stderr,
            )
            check(f"the refusal for {form!r} prints no form of the term", not leaks(result), result.stdout)

        repo = make_repo(tmp / "near", {"notes.md": "quokkas and lanterns, quokka lanterns\n"})
        result = run(repo, with_term, "--all")
        check("a longer word is not the term", result.returncode == 0, result.stdout)

        repo = make_repo(tmp / "path", {"docs/quokka-lantern/index.md": "clean contents\n"})
        result = run(repo, with_term, "--all")
        check(
            "a path carrying the term is refused",
            result.returncode == 1 and "tracked path 1 (git ls-files order): private term 1" in result.stdout and not leaks(result),
            result.stdout,
        )
        result = run(repo, with_term)
        check("paths are read even when no file is named", result.returncode == 1, result.stdout)

        overlay = tmp / "overlay.local"
        overlay.write_text("# private terms, one per line\nquokka lantern\n", encoding="utf-8")
        repo = make_repo(tmp / "overlay", {"notes.md": "the Quokka-Lantern notes\n"})
        result = run(repo, env(None, overlay), "notes.md")
        check("the overlay file supplies a term", result.returncode == 1 and not leaks(result), result.stdout)

        clean = make_repo(tmp / "clean", {"notes.md": "nothing private here\n"})
        result = run(clean, with_term, "--all", "--require")
        check("a clean tree passes with a term loaded", result.returncode == 0 and "PASS:" in result.stdout,
              result.stdout)
        result = run(clean, env(None, missing), "--all", "--require")
        check(
            "--require with no term loaded exits 2 and names the secret",
            result.returncode == 2 and "RESIDUE_PRIVATE_TERMS" in result.stdout,
            result.stdout,
        )
        result = run(clean, env(None, missing), "--all")
        check("a plain run with no term loaded passes", result.returncode == 0, result.stdout)

    if FAILURES:
        print(f"FAILED: {len(FAILURES)} case(s): " + ", ".join(FAILURES))
        raise SystemExit(1)
    print("PASS: private residue check refuses each form of a planted term in contents and paths, and never prints it")


if __name__ == "__main__":
    main()
