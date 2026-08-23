---
name: hidden-and-plugin-skill-reachability
description: |
  Diagnose "that skill doesn't exist" when the skill is installed and working.
  Use when: (1) the Skill tool refuses a skill name the user just typed as
  `/name`, (2) a skill named in CLAUDE.md or a docs file is absent from the
  available-skills listing, (3) `find ~/.claude/plugins -maxdepth 4 -iname
  "*skill*"` returns nothing for a plugin skill you know is installed, (4) a
  skill works for the operator but not for the agent, (5) a skill is present in
  the plugin cache and still unreachable. Three independent mechanisms make a
  present skill unreachable — `disable-model-invocation: true` frontmatter,
  plugin-cache directory depth, and project-level `skillOverrides` — and each
  produces the same symptom. Includes the verification commands for all three
  and the rule for documenting a skill list so this cannot recur.
author: Claude Code
version: 1.0.0
date: 2026-08-18
---

# Hidden and plugin skill reachability

## Problem

An agent reports a skill as missing or non-existent. The skill is installed, current,
and works when the operator types `/name`. The agent's report is wrong, and it is wrong
in a way that costs the user a working tool and costs the agent credibility.

The failure is not one bug. **Three independent mechanisms produce the identical symptom**,
and checking only the first leaves two live.

## Context / Trigger conditions

- The Skill tool returns a refusal for a name the user has just used successfully.
- A skill is named in `CLAUDE.md`, a README, or a handoff, and is absent from the
  available-skills listing the agent was given.
- A recursive search under `~/.claude/plugins` returns nothing for a plugin skill.
- The user says "it's a plugin skill" / "it's a Pocock skill" after the agent said it
  did not exist.
- A skill was reachable in one project and is not in another.

## Root causes, all three

### 1. `disable-model-invocation: true`

The skill's own frontmatter. It removes the skill from auto-discovery **and makes the
Skill tool refuse it**. Only the operator can fire it, by typing `/name`. This is the
common case: in one measured install, **20 of 35** plugin skills carried it.

```sh
grep -c 'disable-model-invocation: true' ~/.claude/skills/<name>/SKILL.md
```

`1` means operator-only. `0` means model-invocable.

### 2. Plugin skills sit seven levels deep

Plugin skills are **not** under `~/.claude/skills/`. They live at:

```
~/.claude/plugins/cache/<vendor>/<plugin>/<version>/skills/<group>/<name>/SKILL.md
```

That is depth 7 from `~/.claude/plugins`. **A `find -maxdepth 4` returns nothing, and
that is not an absence.** Multiple versions are cached side by side; only one is
installed — check which:

```sh
find ~/.claude/plugins/cache -maxdepth 6 -type d -name "<name>"
python -c "import json;d=json.load(open('$HOME/.claude/plugins/installed_plugins.json'));print({k:[i['version'] for i in v] for k,v in d['plugins'].items()})"
```

Read the **installed** version's file, not the newest cached one. They differ: skills get
added, renamed, and moved between groups across versions.

### 3. Project-level `skillOverrides`

A skill that is model-invocable upstream can be switched off per project:

```jsonc
// <project>/.claude/settings.local.json
{ "skillOverrides": { "azimuth": "off", "skill-necessity-gate": "off" } }
```

This is invisible from the skill itself. A skill whose frontmatter says nothing and whose
file is present can still be unreachable, and the reason lives in a different repository.

```sh
cat <project>/.claude/settings.local.json
```

## Solution

Before reporting a skill missing, run all three checks in order. Report the **mechanism**,
not "missing":

1. Frontmatter → operator-only. Say so and suggest the operator type `/name`.
2. Plugin cache at full depth → present, and name the version you read.
3. Project `skillOverrides` → disabled here, and name the file.

Only if all three come back empty is the skill actually absent.

## Verification

Enumerate an entire plugin's skills by reachability in one pass:

```sh
cd ~/.claude/plugins/cache/<vendor>/<plugin>/<version>/skills
for f in */*/SKILL.md; do
  n=$(basename $(dirname "$f")); g=$(dirname $(dirname "$f"))
  if grep -q 'disable-model-invocation: true' "$f"; then echo "HIDDEN  $g/$n"; else echo "VISIBLE $g/$n"; fi
done | sort
```

The count should match: `VISIBLE` entries appear in the agent's available-skills listing,
`HIDDEN` ones do not. If a `VISIBLE` skill is still absent from the listing, cause 3 is live.

## Example

2026-08-18. A user typed `/ask-matt`. The agent searched
`find ~/.claude/plugins -maxdepth 4 -iname "*ask-matt*"`, got nothing, checked
`~/.claude/skills/`, `~/.claude/commands/`, and the project's `.claude/commands/`, and
reported: *"`/ask-matt` does not exist on this machine."*

The user replied: *"It's a Pocock skill."*

It was at
`~/.claude/plugins/cache/mattpocock/mattpocock-skills/1.2.3/skills/engineering/ask-matt/SKILL.md`
— **depth 7**, with `disable-model-invocation: true`. Both causes 1 and 2 at once. The
`-maxdepth 4` produced the empty result; the frontmatter is why it was absent from the
listing in the first place.

The same audit found the machine's `CLAUDE.md` naming `mattpocock-skills:handoff` and
`grill-me` — both hidden — beside `prototype`, which is visible, with nothing
distinguishing them. Any agent following that list would call `Skill(handoff)`, be
refused, and report a working skill as missing.

## The documentation rule this implies

**Naming a skill without stating its access is how a present skill gets reported missing.**
Any curated skill list an agent reads should mark each entry:

- `[✓]` agent-reachable — the Skill tool can call it.
- `[/]` operator-only — `disable-model-invocation: true`; suggest it, never call it.
- `[off]` disabled by this project's `skillOverrides`.

This is the same defect class as naming a documentation directory without saying whether
it is authoritative: the reader cannot act on the name alone.

## Notes

- **An empty search result is not evidence of absence** unless the search could have found
  the thing. Depth-limited `find` is the specific trap here.
- The operator can always fire an operator-only skill. "Missing" and "not mine to call"
  are different reports and only one of them is true.
- Frontmatter hiding is a property of the skill; `skillOverrides` is a property of the
  project. A skill can be reachable in one repo and not the next with no change to either
  the skill or the agent.
- See also: `claude-code-stop-hook-envelope` for the adjacent case of wiring that is present
  and silently ineffective, and `router-skill-predicate-gap` for a skill that is reachable
  and still does not fire.

## References

Verified by direct filesystem observation on one machine (Windows, Claude Code, 2026-08-18);
no external documentation was consulted, and the directory layout above should be
re-verified rather than assumed on a major version change.
