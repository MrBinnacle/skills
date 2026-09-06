---
name: click-clirunner-env-none-deletes
description: "Click's CliRunner.invoke `env=` only overrides keys the dict names; an absent key is not deleted. Pass `{key: None}` to delete one. Use when a CLI test asserts on an env var being absent."
---

# Click CliRunner: `env=None` deletes; absence does NOT

Evidence and failure modes: [EVIDENCE.md](EVIDENCE.md), [gotchas.md](gotchas.md).

## Problem

You wrote a CLI test where the SUT (system under test) branches on whether an env var is set. The test invokes the CLI via `CliRunner.invoke(cli, args, env=clean_env_dict)`, where `clean_env_dict` omits the env var you want absent. The test passes locally. You ship it. Later it turns out the test was never exercising the "var absent" branch — it was running with the var present (inherited from your shell), and your assertion happened to also pass for the "var present" code path. In a live-API-call test, this can mean the test SILENTLY makes the network call you thought you were preventing.

## Root cause

Click's `CliRunner.invoke(env=...)` is an OVERRIDE dict, not a REPLACEMENT environment. It iterates the dict and applies each key:

- `env[key] = "value"` → sets `os.environ[key] = "value"` for the duration of the invocation, restoring afterward
- `env[key] = None` → calls `del os.environ[key]` for the duration of the invocation, restoring afterward
- key absent from `env` → `os.environ[key]` is left UNTOUCHED

Originally verified against `click/testing.py:534` on Click 8.1.x; re-checked 2026-08-23 and 2026-08-24 against the current published [testing module source](https://github.com/pallets/click/blob/stable/src/click/testing.py). The durable evidence is the signature: `env: Mapping[str, str | None] | None` on `CliRunner`, `CliRunner.invoke` and `CliRunner.isolation`. A value type of `str | None` is the API stating that `None` is a meaningful value rather than an omission — that is the delete. The docs describe `env` as "overrides", which is the absent-keys-untouched half. Cite the signature, not a file offset or a version pin — the `8.1.x` branch no longer exists, and the signature has survived every check so far.

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

For pytest-based tests, prefer [`monkeypatch.delenv`](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) when the code under test is not exclusively a CLI entry-point — the SUT then runs with the key genuinely absent from `os.environ`, which is the clearer semantics:

```python
def test_resolver_no_keys(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    # ... assertion
```

When you MUST use CliRunner's `env=` (the SUT is launched as a click command and you need one invocation), use the `{key: None}` form.

## Verification

After the fix, verify the test actually exercises the intended branch:

1. Temporarily insert `print(f"key={os.environ.get('MY_VAR')!r}", file=sys.stderr)` inside the SUT and re-run. The print should show `key=None`.
2. Run the test on a machine where the env var IS set in the shell. A correct fix passes/fails the same way as on a clean machine.
3. If the test asserts an exception, intentionally remove the `{key: None}` and confirm the test then fails. Put it back.

## Notes

- Most dangerous in tests of API-key-dependent code: the missing `{key: None}` can let a test silently make a live network call, burning real money and producing flaky results.
- The behavior is documented — [the env parameter on CliRunner.invoke](https://click.palletsprojects.com/en/stable/api/#click.testing.CliRunner.invoke) — but phrased as "added/overridden," not as "absence does nothing." Easy to miss.
- `subprocess.run(env=...)` works differently: there, `env=` REPLACES the entire environment. The cross-tool inconsistency is a contributor to the confusion.

## Example (from skill-harness 2026-06-09)

```python
# tests/ablation/test_cli_d3_fixes.py — BEFORE, looked correct
clean_env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
result = runner.invoke(run_ablation, [...], env=clean_env)
assert "ANTHROPIC_API_KEY is not set" in result.output
```

On a machine where `OPENROUTER_API_KEY` was set, a model-aware resolver in the SUT rewrote the model id and proceeded to a live 12-minute Anthropic API call. The test passed because the old assertion string was still in `result.output` from a DIFFERENT code path — the branch under test was never exercised.

```python
# AFTER
result = runner.invoke(run_ablation, [...], env={
    "ANTHROPIC_API_KEY": None,
    "OPENROUTER_API_KEY": None,
})
assert "ANTHROPIC_API_KEY is not set" in result.output  # now actually fires
```
