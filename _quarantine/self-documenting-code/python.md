# Python notes

Read this file only for Python code.

## Contracts

- Add type annotations to public functions and unclear internal boundaries.
- Use `Protocol` for behavior contracts when inheritance is not required.
- Use `dataclass`, `NamedTuple`, or a validated model for values that travel together.
- Use `Enum` or `Literal` when a Boolean or string has a closed set of states.
- Preserve runtime compatibility when annotations affect imports or evaluation.

## Naming

- Use nouns for values and types.
- Use verbs for commands.
- Use question-like predicates such as `is_ready`, `has_evidence`, or `can_retry`.
- Include units where the type does not provide them, such as `timeout_seconds`.
- Avoid `data`, `info`, `item`, `obj`, `tmp`, and `result` when a domain name exists.
- Permit short conventional names in small mathematical or comprehension scopes.

## Side effects

Names such as `get`, `find`, `read`, and `calculate` should not hide writes or network mutations.

Separate pure calculation from I/O when the split exposes behavior or enables a direct test.

Do not split a cohesive operation only to satisfy a purity preference.

## Exceptions

- Catch the narrowest useful exception.
- Preserve the original cause with `raise ... from ...` when translation adds context.
- Do not return `None` for both "not found" and "failed" unless the contract states that meaning.
- Put retry policy at an infrastructure boundary. Do not hide retries inside a value calculation.

## Comments and docstrings

- Public docstrings should state contract facts that the signature cannot carry.
- Do not repeat parameter names and types that annotations already show.
- Keep examples when they clarify units, state transitions, or failure behavior.
- Preserve comments that explain an external rule, numerical method, compatibility constraint, or measured optimization.

## Verification

Use repository commands first. Common commands include:

```bash
ruff format --check .
ruff check .
pyright
pytest -q path/to/relevant_tests.py
```

Do not install a tool only for this skill unless the user requests repository setup.

For renames, use language-server references when available. Confirm dynamic imports, string-based registration, fixtures, and serialized names through search and tests.
