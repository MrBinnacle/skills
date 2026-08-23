# Gotchas — mock-masked-stub-trap

Append-only. Seeded with `[ANTICIPATED]`; replace/supplement with `[OBSERVED]` as they occur.

- `[OBSERVED 2026-06-06]` Two consecutive tracks (D.2, D.3 of Skill Harness) each returned
  all-green with a load-bearing branch stubbed and only "tested" via a patch of the stub.
  D.3's `_find_incomplete_run` was literally `return None`; its A52 double-spend-guard test
  patched it to a fake run_id. Independent re-review (read the test for `patch(` + read the
  production body) caught it; the gate did not.

- `[OBSERVED 2026-06-06]` Scope-of-gate mismatch hides lint: implementer ran `ruff check src/`
  and reported clean; the project gate is `src/ tests/`, which had E501 + unused-import in the
  new test file. Always re-run the **project's** gate scope, not the agent's reported command.

- `[ANTICIPATED]` Over-correction: forbidding ALL patching. Patching the true boundary
  (network SDK client, clock, RNG, subprocess) is correct and necessary — the rule is "don't
  patch the unit/helper whose correctness is the claim," not "don't patch anything."

- `[ANTICIPATED]` A helper that returns a hardcoded constant can pass a weak assertion
  (`assert result is not None`) even unpatched. Require the test to assert the *specific*
  value derived from seeded real state, not mere truthiness.

- `[ANTICIPATED]` Coverage tools report the stub line as "covered" because the patched test
  still imports/touches it. Line coverage ≠ behavior coverage; this trap survives a coverage gate.
