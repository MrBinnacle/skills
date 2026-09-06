# self-documenting-code

A Claude Code skill for evidence-backed reviews and behavior-preserving clarity refactors.

## Install

Copy this directory to one location:

```bash
# Project
.claude/skills/self-documenting-code/

# Personal
~/.claude/skills/self-documenting-code/
```

Invoke it directly with `/self-documenting-code`, or let Claude load it when the request matches its description.

## Package structure

- `SKILL.md` contains the core workflow and resource routing.
- `references/` contains conditional expert guidance.
- `assets/` contains optional templates.
- `scripts/` contains deterministic evidence and package checks.
- `evals/` contains functional and trigger test cases.

## Validate

```bash
python scripts/validate_package.py .
python -m py_compile scripts/*.py
```

Behavior remains unmeasured until the functional and trigger evals run in clean Claude Code sessions.
