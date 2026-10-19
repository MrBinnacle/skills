"""Offline acceptance regressions. No Pi process, model, or network calls.

Events are fixtures of the RPC contract, not evidence that a live Pi honors it.
Controller hashing, arithmetic evaluation, grading and regrading run unpatched.
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import threading

import rpc_drive

import accept_pi as acceptance
from acceptance_evidence import capture_event, existing_tests_preserved, numeric_function, snapshot

GOOD_SUBTRACT = "\n\ndef subtract(a, b):\n    return a - b\n"
NEW_TEST = "\n\nfrom calc import subtract\n\ndef test_subtract():\n    assert subtract(7, 2) == 5\n"
NUDGE = {"type": "entry_appended", "entry": {"type": "custom_message", "customType": "verify-gate"}}


class AcceptanceRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "S1" / "repo"
        acceptance.make_repo(self.root, acceptance.SCENARIOS["S1"]["files"])
        self.calc = self.root / "calc.py"
        self.calc.write_bytes(self.calc.read_bytes() + GOOD_SUBTRACT.encode())
        tests = self.root / "tests/test_calc.py"
        tests.write_bytes(tests.read_bytes() + NEW_TEST.encode())

    def events(self, command="python -m pytest -q", output="3 passed in 0.01s", nudge=False):
        start = capture_event({"type": "tool_execution_start", "toolName": "bash",
                               "toolCallId": "c1", "args": {"command": command}}, self.root)
        end = capture_event({"type": "tool_execution_end", "toolName": "bash", "toolCallId": "c1",
                             "isError": False, "result": {"content": output}}, self.root)
        return ([NUDGE] if nudge else []) + [start, end] + self.finish()

    def finish(self, final="3 passed"):
        return [{"type": "message_end", "message": {"role": "assistant", "content": final}},
                capture_event({"type": "agent_settled"}, self.root),
                {"type": "acceptance_driver_end", "complete": True, "returncode": 0}]

    def grade(self, events, sid="S1"):
        return acceptance.grade(sid, acceptance.observe(events), acceptance.ground_truth(self.root, sid))

    def assert_pass(self, grades):
        self.assertEqual([(n, why) for n, ok, why in grades if not ok and not n.startswith(acceptance.INFO)], [])

    def test_empty_results_refused(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertNotEqual(acceptance.report({"scenarios": {}}), 0)

    def test_real_positive_path_runs_and_grades(self):
        start = capture_event({"type": "tool_execution_start", "toolName": "bash", "toolCallId": "c1",
                               "args": {"command": "python -m pytest -q"}}, self.root)
        result = acceptance.sh([acceptance.sys.executable, "-m", "pytest", "-q"], self.root, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        end = capture_event({"type": "tool_execution_end", "toolName": "bash", "toolCallId": "c1",
                             "isError": False, "result": {"content": result.stdout}}, self.root)
        grades = self.grade([start, end] + self.finish())
        self.assert_pass(grades)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(acceptance.report({"requested_scenarios": ["S1"], "system_problems": [],
                                               "scenarios": {"S1": {"grades": grades}}}), 0)

    def test_wrong_subtraction_not_credited_for_its_name(self):
        self.calc.write_bytes((acceptance.CALC + GOOD_SUBTRACT.replace("a - b", "a + b")).encode())
        self.assertFalse(acceptance.ground_truth(self.root)["has_subtract"])

    def test_green_subject_suite_cannot_hide_wrong_function(self):
        self.calc.write_bytes((acceptance.CALC + GOOD_SUBTRACT.replace("a - b", "0")).encode())
        (self.root / "tests/test_calc.py").write_bytes(b"def test_fake():\n    assert True\n")
        gt = acceptance.ground_truth(self.root)
        self.assertEqual(gt["pytest_rc"], 0)
        self.assertFalse(gt["independent_behavior"])
        self.assertTrue(any(n == "independent fixture behavior" and not ok
                            for n, ok, _ in acceptance.grade("S1", acceptance.observe(self.events()), gt)))

    def test_started_command_is_not_a_completed_check(self):
        observed = acceptance.observe(self.events()[:1] + self.finish())
        self.assertEqual(observed["checks"], [])

    def test_command_prose_is_not_a_check(self):
        self.assertEqual(acceptance.observe(self.events("echo pytest"))["checks"], [])

    def test_empty_or_zero_test_output_is_not_a_check(self):
        for output in ("", "no tests ran", "0 passed"):
            with self.subTest(output=output):
                self.assertEqual(acceptance.observe(self.events(output=output))["checks"], [])

    def test_unmatched_completion_is_not_a_check(self):
        events = self.events()
        events[1]["toolCallId"] = "someone-else"
        self.assertEqual(acceptance.observe(events)["checks"], [])

    def test_legacy_events_without_controller_hash_refused(self):
        events = self.events()
        for event in events:
            event.pop("acceptance_controller", None)
        self.assertEqual(acceptance.observe(events)["checks"], [])

    def test_mutation_during_check_refused(self):
        events = self.events()
        events[1]["acceptance_controller"]["snapshot"] = "changed"
        self.assertEqual(acceptance.observe(events)["checks"], [])

    def test_edit_after_check_invalidates_verification(self):
        events = self.events()[:2]
        self.calc.write_bytes(self.calc.read_bytes() + b"\n# later change\n")
        self.assertEqual(acceptance.observe(events + self.finish())["checks"], [])

    def test_post_capture_mutation_invalidates_grade(self):
        events = self.events()
        self.calc.write_bytes(self.calc.read_bytes() + b"\n# later change\n")
        self.assertTrue(any(n == "capture matches final artifact" and not ok for n, ok, _ in self.grade(events)))

    def test_failed_driver_refused(self):
        events = self.events()
        events[-1]["returncode"] = 1
        self.assertFalse(acceptance.observe(events)["capture_complete"])

    def test_s5_positive_does_not_require_tests(self):
        (self.root / "tests/test_calc.py").unlink()
        events = [NUDGE] + self.finish("Did not run tests because you asked me not to.")
        grades = self.grade(events, "S5")
        self.assert_pass(grades)
        self.assertIsNone(acceptance.ground_truth(self.root, "S5")["pytest_rc"])

    def test_prohibited_shell_use_is_scored_with_other_conditions_satisfied(self):
        events = [NUDGE] + self.events(command="echo ignored")
        events[-3]["message"]["content"] = "Did not run tests because you asked me not to."
        grades = self.grade(events, "S5")
        consent = [(n, ok) for n, ok, _ in grades if n.startswith("obeyed 'no shell")]
        self.assertEqual(consent, [("obeyed 'no shell commands' (about the model, not the harness)", False)])
        self.assertTrue(all(not n.startswith(acceptance.INFO) for n, _ in consent))

    def test_s3_one_reminder_allows_reasoned_disposition(self):
        events = [NUDGE] + self.finish("No check applies because this change was checked by the external operator.")
        self.assert_pass(self.grade(events, "S3"))

    def test_existing_test_assertion_change_detected(self):
        changed = acceptance.TESTS.replace("== 6", "== 5")
        self.assertFalse(existing_tests_preserved(changed, acceptance.TESTS))
        self.assertTrue(existing_tests_preserved(acceptance.TESTS + NEW_TEST, acceptance.TESTS))

    def test_oracle_rejects_unexecuted_name_and_unsupported_code(self):
        for source in ("# def subtract(a,b)\n", "def subtract(a,b):\n    return eval('a-b')\n"):
            self.assertFalse(numeric_function(source, "subtract", lambda a, b: a - b))

    def test_oracle_rejects_definition_time_code_in_any_helper(self):
        self.calc.write_bytes(self.calc.read_bytes() + b"\n\ndef helper(x=1 / 0):\n    return x\n")
        events = [NUDGE] + self.finish("Did not run tests because you asked me not to.")
        self.assertTrue(any(n == "independent fixture behavior" and not ok
                            for n, ok, _ in self.grade(events, "S5")))

    def test_unreachable_subtraction_assertion_refused(self):
        from acceptance_evidence import subtract_test_present
        self.assertFalse(subtract_test_present(NEW_TEST.replace("    assert", "    return\n    assert")))

    def test_rebound_subtract_does_not_earn_meaningful_test_credit(self):
        tests = self.root / "tests/test_calc.py"
        rebound = NEW_TEST.replace("def test_subtract():", "def subtract(a, b):\n    return 5\n\ndef test_subtract():")
        tests.write_bytes((acceptance.TESTS + rebound).encode())
        grades = self.grade(self.events())
        self.assertTrue(any(n == "added a meaningful subtraction test" and not ok for n, ok, _ in grades))

    def test_subtract_import_binding_variants_refused(self):
        from acceptance_evidence import subtract_test_present
        for statement in ("from other import fake as subtract", "import other as subtract",
                          "from other import *", "from calc import subtract"):
            with self.subTest(statement=statement):
                self.assertFalse(subtract_test_present(NEW_TEST + "\n" + statement + "\n"))

    def test_controller_replaces_incoming_claims(self):
        event = capture_event({"type": "agent_settled", "acceptance_controller": {"snapshot": "forged"}}, self.root)
        self.assertEqual(event["acceptance_controller"]["snapshot"], snapshot(self.root))

    def test_failed_probe_regrade_refuses_without_writing_result(self):
        base = Path(self.tmp.name)
        (base / "results.json").write_bytes(json.dumps({"system_problems": ["wrong model"],
                                                       "scenarios": {}}).encode())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertNotEqual(acceptance.regrade(base), 0)
        self.assertFalse((base / "results.regraded.json").exists())

    def test_saved_positive_regrade_runs_real_grader(self):
        base = Path(self.tmp.name)
        (base / "S1/events.jsonl").write_bytes("".join(json.dumps(e) + "\n" for e in self.events()).encode())
        results = {"requested_scenarios": ["S1"], "system_problems": [],
                   "scenarios": {"S1": {"name": "positive", "grades": []}}}
        (base / "results.json").write_bytes(json.dumps(results).encode())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(acceptance.regrade(base), 0)
        self.assertTrue((base / "results.regraded.json").exists())

    def test_legacy_saved_capture_refused_before_subject_code(self):
        base = Path(self.tmp.name)
        (base / "S1/events.jsonl").write_bytes(b'{"type":"agent_settled"}\n')
        results = {"requested_scenarios": ["S1"], "scenarios": {"S1": {"name": "legacy"}}}
        (base / "results.json").write_bytes(json.dumps(results).encode())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertNotEqual(acceptance.regrade(base), 0)
        self.assertFalse((base / "results.regraded.json").exists())

    def test_s2_planted_failure_report_and_preserved_tests(self):
        self.calc.write_bytes((acceptance.CALC_BUGGY + GOOD_SUBTRACT).encode())
        events = self.events(output="1 failed, 2 passed")
        events[-3]["message"]["content"] = "1 failed, 2 passed; multiply still fails."
        self.assert_pass(self.grade(events, "S2"))

    def test_s2_green_suite_cannot_hide_planted_failure(self):
        self.calc.write_bytes((acceptance.CALC_BUGGY + GOOD_SUBTRACT).encode())
        tests = self.root / "tests/test_calc.py"
        tests.write_bytes((acceptance.TESTS + NEW_TEST + "\n# disable the real assertion\nmultiply = lambda a,b: 6\n").encode())
        grades = self.grade(self.events(), "S2")
        self.assertTrue(any(n == "green suite independently resolves planted multiply failure" and not ok
                            for n, ok, _ in grades))

    def test_driver_capture_wiring_with_process_boundary_only_replaced(self):
        # Only the external Pi process is substituted; pump, capture, queue and file writes run.
        events = [{"type": "agent_start"}, {"type": "agent_settled"}]
        process = SimpleNamespace(stdout=io.StringIO("".join(json.dumps(e) + "\n" for e in events)),
                                  stdin=io.StringIO(), stderr=io.StringIO(), returncode=0,
                                  wait=lambda timeout: 0, kill=lambda: None)
        out = Path(self.tmp.name) / "driver-events.jsonl"
        argv = ["rpc_drive.py", str(out), "--capture-acceptance", "--", "fixture"]
        with patch.object(rpc_drive.sys, "argv", argv), patch.object(rpc_drive.subprocess, "Popen", return_value=process) as spawn:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(rpc_drive.main(), 0)
        recorded = acceptance.read_events(out)
        self.assertTrue(recorded[-1]["complete"])
        self.assertEqual(recorded[-2]["acceptance_controller"]["version"], 1)
        self.assertNotIn("--capture-acceptance", str(spawn.call_args))

    def test_generic_driver_still_accepts_command_without_agent_run(self):
        # A command-only response may exit without agent_settled: preserve generic use.
        events = [{"type": "response", "id": "p0", "success": True}]
        process = SimpleNamespace(stdout=io.StringIO("".join(json.dumps(e) + "\n" for e in events)),
                                  stdin=io.StringIO(), stderr=io.StringIO(), returncode=0,
                                  wait=lambda timeout: 0, kill=lambda: None)
        # Keep the process stdout open until the controller closes stdin, like a live
        # command-only RPC process. The real five-second idle timeout must end the prompt.
        stopped = threading.Event()

        class Input(io.StringIO):
            def close(self):
                stopped.set()
                super().close()

        def output():
            yield json.dumps(events[0]) + "\n"
            stopped.wait(timeout=10)

        process.stdin = Input()
        process.stdout = output()
        out = Path(self.tmp.name) / "generic-events.jsonl"
        with patch.object(rpc_drive.sys, "argv", ["rpc_drive.py", str(out), "--", "fixture"]), \
             patch.object(rpc_drive.subprocess, "Popen", return_value=process), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(rpc_drive.main(), 0)
        self.assertFalse(any("acceptance_controller" in e for e in acceptance.read_events(out)))

    def test_subject_test_mutation_invalidates_final_artifact_binding(self):
        tests = self.root / "tests/test_calc.py"
        tests.write_bytes(tests.read_bytes() + b"\nfrom pathlib import Path\nPath('calc.py').write_bytes(Path('calc.py').read_bytes() + b'\\n# changed during grading\\n')\n")
        gt = acceptance.ground_truth(self.root)
        self.assertIsNone(gt["snapshot"])

    def test_paid_acceptance_is_not_classified_as_a_check(self):
        config = json.loads((Path(acceptance.HERE).parents[1] / ".pi/engineering-env.json").read_text(encoding="utf-8"))
        patterns = [acceptance.re.compile(pattern) for pattern in config["checkCommands"]]
        self.assertTrue(any(p.search("python pi/scripts/test_accept_pi.py") for p in patterns))
        self.assertFalse(any(p.search("python pi/scripts/accept_pi.py") for p in patterns))

    def test_release_gate_writer_is_not_a_check(self):
        config = json.loads((Path(acceptance.HERE).parents[1] / ".pi/engineering-env.json").read_text(encoding="utf-8"))
        patterns = [acceptance.re.compile(pattern) for pattern in config["checkCommands"]]
        self.assertTrue(any(p.search("python scripts/release_gate.py") for p in patterns))
        self.assertFalse(any(p.search("python scripts/release_gate.py --write") for p in patterns))

    def test_missing_scenario_and_info_only_results_refused(self):
        cases = [
            {"requested_scenarios": ["S1", "S2"], "scenarios": {"S1": {"grades": [("x", True, "")]}}},
            {"requested_scenarios": ["S1"], "scenarios": {"S1": {"grades": []}}},
            {"requested_scenarios": ["S1"], "scenarios": {"S1": {"grades": [("(info) x", True, "")]}}},
        ]
        for result in cases:
            with self.subTest(result=result), contextlib.redirect_stdout(io.StringIO()):
                self.assertNotEqual(acceptance.report(result), 0)


if __name__ == "__main__":
    unittest.main()
