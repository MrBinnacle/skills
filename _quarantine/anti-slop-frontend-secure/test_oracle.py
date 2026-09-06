#!/usr/bin/env python3
"""Run the fixtures and the ablation arms against the oracle.

HOW THE FIXTURES REACH THE PARSER
    `SECURITY.md` commitment 3 declares a closed format vocabulary for everything
    inside a skill folder: `.md`, `.txt`, `.py`, `.json`. An `.html` fixture is
    outside it, so the fixture bodies are held as strings in `fixtures.json` and
    written to a temporary path here before the oracle opens them. The oracle
    parses a real file from a real path; only the delivery changed, and no policy
    was widened to allow it.

THE REGEX CONTROL, WHICH IS THE POINT OF THE SUITE
    The requirement this suite exists to hold is that a fixture a regular
    expression could settle is not exercising the oracle. A test that only
    asserted the oracle's own verdict could not tell a parser-backed check from
    a byte scan wearing one's clothes: both would be green.

    So every fixture carrying a `regex_probe` states the naive pattern a
    reasonable person would reach for and the verdict that pattern returns.
    `test_regex_probe_disagrees_with_the_oracle` runs the probe and asserts it
    gets the OPPOSITE answer. A fixture that stops being parser-discriminating --
    because someone rewrote it, or because a gate quietly became a string match --
    turns this suite red, and it says which fixture and in which direction.

    `test_every_gate_has_a_parser_discriminating_fixture` is the coverage half:
    it refuses a green run in which any gate has lost its probe entirely, which
    is the failure a per-fixture assertion cannot see.

RUN
    python test_oracle.py            # unittest, no third-party runner
    python -m unittest test_oracle   # the same suite through the module runner
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit_frontend  # noqa: E402
import emit_csp  # noqa: E402

FIXTURES = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))
ABLATIONS = json.loads((HERE / "ablations.json").read_text(encoding="utf-8"))

ALL_GATES = ("A", "B", "C", "D", "E", "F")


def materialise(directory: Path, name: str, body: str) -> Path:
    """Write one held body to a real path so the oracle reads a real file."""
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


def run_oracle(
    directory: Path, fixture: dict[str, Any], advisory: Path | None = None
) -> tuple[dict[str, Any], int]:
    path = materialise(directory, fixture["filename"], fixture["body"])
    return audit_frontend.audit(
        path,
        fixture["body"],
        fixture.get("mode", "artifact"),
        list(fixture.get("allowlist", [])),
        advisory,
        stamp=False,
    )


def gate_of(receipt: dict[str, Any], letter: str) -> dict[str, Any]:
    for record in receipt["gates"]:
        if record["gate"] == letter:
            return record
    raise AssertionError(f"receipt states no gate {letter}")


class FixtureSuite(unittest.TestCase):
    """One passing and one failing case per gate, plus the parser controls."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    # -------------------------------------------------- per-fixture verdicts

    def test_each_fixture_gets_its_stated_verdict(self) -> None:
        for fixture in FIXTURES["fixtures"]:
            with self.subTest(fixture=fixture["id"]):
                receipt, code = run_oracle(self.tmp, fixture)
                expected = fixture["expect"]

                if expected == "refused":
                    self.assertEqual(receipt["verdict"], "REFUSED", fixture["why"])
                    self.assertEqual(code, audit_frontend.EXIT_REFUSED)
                    self.assertEqual(receipt["gates_run"], 0)
                    continue

                letter = fixture["gate"]
                record = gate_of(receipt, letter)
                if expected == "pass":
                    self.assertTrue(
                        record["pass"],
                        f"{fixture['id']} should pass gate {letter}: "
                        f"{record['issues']}",
                    )
                else:
                    self.assertFalse(
                        record["pass"],
                        f"{fixture['id']} should fail gate {letter}. {fixture['why']}",
                    )
                    for needle in fixture.get("expect_issue_contains", []):
                        self.assertTrue(
                            any(needle in issue for issue in record["issues"]),
                            f"{fixture['id']} gate {letter} states no issue "
                            f"mentioning {needle!r}: {record['issues']}",
                        )

    def test_advisory_findings_reported_without_blocking(self) -> None:
        """Artifact mode reports what netlify mode blocks on, and passes."""
        for fixture in FIXTURES["fixtures"]:
            if not fixture.get("expect_advisory_findings"):
                continue
            with self.subTest(fixture=fixture["id"]):
                receipt, code = run_oracle(self.tmp, fixture)
                record = gate_of(receipt, "E")
                self.assertTrue(record["pass"])
                self.assertFalse(record["enforcing"])
                self.assertTrue(
                    record["advisory_findings"],
                    "artifact mode should still report what it does not block on",
                )
                self.assertEqual(code, audit_frontend.EXIT_PASS)

    # ------------------------------------------------------ the regex control

    def test_regex_probe_disagrees_with_the_oracle(self) -> None:
        """Every probe-carrying fixture is one a byte scan settles wrongly.

        This is the assertion behind the claim that the oracle is parser-backed.
        If the probe and the oracle ever agree, the fixture has stopped
        discriminating and the suite says so by name.

        The probe is compared against the oracle's OBSERVED verdict, not only
        against the fixture's declared one. An earlier edition compared it
        against the declaration alone, and a mutation that turned Gate C into a
        byte scan left this test green: comparing a probe with a declaration is
        a statement about the fixture, and the claim being made is about the
        oracle. Both comparisons are kept -- the declaration catches a fixture
        that drifted, the observation catches a gate that stopped parsing.
        """
        probed = 0
        for fixture in FIXTURES["fixtures"]:
            probe = fixture.get("regex_probe")
            if probe is None:
                continue
            probed += 1
            with self.subTest(fixture=fixture["id"]):
                pattern = re.compile(probe["pattern"])
                naive_hit = bool(pattern.search(fixture["body"]))
                # A probe hunts either a FORBIDDEN thing, where a hit reads as a
                # failure, or a REQUIRED one, where a hit reads as a pass. Gate A
                # needs the second polarity: a byte scan that finds `<html` calls
                # the structure sound. Assuming the first polarity for every probe
                # inverts that fixture's stated verdict and makes a correct probe
                # look broken.
                hit_means = probe.get("hit_means", "fail")
                miss_means = "pass" if hit_means == "fail" else "fail"
                naive_verdict = hit_means if naive_hit else miss_means

                self.assertEqual(
                    naive_verdict,
                    probe["naive_verdict"],
                    f"{fixture['id']}: the stated naive verdict is "
                    f"{probe['naive_verdict']!r} but the pattern returns "
                    f"{naive_verdict!r}. The probe no longer describes what a byte "
                    "scan does to this body.",
                )
                self.assertNotEqual(
                    naive_verdict,
                    fixture["expect"],
                    f"{fixture['id']}: a byte scan and this fixture's declared "
                    f"verdict now agree ({naive_verdict}), so the fixture no "
                    f"longer exercises the parser. {probe['note']}",
                )

                receipt, _ = run_oracle(self.tmp, fixture)
                observed = "pass" if gate_of(receipt, fixture["gate"])["pass"] else "fail"
                self.assertNotEqual(
                    naive_verdict,
                    observed,
                    f"{fixture['id']}: a byte scan and the ORACLE now agree "
                    f"({naive_verdict}) on gate {fixture['gate']}. The gate has "
                    f"stopped parsing and started matching strings. "
                    f"{probe['note']}",
                )
        self.assertGreater(probed, 0, "no fixture carries a regex probe")

    def test_every_gate_has_a_parser_discriminating_fixture(self) -> None:
        """Coverage: no gate may lose its probe and stay green."""
        probed = {
            f["gate"] for f in FIXTURES["fixtures"] if f.get("regex_probe") is not None
        }
        missing = [g for g in ALL_GATES if g not in probed]
        self.assertEqual(
            missing,
            [],
            f"gate(s) {missing} have no fixture a regular expression settles "
            "wrongly, so nothing measures whether they parse or match strings",
        )

    def test_every_gate_has_a_passing_and_a_failing_fixture(self) -> None:
        for letter in ALL_GATES:
            with self.subTest(gate=letter):
                verdicts = {
                    f["expect"] for f in FIXTURES["fixtures"] if f["gate"] == letter
                }
                self.assertIn("pass", verdicts, f"gate {letter} has no passing fixture")
                self.assertIn("fail", verdicts, f"gate {letter} has no failing fixture")


class ReceiptSuite(unittest.TestCase):
    """A receipt names which gates ran, on what input, with what result."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.clean = next(
            f for f in FIXTURES["fixtures"] if f["id"] == "A-pass-plain"
        )

    def test_receipt_states_input_gates_and_result(self) -> None:
        receipt, _ = run_oracle(self.tmp, self.clean)
        for field in (
            "schema",
            "tool",
            "input",
            "input_sha256",
            "mode",
            "allowlist",
            "verdict",
            "gates",
            "gates_run",
            "advisory_status",
        ):
            self.assertIn(field, receipt, f"receipt states no {field}")
        self.assertEqual(receipt["gates_run"], len(ALL_GATES))
        self.assertEqual([g["gate"] for g in receipt["gates"]], list(ALL_GATES))
        for record in receipt["gates"]:
            self.assertIn("name", record)
            self.assertIn("pass", record)
            self.assertIn("issues", record)

    def test_receipt_is_reproducible_without_a_timestamp(self) -> None:
        first, _ = run_oracle(self.tmp, self.clean)
        second, _ = run_oracle(self.tmp, self.clean)
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        self.assertNotIn("generated_at", first)

    def test_receipt_digest_binds_the_receipt_to_the_bytes_audited(self) -> None:
        """A receipt whose digest floats free of the input proves nothing."""
        clean, _ = run_oracle(self.tmp, self.clean)
        altered = dict(self.clean, body=self.clean["body"] + "<!-- edited -->\n")
        changed, _ = run_oracle(self.tmp, altered)
        self.assertNotEqual(clean["input_sha256"], changed["input_sha256"])


class AblationSuite(unittest.TestCase):
    """The five declared arms, executed rather than described."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.receipts: dict[int, dict[str, Any]] = {}
        self.codes: dict[int, int] = {}
        for arm in ABLATIONS["arms"]:
            advisory_path: Path | None = None
            if "advisory_raw" in arm:
                advisory_path = self.tmp / f"advisory-{arm['arm']}.json"
                advisory_path.write_text(arm["advisory_raw"], encoding="utf-8")
            elif arm.get("advisory") is not None:
                advisory_path = self.tmp / f"advisory-{arm['arm']}.json"
                advisory_path.write_text(
                    json.dumps(arm["advisory"]), encoding="utf-8"
                )
            path = materialise(self.tmp, arm["filename"], arm["document"])
            receipt, code = audit_frontend.audit(
                path,
                arm["document"],
                arm["mode"],
                list(arm["allowlist"]),
                advisory_path,
                stamp=False,
            )
            self.receipts[arm["arm"]] = receipt
            self.codes[arm["arm"]] = code

    def test_five_arms_are_declared(self) -> None:
        self.assertEqual(len(ABLATIONS["arms"]), 5)
        self.assertEqual(
            [a["id"] for a in ABLATIONS["arms"]],
            [
                "with-taste-provider",
                "without-taste-provider",
                "out-of-scope-routing",
                "provider-failure-degrades",
                "security-overrides-unsafe-advice",
            ],
        )

    def test_each_arm_matches_its_declared_expectation(self) -> None:
        for arm in ABLATIONS["arms"]:
            with self.subTest(arm=arm["id"]):
                receipt = self.receipts[arm["arm"]]
                expected = arm["expect"]
                self.assertEqual(receipt["verdict"], expected["verdict"])
                self.assertEqual(self.codes[arm["arm"]], expected["exit_code"])
                self.assertEqual(
                    receipt["advisory_status"], expected["advisory_status"]
                )
                if "advisory_note_count" in expected:
                    self.assertEqual(
                        len(receipt["advisory_notes"]),
                        expected["advisory_note_count"],
                    )
                if "gates_run" in expected:
                    self.assertEqual(receipt["gates_run"], expected["gates_run"])
                if "gates_failed" in expected:
                    self.assertEqual(
                        receipt["gates_failed"], expected["gates_failed"]
                    )
                if "security_overrode_advisory" in expected:
                    self.assertEqual(
                        receipt["security_overrode_advisory"],
                        expected["security_overrode_advisory"],
                    )

    def test_provider_presence_does_not_move_a_single_gate(self) -> None:
        """Arms 1, 2 and 4 must produce the SAME security verdict object.

        This is the authority split as an equality rather than as a sentence. A
        provider that is present, absent or broken leaves the gates untouched;
        if any of the three ever diverges, the split has stopped holding.
        """
        for arm in ABLATIONS["arms"]:
            reference = arm["expect"].get("gates_identical_to_arm")
            if reference is None:
                continue
            with self.subTest(arm=arm["id"]):
                self.assertEqual(
                    json.dumps(self.receipts[arm["arm"]]["gates"], sort_keys=True),
                    json.dumps(self.receipts[reference]["gates"], sort_keys=True),
                    f"{arm['id']} produced different gate results from arm "
                    f"{reference}, so the provider moved a security verdict",
                )

    def test_no_arm_lets_an_advisory_note_change_a_verdict(self) -> None:
        for arm in ABLATIONS["arms"]:
            receipt = self.receipts[arm["arm"]]
            if receipt["verdict"] == "REFUSED":
                continue
            with self.subTest(arm=arm["id"]):
                self.assertFalse(receipt["advisory_affected_verdict"])

    def test_unsafe_advice_is_overridden_and_the_receipt_says_so(self) -> None:
        receipt = self.receipts[5]
        self.assertEqual(receipt["verdict"], "FAIL")
        self.assertTrue(receipt["security_overrode_advisory"])
        self.assertTrue(
            any("innerHTML" in note["note"] for note in receipt["advisory_notes"]),
            "arm 5 requires a provider note that recommends a blocked pattern",
        )
        self.assertFalse(gate_of(receipt, "C")["pass"])


class CspSuite(unittest.TestCase):
    """The emitter derives a policy and validates one."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.clean = ABLATIONS["arms"][0]["document"]
        self.path = materialise(self.tmp, "csp.html", self.clean)

    def surface(self, body: str) -> emit_csp.Surface:
        return emit_csp.Surface(audit_frontend.parse(body))

    def test_emitted_policy_denies_by_default_and_pins_inline_scripts(self) -> None:
        directives = emit_csp.derive(self.surface(self.clean), "netlify", [])
        self.assertEqual(directives["default-src"], ["'none'"])
        self.assertEqual(directives["connect-src"], ["'none'"])
        self.assertEqual(directives["object-src"], ["'none'"])
        self.assertEqual(directives["frame-ancestors"], ["'none'"])
        self.assertTrue(
            any(part.startswith("'sha256-") for part in directives["script-src"]),
            "an inline script must be pinned by digest, not waved through",
        )
        self.assertNotIn("'unsafe-inline'", directives["script-src"])

    def test_meta_rendering_drops_the_directive_meta_cannot_carry(self) -> None:
        directives = emit_csp.derive(self.surface(self.clean), "artifact", [])
        rendered = emit_csp.render_policy(directives, emit_csp.META_UNSUPPORTED)
        self.assertNotIn("frame-ancestors", rendered)
        self.assertIn("default-src 'none'", rendered)

    def test_emitted_policy_validates_against_the_document_it_came_from(self) -> None:
        surface = self.surface(self.clean)
        policy = emit_csp.render_policy(emit_csp.derive(surface, "netlify", []))
        violations, _ = emit_csp.validate_policy(policy, surface, "netlify")
        self.assertEqual(violations, [])

    def test_validation_refuses_unsafe_inline_and_an_unpinned_script(self) -> None:
        surface = self.surface(self.clean)
        violations, _ = emit_csp.validate_policy(
            "default-src 'none'; script-src 'unsafe-inline'", surface, "netlify"
        )
        self.assertTrue(any("unsafe-inline" in v for v in violations))
        self.assertTrue(any("does not pin an inline script" in v for v in violations))

    def test_validation_refuses_a_policy_that_omits_a_host_the_page_reaches(
        self,
    ) -> None:
        body = self.clean.replace(
            'document.getElementById("count").textContent = "0 orders";',
            'fetch("https://api.other.example/v1");',
        )
        surface = self.surface(body)
        policy = "default-src 'none'; connect-src 'none'"
        violations, _ = emit_csp.validate_policy(policy, surface, "netlify")
        self.assertTrue(any("api.other.example" in v for v in violations))

    def test_emitter_refuses_an_input_that_is_not_an_artifact(self) -> None:
        path = materialise(self.tmp, "notes.py", "x = 1\n")
        receipt, code, state = emit_csp.build_receipt(
            path, "x = 1\n", "emit", "netlify", [], stamp=False
        )
        self.assertEqual(receipt["verdict"], "REFUSED")
        self.assertEqual(code, audit_frontend.EXIT_REFUSED)
        self.assertNotEqual(state, "ready")


class CommandLineSuite(unittest.TestCase):
    """Both scripts run as commands, because that is how SKILL.md names them."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HERE / script), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_audit_exit_codes_distinguish_pass_fail_and_refusal(self) -> None:
        cases = [
            ("A-pass-plain", audit_frontend.EXIT_PASS),
            ("C-fail-sink-in-script", audit_frontend.EXIT_FAIL),
            ("SCOPE-refuse-python-input", audit_frontend.EXIT_REFUSED),
        ]
        for fixture_id, expected in cases:
            fixture = next(f for f in FIXTURES["fixtures"] if f["id"] == fixture_id)
            path = materialise(self.tmp, fixture["filename"], fixture["body"])
            with self.subTest(fixture=fixture_id):
                result = self.run_script(
                    "audit_frontend.py",
                    str(path),
                    "--mode",
                    fixture["mode"],
                    "--no-timestamp",
                )
                self.assertEqual(result.returncode, expected, result.stderr)
                json.loads(result.stdout)

    def test_emit_csp_prints_a_headers_block(self) -> None:
        arm = ABLATIONS["arms"][0]
        path = materialise(self.tmp, "cli.html", arm["document"])
        result = self.run_script(
            "emit_csp.py", str(path), "--action", "emit", "--deploy", "netlify",
            "--no-timestamp",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["rendered_as"], "_headers")
        self.assertIn("Content-Security-Policy:", receipt["rendered"])


class SkillContractSuite(unittest.TestCase):
    """The card's own obligations, checked from inside the card.

    `scripts/validate_conformance.py` runs O1 and O3 over the PUBLISHED tree and
    this candidate sits in `_quarantine/`, so nothing upstream checks it yet.
    Waiting for promotion to find out would mean discovering at promotion that
    the card was never conformant. These assertions are the same two rules,
    applied here, now.
    """

    def test_every_shipped_script_is_named_in_skill_md(self) -> None:
        skill = (HERE / "SKILL.md").read_text(encoding="utf-8")
        scripts = [
            p.name for p in HERE.rglob("*.py") if "__pycache__" not in p.parts
        ]
        self.assertTrue(scripts)
        unnamed = [name for name in scripts if name not in skill]
        self.assertEqual(
            unnamed,
            [],
            f"O3: SKILL.md names no {unnamed}. SECURITY.md commitment 3 says a "
            "reader can read a script before running it, which requires the card "
            "to name it.",
        )

    def test_every_shipped_file_is_a_declared_readable_format(self) -> None:
        """O1, asked exactly the way the repository gate asks it.

        `scripts/validate_skill_formats.py` puts the ignore question to git and
        judges only what is IN the repository, because a file git ignores is
        never in the published tree. A local restatement that skips that step
        reddens on a `.mypy_cache/` an editor dropped here and on nothing a
        reader would ever receive, and its own docstring names that outcome: a
        guard that cries wolf locally trains its reader to route around it.
        """
        allowed = {".md", ".txt", ".py", ".json"}
        candidates = [
            p
            for p in HERE.rglob("*")
            if p.is_file() and p.suffix not in allowed and "__pycache__" not in p.parts
        ]
        if candidates:
            ignored = subprocess.run(
                ["git", "-C", str(HERE), "check-ignore", "--stdin", "-z"],
                input="\0".join(str(p) for p in candidates),
                capture_output=True,
                text=True,
            )
            # Exit 0 means some paths matched, 1 means none did. Anything else
            # is an error, and an error must never subtract from what is judged.
            reported = (
                {line for line in ignored.stdout.split("\0") if line}
                if ignored.returncode in (0, 1)
                else set()
            )
            candidates = [p for p in candidates if str(p) not in reported]
        offenders = sorted(p.name for p in candidates)
        self.assertEqual(
            offenders, [], f"O1: {offenders} are outside the declared vocabulary"
        )

    def test_description_is_within_the_published_bar(self) -> None:
        text = (HERE / "SKILL.md").read_text(encoding="utf-8")
        block = re.match(r"\A---\r?\n(.*?)\r?\n---", text, re.S)
        self.assertIsNotNone(block, "SKILL.md carries no frontmatter")
        found = re.search(r"^description:\s*(\S.*?)\s*$", block.group(1), re.M)
        self.assertIsNotNone(found, "SKILL.md states no description")
        value = found.group(1)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        self.assertLessEqual(
            len(value),
            200,
            f"the description is {len(value)} characters, over the published bar "
            "of 200 that scripts/validate_card_files.py enforces",
        )

    def test_the_authority_split_is_stated_in_skill_md(self) -> None:
        skill = (HERE / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "Security may block completion; subjective beauty may not.",
            skill,
            "the authority split is the stable contract and must stay in SKILL.md",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
