---
name: click-clirunner-env-none-deletes
description: |
  Click's CliRunner.invoke `env=` parameter ONLY overrides keys present
  in the dict — absent keys are not deleted from os.environ during the
  invocation. To actually delete a key for the duration of the test, pass
  `{key: None}` (Click translates None to `del os.environ[key]`). Use
  when: (1) a CLI test asserts behavior that depends on an env var being
  ABSENT and the test silently passes locally even when the real env has
  the var set, (2) testing a pre-flight check, key-resolution path, or
  any code that branches on `os.environ.get(key)`, (3) you wrote
  `clean_env = {k: v for k, v in os.environ.items() if k != "X"}` and
  passed it as `env=` — that does NOT delete X. Behaviour re-verified
  against current stable Click, 2026-08-23.
metadata:
  type: trap
version: 1.1.0
date: 2026-08-23
---

# Click CliRunner: `env=None` deletes; absence does NOT

## Problem

You wrote a CLI test where the SUT (system under test) branches on whether some env var is set. The test invokes the CLI via `CliRunner.invoke(cli, args, env=clean_env_dict)`, where `clean_env_dict` omits the env var you want absent. The test passes locally. You ship it. Later it turns out the test was never actually exercising the "var absent" branch — it was running with the var present (inherited from your shell), and your assertion happened to also pass for the "var present" code path.

In a live-API-call test, this can mean the test SILENTLY makes the network call you thought you were preventing.

## Root cause

Click's `CliRunner.invoke(env=...)` is an OVERRIDE dict, not a REPLACEMENT environment. It iterates the dict and applies each key:

- `env[key] = "value"` → sets `os.environ[key] = "value"` for the duration of the invocation, restoring afterward
- `env[key] = None` → calls `del os.environ[key]` for the duration of the invocation, restoring afterward
- key absent from `env` → `os.environ[key]` is left UNTOUCHED

Originally verified against `click/testing.py:534` on Click 8.1.x. **Re-checked 2026-08-23
against current stable**, which is the durable evidence: the published signature types the
parameter as `env: Mapping[str, str | None] | None` on both `CliRunner.invoke` and
`CliRunner.isolation`. A value type of `str | None` is the API stating that `None` is a
meaningful value rather than an omission — that is the delete. The docs describe `env` as
"overrides" and "the environment overrides as dictionary", which is the absent-keys-untouched
half. The line number is not re-pinned: Click has moved from 8.1 to 8.5 and `8.1.x` no longer
exists as a branch, so cite the signature rather than a file offset.

## Trigger conditions

You wrote one of these patterns and the test silently passed:

```python
# Pattern 1: filtered dict
clean_env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
runner.invoke(cli, args, env=clean_env)  # ANTHROPIC_API_KEY may STILL be in os.environ during invoke

# Pattern 2: empty dict
runner.invoke(cli, args, env={})  # NOTHING is deleted; nothing is overridden; identity to no env=

# Pattern 3: subset dict
runner.invoke(cli, args, env={"OTHER_VAR": "x"})  # Only OTHER_VAR is touched
```

Specific symptoms:

- Test passes when run alone but you can't reproduce the bug it was supposed to catch
- `os.environ.get("MY_VAR")` inside the SUT returns a non-empty string even though the test "set" `env` to a dict without `MY_VAR`
- A pre-flight key check passes when you expected it to fail
- A test that asserts "refuse when key absent" never actually fires its refusal path

## Fix

Pass `{key: None}` explicitly for every env var that must be absent:

```python
runner.invoke(cli, args, env={
    "ANTHROPIC_API_KEY": None,      # delete for the duration of invoke
    "OPENROUTER_API_KEY": None,     # delete for the duration of invoke
    "SOME_OVERRIDE": "value-x",     # set for the duration of invoke
})
```

For pytest-based tests, prefer `monkeypatch` over CliRunner's `env=` when you can — it has clearer semantics:

```python
def test_resolver_no_keys(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    # ... assertion
```

But when you MUST use CliRunner's `env=` (e.g., because the SUT is launched as a click command and you need it in one invocation), use the `{key: None}` form.

## Verification

After the fix, verify the test actually exercises the intended branch:

1. Temporarily insert `print(f"key={os.environ.get('MY_VAR')!r}", file=sys.stderr)` inside the SUT and re-run the test. The print should show `key=None`.
2. Run the test on a machine where the env var is genuinely set in the shell. If the fix is correct, the test should still pass / fail the same way as on a clean machine.
3. If the test asserts an exception is raised, intentionally remove the `{key: None}` and confirm the test then fails (assertion didn't fire). Then put it back.

## Notes

- This trap is particularly dangerous in tests of API-key-dependent code: the absence of `{key: None}` can let a test SILENTLY make a live network call, burning real money and producing flaky results.
- The behavior is documented in Click 8 — see [the env parameter on CliRunner.invoke](https://click.palletsprojects.com/en/stable/api/#click.testing.CliRunner.invoke) — but the docs phrase it as "added/overridden," not as "absence does nothing." Easy to miss.
- The same pattern in `subprocess.run(env=...)` works differently: there, `env=` REPLACES the entire environment. Cross-tool inconsistency is a contributor to the confusion.
- In a `monkeypatch.delenv(key, raising=False)` test, the SUT runs with the key genuinely absent from `os.environ`. This is the safer default for env-isolation tests when the code under test is not exclusively a CLI entry-point.

## Example (from skill-harness 2026-06-09)

Test that originally looked correct:

```python
# tests/ablation/test_cli_d3_fixes.py — BEFORE
clean_env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
result = runner.invoke(run_ablation, [...], env=clean_env)
assert "ANTHROPIC_API_KEY is not set" in result.output
```

On a dev machine where `OPENROUTER_API_KEY` was set (the actual project author's machine), a new model-aware resolver in the SUT rewrote the model id and proceeded to a live 12-minute Anthropic API call. The test passed because the old assertion was still in `result.output` from a DIFFERENT code path. The real branch under test was never being exercised.

Fix:

```python
# tests/ablation/test_cli_d3_fixes.py — AFTER
result = runner.invoke(run_ablation, [...], env={
    "ANTHROPIC_API_KEY": None,
    "OPENROUTER_API_KEY": None,
})
assert "ANTHROPIC_API_KEY is not set" in result.output  # now actually fires
```

## References

- Click testing module source: https://github.com/pallets/click/blob/stable/src/click/testing.py
- Click CLI testing docs: https://click.palletsprojects.com/en/stable/testing/
- pytest monkeypatch.delenv: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
