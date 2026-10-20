"""Offline suite for finish_changelog.py (issue #330).

What this pins
    1. The rewrite. On the shape `changeset version` writes (a bare
       `## X.Y.Z` section between `# Changelog` and the preamble), the
       output is a literal expected file: dated heading, preamble on top,
       older sections untouched. The fixture is cut from a live
       `npm run version` run on 2026-10-20, so the indented bullet
       continuations and whitespace-only lines are the real ones.
    2. Release gate G4 refuses the raw output and accepts the finished one.
    3. Idempotence. A second run is a no-op, and so is a run on this repo's
       own CHANGELOG.md, whose newest section is already dated.
    4. CRLF survives, and an unexpected first heading is refused.
    5. The command line, as `npm run version` calls it, rewrites the file
       and exits 0, and exits 1 on a file it does not understand.

Run:  python scripts/test_finish_changelog.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from finish_changelog import finish_changelog  # noqa: E402
from release_gate import gate_changelog_section  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "finish_changelog.py"
REPO = SCRIPT.parent.parent

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"ok   {name}")
    else:
        print(f"FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


PREAMBLE = (
    "All notable changes to the collection. A release is a delivery event: changed cards reach\n"
    "installed users when a version is released, not on every merge to `main`. See\n"
    "[ADR 0002](docs/adr/0002-a-release-is-a-delivery-event.md) for what a version promises.\n"
)

OLDER = (
    "## v3.1.0 - 2026-10-17\n"
    "\n"
    "### Minor Changes\n"
    "\n"
    "- [#350](https://github.com/MrBinnacle/skills/pull/350) Rename the domain glossary.\n"
)

ENTRY = (
    "### Patch Changes\n"
    "\n"
    "- [#507](https://github.com/MrBinnacle/skills/pull/507) Mark the two #337 entries.\n"
    "\n"
    "- [#499](https://github.com/MrBinnacle/skills/pull/499) Tighten the Linear card:\n"
    "  \n"
    "  - take each write's read-back from a fresh query;\n"
    "  - give every count its coverage.\n"
    "  \n"
    "  A duplicated absence reminder is cut from `object-model.md`.\n"
)

RAW = "# Changelog\n\n## 3.1.1\n\n" + ENTRY + "\n" + PREAMBLE + "\n" + OLDER

EXPECTED = (
    "# Changelog\n\n" + PREAMBLE + "\n## v3.1.1 - 2026-10-20\n\n" + ENTRY + "\n" + OLDER
)


def g4_errors(text: str, version: str) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "CHANGELOG.md").write_text(text, encoding="utf-8", newline="")
        errors: list[str] = []
        gate_changelog_section(Path(tmp), errors, version)
        return errors


def rewrite_cases() -> None:
    out = finish_changelog(RAW, "3.1.1", "2026-10-20")
    check("the raw changesets output becomes the expected file", out == EXPECTED, repr(out))
    check(
        "the preamble sits above the first release heading",
        out.split("\n## ", 1)[0].endswith(PREAMBLE),
    )
    raw_errors = g4_errors(RAW, "3.1.1")
    check(
        "G4 refuses the raw changesets output as undated",
        len(raw_errors) == 1 and "carries no release date" in raw_errors[0],
        repr(raw_errors),
    )
    check("G4 accepts the finished output", g4_errors(out, "3.1.1") == [], repr(g4_errors(out, "3.1.1")))
    check("a second run is a no-op", finish_changelog(out, "3.1.1", "2026-10-21") == out)

    real = (REPO / "CHANGELOG.md").read_bytes().decode("utf-8")
    version = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["version"]
    check(
        "this repo's dated CHANGELOG.md is left byte-for-byte alone",
        finish_changelog(real, version, "2026-10-20") == real,
    )

    crlf = RAW.replace("\n", "\r\n")
    crlf_out = finish_changelog(crlf, "3.1.1", "2026-10-20")
    check("CRLF line endings survive", crlf_out == EXPECTED.replace("\n", "\r\n"), repr(crlf_out))

    for name, text in (
        ("a different version's bare heading", RAW.replace("## 3.1.1", "## 3.2.0")),
        ("no section heading at all", "# Changelog\n\n" + PREAMBLE),
    ):
        try:
            finish_changelog(text, "3.1.1", "2026-10-20")
        except ValueError:
            check(f"refuses {name}", True)
        else:
            check(f"refuses {name}", False, "no ValueError")


def run_cli(changelog: str, version: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")
        Path(tmp, "CHANGELOG.md").write_text(changelog, encoding="utf-8", newline="")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", tmp, "--date", "2026-10-20"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, Path(tmp, "CHANGELOG.md").read_bytes().decode("utf-8")


def cli_cases() -> None:
    code, written = run_cli(RAW, "3.1.1")
    check("the command line writes the finished file and exits 0", (code, written) == (0, EXPECTED))
    code, written = run_cli(RAW, "9.9.9")
    check(
        "the command line exits 1 and leaves the file alone on a heading it does not expect",
        (code, written) == (1, RAW),
    )


def main() -> int:
    rewrite_cases()
    cli_cases()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED")
        return 1
    print(
        "PASS: the changesets section is dated, the preamble stays on top, "
        "G4 accepts the result, and a second run changes nothing"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
