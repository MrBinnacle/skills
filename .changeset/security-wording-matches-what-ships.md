---
"mrbinnacle-skills": patch
---

`SECURITY.md` and `README.md` stop claiming that a skill is a plain-text markdown file, and say
what this repository actually ships.

The claim was false as published. `SECURITY.md` opened with *"A skill is a plain-text markdown
file. Installing one: executes **nothing** on your machine"* while five tracked `.py` files sit
inside `skills/engineering/im-{down,up}/`, and both cards' `SKILL.md` instruct the agent to run
them. The README repeated it.

The replacement separates installation from execution, which is the distinction the old sentence
collapsed: nothing runs at install time, and a script runs when the skill runs, subject to the
host's permissions. It also restores the audit instruction. That last part is the actual repair —
the old sentence was worse than inaccurate because it told a reader there was nothing to audit,
so it cost them the review the platform's own guidance asks for.

A new commitment 3 states that any code a skill ships is readable source, names the four permitted
formats plus the conditional bytecode rule, and carries the check a reader runs against their own
installed copy.

Two claims elsewhere in the same files were contradicted by admitting scripts and are corrected
here rather than left standing: commitment 1's *few minutes end to end* bar, which `im-down`'s 627
lines of Python fail, and the README's definitional *a skill is a small markdown file*. Commitment
3 also no longer says a shipped script is invoked only by the skill's own instructions — the two
test suites are run by CI and no skill invokes them, and a reader auditing the folder will find
them.

The reader-side command was found to be strictly weaker than the gate it reproduces: a bare
`-path '*/__pycache__/*.pyc'` matches at any depth, so a payload nested one level inside
`__pycache__` was skipped by step 1 and waved through by step 2, on a tree CI rejects. Both steps
in `scripts/validate_skill_formats.py` and `scripts/check-installed-skills.sh` are now anchored to
one level, with a regression case running both instruments over that tree and requiring the same
verdict. The command's target is no longer a hardcoded `~/.claude/skills/<name>`, because
`npx skills add` installs project-locally unless `--global` is passed.

⚠ The commitment says CI **detects** violations, not that it prevents them. `main` has no required
status checks, so a nonzero exit is a signal rather than a gate. Publishing the stronger verb
against the weaker mechanism would have reintroduced this effort's own defect inside the sentence
written to remove it.
