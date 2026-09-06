# Self-documenting code rules

Use only the rules that apply to this repository.

- Use one domain term for one concept.
- Name commands after their side effects and queries after their returned value.
- Put units and lifecycle state in types or names when confusion can cause defects.
- Preserve public names unless the task includes a migration plan.
- Use comments for rationale, authority, hazards, and compatibility facts.
- Do not use comments to translate code that a small refactor can clarify.
- Keep behavior changes separate from clarity refactors.
- Run focused tests and configured static checks before completion.
- Report existing failures separately from failures introduced by the change.
