---
name: mock-masked-stub-trap
description: Use when reviewing a just-returned implementation that reports all-green tests, especially for a load-bearing or safety-critical branch (budget/spend guards, idempotency, auth, refusal paths). Catches the dominant false-pass where a test patches the very helper that is a production stub.
---

# Mock-Masked Stub Trap

## The trap

An implementer returns a track/PR with **all gates green** (pytest passing, mypy/lint
clean) — and a load-bearing branch is **stubbed in production** but appears tested because
the test **patches the very function that is the stub**. The green is hollow: the production
code path it claims to cover never runs in any test.

Canonical shape:

```python
# production
def _find_incomplete_run(skill_id):
    return None            # <-- stub; docstring may even admit it

# test (passes, proves nothing about production)
with patch("mod._find_incomplete_run", return_value="run-123"):
    ...  # exercises only the render-given-a-truthy-value path
```

The safety guard built on `_find_incomplete_run` is dead code in production; the test
patches the stub to a fake truthy value and validates only the downstream branch. A real
run silently skips the guard. This is **not** a rare slip — it is the *default* failure mode
of TDD-after-the-fact when the helper is hard to drive, and it recurs run-over-run (observed
in two consecutive tracks in one session).

## When to fire

- Reviewing a returned implementation that self-reports green, **before** trusting it to land.
- Especially when the change includes a **safety/spend/refusal/idempotency** invariant
  ("must warn", "must refuse", "must not double-spend", "exits N"), or a branch that is
  awkward to exercise without real I/O (DB, network, filesystem, subprocess).
- Any time the prior round of work on this surface shipped green-but-broken.

## The check (do these, do not skip to the gate result)

1. **Grep the test file for `patch(`/`patch.object` and list every patched symbol.** For each,
   ask: *is this symbol the production function the test claims to validate?* If yes → that
   behavior is unverified. A test may patch the **boundary** (network client, clock, RNG) —
   that is fine. It must **not** patch the **unit under test** or the helper whose correctness
   is the claim.
2. **Read the production body of every patched helper.** If it is `return None` / `pass` /
   `raise NotImplementedError` / a hardcoded constant / `[placeholder]`, the green is hollow.
3. **Confirm at least one test drives the real function unpatched** — seeds real state
   (DB row, file, env) and calls the production function directly, asserting the real output.
4. **For integration paths, confirm only the true boundary is patched** (e.g. the SDK/network
   client) and the wiring (config load, dispatch, arg-passing) runs for real.
5. **Independently re-run the gates yourself** — and at the **project's** scope, not the
   implementer's. (Observed: an agent ran `ruff check src/` and reported clean; the repo gate
   is `src/ tests/`, which had failures.)

## What good looks like

The falsifying test seeds real state and calls the production function with **no patch on it**:

```python
_seed_run_progress(rt, "run-001", state="running")      # real DB row
assert _find_incomplete_run(skill_id, runtime_conn=rt) == "run-001"   # unpatched
```

If you cannot write such a test without patching the unit, that is the signal the production
code is a stub — not a reason to patch.

## Why it matters

Green is evidence the *test passed*, never evidence the *production path ran*. The mock that
makes the test convenient is the same mock that hides the missing implementation. A
fresh-context re-review that reads the BLOCKER tests for unpatched-ness — rather than trusting
the suite — is what catches it. (Verification beats self-reporting: the model saying "633
passed" is not evidence the guard works.)

## See also

- `ai-slop-sentinel`, `code-review-sentinel` — broader fresh-context review; this is the
  specific test-vacuity lens to add when a safety branch reports green.
- `parallel-review-disposition-schema` / `cross-talk-council-dispatch` — fan out N isolated
  reviewers on return; assign one the explicit "are the tests unpatched?" lens.
- `sqlite-tie-break-red-test-trap` — sibling RED-test trap.
