---
"mrbinnacle-skills": patch
---

Add the skill-folder format gate, plus the command a reader runs on their own copy.

`SECURITY.md` is about to commit to a closed vocabulary: every file inside a skill folder is `.md`, `.txt`, `.py` or `.json`. `scripts/validate_skill_formats.py` is the check behind that sentence. It walks and evaluates a predicate per file, with no per-file allowlist anywhere in it, so a new violating file turns the run red with nobody remembering to update a list. It discovers skill folders by the presence of `SKILL.md` — the marker the installer keys on — rather than by the literal path `skills/**`, which brings the fixture trees under `scripts/fixtures/` inside the guarded set by construction. All violations are listed, not just the first. The walk follows symlinks, because installs are symlinked and a walk that does not follow them skips the files it exists to guard.

Compiled Python is admitted only when the source it derives from sits beside it: `__pycache__/mod.*.pyc` passes if and only if `mod.py` is in the parent directory. A skill that ships a script leaves bytecode behind the first time it runs, and blanket-skipping `__pycache__` would answer that while carving out a directory the check never opens. A payload at `__pycache__/evil.pyc` has no `evil.py`, so it fails.

A co-located gate makes the claim maintainable, not verifiable — one commit can add a violating file and widen the vocabulary in the same diff, and green CI is invisible to a reader anyway. So it ships paired with `scripts/check-installed-skills.sh`, the same check aimed at an installed copy. The two `find` commands in it are generated from the same suffix tuple the walker enforces and are asserted identical by the suite, so the published text cannot drift from the predicate.

`scripts/test_validate_skill_formats.py` builds every rejection case as a real tree and runs the real entrypoint: a planted `.sh`, bytecode with no source, an extensionless file, a violating file in a `SKILL.md` folder outside `skills/`, and a root with no skill folders at all. Two of those also run as visible poison-control steps in the `validator` job.

**This detects violations. It does not prevent them.** `main` has no branch protection and no required checks, so a nonzero exit here is a signal, not a gate.
