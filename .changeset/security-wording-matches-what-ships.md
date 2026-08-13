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

A new commitment 3 states that any code a skill ships is readable source invoked only by that
skill's own written instructions, names the four permitted formats, and carries the check a reader
runs against their own installed copy. The published command is the one
`scripts/validate_skill_formats.py` generates from the suffix tuple it enforces, so the page and
the predicate cannot disagree.

⚠ The commitment says CI **detects** violations, not that it prevents them. `main` has no required
status checks, so a nonzero exit is a signal rather than a gate. Publishing the stronger verb
against the weaker mechanism would have reintroduced this effort's own defect inside the sentence
written to remove it.
