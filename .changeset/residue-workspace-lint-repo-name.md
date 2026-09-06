---
"mrbinnacle-skills": patch
---

A private repository's name leaked into five public Markdown files, two of them published skill cards, and the de-personalization gate had no term to catch it.

**What was wrong.** The name of the maintainer's private linter repository appeared by name in `CHANGELOG.md`, `_quarantine/structure-at-the-write-site/SKILL.md`, `_quarantine/subagent-research-reliability/PROVENANCE.md`, `skills/engineering/pretooluse-bash-guard-prose-false-positive/gotchas.md`, and `skills/engineering/success-test-accepts-any-output/SKILL.md`. The `.pre-commit-config.yaml` residue hooks list several private identifiers by name, but this one was not among them, so the gate never caught it.

**What changed.** All five occurrences are replaced with the generic descriptor "a private linter project," used identically everywhere so the passages that count it as a distinct evidence occurrence (separate from "a different repository" and "a third project" elsewhere in the same files) stay distinguishable. No date, count, or other technical detail changed. A new residue hook now bans the private repository's name in `.md` files, matching the shape of the existing residue hooks, so this cannot recur silently.
