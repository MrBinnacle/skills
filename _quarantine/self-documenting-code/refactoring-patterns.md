# Refactoring patterns

Use the smallest established refactoring that answers the reader question. Preserve behavior before and after each step.

The primary prior art is Martin Fowler's refactoring catalog. This guide selects patterns that improve code comprehension without treating style as correctness.

## Pattern map

| Observed problem | Preferred refactoring | Verification guardrail |
|---|---|---|
| Vague or conflicting identifier | Rename Variable, Rename Function, or Rename Field | Search all references and preserve public aliases when required |
| A block has a distinct purpose | Extract Function | Test the caller before and after extraction |
| A function mixes responsibilities | Extract Function or Extract Class | Keep orchestration visible and preserve operation order |
| Nested conditions hide the main path | Replace Nested Conditional with Guard Clauses | Test each branch and failure path |
| A complex condition has no domain name | Decompose Conditional | Test truth-table cases |
| A Boolean argument changes behavior | Replace Parameter with Explicit Methods or Introduce Parameter Object | Verify every call-site mode |
| Primitive values hide units or valid states | Replace Primitive with Object or Introduce Assertion | Verify serialization and boundary conversion |
| A read-like function changes state | Separate Query from Modifier and Rename Function | Verify side effects and transaction boundaries |
| Several parameters travel together | Introduce Parameter Object | Preserve public signature through an adapter if needed |
| One variable serves several meanings | Split Variable | Verify every assignment and use |
| A comment translates a block | Extract Function with an intention-revealing name | Preserve any rationale outside the translated mechanics |
| Failure behavior is implicit | Introduce explicit result or exception boundary | Test each failure mode and caller response |
| Operation order is hidden | Extract orchestration function or introduce lifecycle state | Verify sequence-sensitive behavior |

## Naming rule

A name should identify the domain meaning at its scope.

Prefer:

```python
eligible_claims = claims.filter(is_filing_ready)
```

Avoid:

```python
items2 = process(items1)
```

Do not encode the implementation when the caller needs the outcome.

Prefer `calculate_net_cost` over `loop_over_rows`.

## Side-effect rule

A function name must not promise a query when the function performs a command.

Before:

```python
def account(user_id):
    data = client.get(user_id)
    cache.write(user_id, data)
    return data
```

After:

```python
def fetch_and_cache_account(user_id):
    account = client.get(user_id)
    cache.write(user_id, account)
    return account
```

A stronger split can separate `fetch_account` from `cache_account` when callers need independent control.

## Comment rule

Classify the comment before any edit.

- **Translation:** Restates the next lines. Improve code, then remove it.
- **Rationale:** Explains why this design exists. Keep it or move it to an ADR.
- **Authority:** Cites a specification, law, protocol, or business rule. Keep it.
- **Hazard:** Warns about a non-obvious failure or dependency. Keep it near the boundary.
- **Contract:** States an invariant that the type system cannot express. Keep it and test it.
- **History:** Explains a compatibility obligation. Keep it until the obligation ends.

## Abstraction gate

Create an abstraction only when at least one condition holds:

1. It gives a stable domain concept a direct name.
2. It prevents an invalid state.
3. It exposes a hidden side effect or lifecycle transition.
4. It removes repeated policy that must change as one unit.
5. It creates a testable boundary around volatile infrastructure.

Do not abstract only to reduce line count.

## Compatibility gate

Before a rename, search for:

- Imports and re-exports.
- Serialization keys and schemas.
- CLI commands and flags.
- Environment variables.
- Database columns and migrations.
- Reflection, dependency injection, and plugin registration.
- Documentation examples and external consumers.

For a public name, prefer an adapter, alias, deprecation notice, and removal condition.

## When not to refactor

Do not refactor generated code, vendored code, or active migrations without explicit scope.

Do not simplify an algorithm when performance or numerical behavior lacks a stable test.

Do not replace a repository idiom with a personal preference.

Do not combine a clarity change with feature work unless the behavior change requires the refactor.
