# Claude Code integration

Read this file only when the user asks for repository-wide enforcement or installation.

## Install the skill

Use one scope:

```bash
# Project scope
mkdir -p .claude/skills
cp -R self-documenting-code .claude/skills/self-documenting-code

# Personal scope
mkdir -p ~/.claude/skills
cp -R self-documenting-code ~/.claude/skills/self-documenting-code
```

The directory name and the frontmatter `name` must remain `self-documenting-code`.

## Keep permanent rules small

Copy only the needed lines from `assets/claude-rules-template.md` into `CLAUDE.md` or a path-specific `.claude/rules/` file.

Keep the procedure in this skill. Permanent rules should contain only constraints that apply to every relevant task.

## Add code intelligence

Install the Claude Code language-server plugin for the repository language.

For Python, install the `pyright-lsp` plugin through `/plugin` and make `pyright-langserver` available on `PATH`.

Use language-server references for repository-wide renames. Text search alone can miss re-exports, generated bindings, and language-aware references.

## Add deterministic hooks

Use hooks only for checks that must run every time.

Good hook candidates include:

- Formatting checks.
- Fast lint checks.
- Type checks for touched packages.
- Generated-file drift checks.

Do not put subjective readability judgment in a hook. A hook needs a deterministic pass or fail result.

Do not run a costly full test suite after every edit. Use focused checks after edits and a broader gate before completion.

## Use a fresh reviewer

Use a subagent for the final cold-reader review. Give it the prompt in `references/review-protocol.md`.

Keep the reviewer read-only when possible. The implementation agent should adjudicate findings and make accepted corrections.

## Continuous repository pattern

Use this division of responsibility:

- `CLAUDE.md`: Stable repository constraints.
- This skill: The reasoning and refactor workflow.
- LSP plugin: Symbol references and immediate diagnostics.
- Hooks: Deterministic checks.
- Tests: Behavior evidence.
- Fresh subagent: Independent comprehension review.
- ADRs or issues: Rationale and migration facts that code cannot express.

A plugin can package these components later. Do not create a plugin until a second repository needs the same hooks and reviewer configuration.
