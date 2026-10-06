---
name: dead-predicate
description: "Use when a hook didn't fire, a reminder never arrived, or before claiming a rule is hook-enforced: a live router rule can match nothing (missing word, JSON escape, shadowing, stale name)."
---

# Router skill predicate gap

## Problem

A **router rule** is one entry in a prompt hook's rule file: a skill name and a list of regex
patterns. The hook (a `UserPromptSubmit` hook in Claude Code) matches each prompt against the
patterns and, on a match, injects a reminder naming the skill. A skill wired this way looks
enforced rather than remembered. It is not, when **the hook runs, exits 0, and matches
nothing**. The wiring is present, the hook is healthy, the config is valid, and nothing
distinguishes "the predicate did not match" from "no prompt needed it."

This card probes the live hook and returns, per prompt, `FIRES` or `SILENT`, plus the branch
that explains a silence. Origin, 2026-08-18: a rule called MANDATORY before any plan had no
pattern for the word "plan" (see § Example). One incident, not a measured rate.

## Use when

- A hook didn't fire, or a reminder never arrived, for a prompt that should have raised it.
- You are about to write, or repeat, the claim that a discipline is hook-enforced.
- A rule's patterns were seeded from error signatures or example phrasings and never re-read.
- The skill did fire once, and you have not checked *which* pattern matched.

## Root cause: five branches

1. **Missing word.** Patterns get seeded from high-precision triggers (error strings, slash
   commands, distinctive nouns) because the ordinary word looks too broad. The predicate
   matches specialist phrasing and misses the common request: **model-pull wearing a hook's
   clothes**.
2. **JSON escape.** In a JSON string `"\b"` is the backspace character; a regex word boundary
   is `"\\b"`. The damaged pattern still compiles and matches nothing. In the maintainer's
   research repo this happened in six sessions, S312 to S487, and one control missed it by
   scanning bytes: JSON writes the backspace as two characters, so **decode the JSON before
   scanning for `\b`**.
3. **Shadowing.** A router that stops at the first match lets an earlier rule claim every
   prompt a later rule's pattern also matches. The later rule is valid and never fires.
4. **Stale name.** The pattern matches, but the skill it names was renamed or uninstalled, so
   the reminder points at a name nothing can call. A plugin skill is named
   `<plugin>:<name>` (Claude Code plugin docs, checked 2026-10-05), so promotion into a
   plugin is a rename.
5. **Wrong claim, complete predicate.** The rule fires on every case it names, but its advice
   makes a causal claim and the case that would refute it lies outside the predicate. Every
   firing looks like confirmation. Write the counter-example and probe whether the rule
   reaches it.

## Solution

### 1. Test the negative first, against the live hook

Probe the suspect prompt **and a known-good fixture in the same run**. The known-good is a
positive control; without it the run is uninterpretable:

```sh
for p in "write me a plan for issue 18" "<a phrase you know this rule matches>"; do
  out=$(echo "{\"session_id\":\"neg-$RANDOM$RANDOM\",\"prompt\":\"$p\"}" | python <router-hook>.py)
  echo "$out" | grep -q "<skill-name>" && echo "FIRES  : $p" || echo "SILENT : $p"
done
```

Empty output on the suspect means it did not fire, **but only if the control fired**. A
crashed interpreter also prints nothing
([`vacuous-check`](https://github.com/MrBinnacle/skills/blob/main/skills/engineering/vacuous-check/SKILL.md)
→ rule 4). Make `session_id` unique per probe: these routers dedupe per session.

### 2 to 4. Scan, read, repair

Open [probes.md](probes.md) for the scripts. Step 2 decodes the rule file and reports any
pattern holding a control character. Step 3 lists every rule a prompt matches in file order,
which exposes shadowing, and checks each named skill still resolves. Step 4 adds patterns
that match the verb plus the noun, so mention stays silent and a request fires.

### 5. Probe positives, then false positives, through the step-1 loop

Every prompt a user actually types (`I need a plan`) must read `FIRES`. Then run the
false-positive set, **including words that share the stem** (`the plane landed`, `explain
the planner architecture`); every line must read `SILENT`.

## Verification

Prove the fix by a before/after pair on the *same* prompt against the *same* hook:

```
before:  "write me a plan for issue 18"  -> silent
after:   "write me a plan for issue 18"  -> fires
```

Use the user's own message from the session that exposed the gap; an invented probe can be
accused of being chosen to fire.

## Example

2026-08-18. A rule file marked `decision-rights` as router-enforced and MANDATORY before any
handoff, plan, ADR or subagent prompt, and "plan" was in no pattern. The skill had fired that
session only because `\bADR\b` matched. Three patterns were added; the user's unmatched
message then fired and five false-positive probes stayed silent.

## Notes

Open [gotchas.md](gotchas.md) when a router rule matches nothing you type, or a green per-rule suite hides a dead pattern. It records each dated case behind the five branches.

- **A passing read is not evidence.** Only piping a prompt into the live hook finds the gap.
- **Dead wiring is a neighbour.** A hook that never runs, or reads the wrong stdin shape, is a
  different diagnosis. A hook that runs and names a skill that no longer resolves is branch 4.
- **The stake is layer placement.** A router rule moves a discipline into the hook layer
  *only as far as its predicate is complete*. An incomplete one is worse than no hook: it
  retires the vigilance that would have compensated.
- **Test per pattern, not per rule.** Give every pattern a fixture only it can satisfy. A
  green per-rule suite is compatible with any number of dead patterns, because fixtures land
  on whichever pattern matches first.

Verified against a live `UserPromptSubmit` router hook, 2026-08-18. The stdin fields
`session_id` and `prompt` match the Claude Code hooks docs, checked 2026-10-05; the per-session
dedupe belongs to that hook, so re-read yours before assuming it.
