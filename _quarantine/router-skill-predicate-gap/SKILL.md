---
name: router-skill-predicate-gap
description: |
  Find and close the gap where a router rule is live, healthy, and still
  matches nothing users type. Two causes, and the second is invisible: the
  pattern list omits the ordinary word for the thing, or a pattern is INERT
  because a JSON string escape was written where a regex escape was meant
  ("\b" in JSON is a backspace character; a word boundary needs "\\b"). Use
  when: (1) a rule says a skill must fire before some class of work and you
  cannot recall it firing, (2) a router rule exists in skill-rules.json and
  the discipline still depends on the model remembering it, (3) you are about
  to claim a discipline is "hook-enforced" rather than model-pull, (4) a
  router self-test is green and you have not checked WHICH pattern each
  fixture matched, (5) you are auditing whether a documented enforcement
  layer actually enforces. Includes the test-the-negative-first procedure
  with a positive control, a control-character check that re.compile cannot
  perform, a false-positive probe set, and why per-rule fixture coverage
  certifies dead patterns.
author: Claude Code
version: 1.1.0
date: 2026-08-23
---

# Router skill predicate gap

## Problem

A skill is documented as MANDATORY. It is wired into a `UserPromptSubmit` router hook, so
the rule looks enforced rather than remembered. It is not. **The hook runs, exits 0, and
matches nothing**, because its regex list omits the word users most often type for the
thing it guards.

This fails silently in the most misleading way available: the wiring is present, the hook
is healthy, the config is valid, and a reader auditing `settings.json` sees enforcement.
Nothing distinguishes "the predicate did not match" from "no prompt needed it."

## Context / Trigger conditions

- A rule file says a skill is MANDATORY before some class of work, and you cannot recall
  the reminder actually arriving.
- You are about to write, or repeat, the claim that a discipline is hook-enforced.
- A router rule's `patterns` list was seeded from error signatures or from a few example
  phrasings, and has not been re-read since.
- The skill did fire once, and you have not checked *which* pattern matched.
- An audit asks whether the enforcement layer enforces.

## Root cause

Router patterns are usually seeded from the highest-precision, lowest-false-positive
triggers — error strings, slash commands, distinctive nouns. That seeding is correct and it
systematically **omits the ordinary word for the artifact**, because the ordinary word looks
too broad to add safely.

The result is a predicate that matches specialist phrasing and misses the common request.
The rule then fires when the user happens to use jargon and stays silent when they do not —
which is model-pull wearing a hook's clothes.

## Solution

### 1. Test the negative first, against the live hook

**Do this before editing anything.** A test that only demonstrates the fixed state proves
nothing about the gap.

Probe the suspect prompt **and a known-good fixture in the same run**. The known-good is a
positive control, and without it the run is uninterpretable:

```sh
cd ~/.claude/hooks
for p in "write me a plan for issue 18" "<a phrase you know this rule matches>"; do
  out=$(echo "{\"session_id\":\"neg-$RANDOM$RANDOM\",\"prompt\":\"$p\"}" | python skill-router.py)
  echo "$out" | grep -q "<skill-name>" && echo "FIRES  : $p" || echo "SILENT : $p"
done
```

Empty output on the suspect prompt means it did not fire — **but only if the control fired.**
Empty output is also what a crashed interpreter prints. If the control is silent, the harness
is broken, not the predicate. The general rule and its worked case live in
`success-test-accepts-any-output` → rule 4; a negative finding needs a positive control for
the same reason a positive one needs a shape assertion.

Note the `session_id` must be unique per probe — these routers dedupe per session, so reusing
one makes a firing rule look silent.

### 1b. Assert that no pattern holds a control character

A JSON string escape is not a regex escape. Inside a JSON rule file, `"\b"` is the **backspace
character**; a regex word boundary must be written `"\\b"`. The damaged pattern is still a
valid regex, so `re.compile()` accepts it, and it matches nothing forever. Grep the compiled
patterns rather than reading them:

```sh
python -c "
import json
CTRL={'\x08':r'\b','\x0c':r'\f','\x0b':r'\v','\x07':r'\a'}
for i,r in enumerate(json.load(open('skill-rules.json'))['rules']):
    for j,p in enumerate(r.get('patterns',[])):
        for ch,esc in CTRL.items():
            if ch in p: print('rule[%d] pattern[%d] holds literal %r, meant %s' % (i,j,ch,esc))
"
```

### 2. Read the actual patterns

```sh
python -c "
import json;d=json.load(open('skill-rules.json'))
for r in d['rules']:
    if r['skill']=='<skill-name>': print(json.dumps(r['patterns'],indent=1))
"
```

Compare against how the artifact is actually requested, not how it is named in the rule
file.

### 3. Add patterns that target authoring, not mention

Match the *verb plus the noun*, so conversation about the thing stays silent while a request
to produce one fires:

```json
"\\b(writ(e|ing)|draft(ing)?|creat(e|ing)|produc(e|ing)|author(ing)?|updat(e|ing)|need|want|give me)\\b.{0,30}\\bplans?\\b",
"\\b(implementation|execution|migration|rollout|remediation|tooling|project|build)\\s+plans?\\b",
"\\bplans?\\b.{0,20}\\bfor\\b.{0,25}(#\\d+|issue|ticket)"
```

Validate the JSON before trusting the file:

```sh
python -c "import json;json.load(open('skill-rules.json'));print('JSON valid')"
```

### 4. Probe positives and negatives

```sh
for p in "write me a plan for issue 18" "draft an implementation plan" "I need a plan"; do
  out=$(echo "{\"session_id\":\"t-$RANDOM$RANDOM\",\"prompt\":\"$p\"}" | python skill-router.py)
  echo "$out" | grep -q "<skill-name>" && echo "FIRES  : $p" || echo "SILENT : $p"
done
```

Then the false-positive set. **Include words that share the stem** — this is what `\b`
boundaries are for and the only way to know they hold:

```sh
for p in "run the tests" "the plane landed" "explain the planner architecture"; do ... done
```

## Verification

The finding is proven when you can show the before/after pair on the *same* prompt string
against the *same* hook:

```
before:  "write me a plan for issue 18"  -> silent
after:   "write me a plan for issue 18"  -> fires
```

Best case, use the user's own message from the session that exposed the gap. A probe you
invented can be accused of being chosen to fire; their real prompt cannot.

## Example

2026-08-18. A machine-level rule file marked `downstream-instruction-framing` as
*router-enforced, MANDATORY before ANY handoff / plan / ADR / subagent-prompt*. Its patterns
were `hand.?off`, `\bADR\b`, `subagent.{0,12}(prompt|brief|dispatch)`,
`dispatch.{0,15}(sub)?agent`, `scheduled?.{0,10}(agent|brief)`, `/schedule\b`, `/loop\b`,
`execution plan`.

**The bare word "plan" was not among them.** The skill had fired earlier in that session
only because the work also involved an ADR — `\bADR\b` matched, and the correct behaviour
was pure coincidence relative to the rule's stated purpose.

Tested negative first: `"write me a plan for issue 18"` → silent. Three patterns added.
After: fires, and so does `"And triage/skill tooling plan"`, the user's actual message from
that session, which had produced no reminder at the time. Five false-positive probes stayed
silent, including `plane` and `planner`.

## Notes

- **A passing read is not evidence.** The gap was invisible to anyone reading the rule file,
  `settings.json`, or the skill. Only piping a prompt into the hook found it.
- **This is not dead wiring.** The hook was healthy and correct. Do not diagnose it as a
  broken hook — see `claude-code-stop-hook-envelope` for that distinct case, where the hook
  itself never fires or reads the wrong stdin shape.
- **The layer-placement rule is what is at stake.** A discipline that must fire cannot live
  in the skill layer, because skill retrieval is model-pull. A router rule moves it to the
  hook layer *only to the extent its predicate is complete.* An incomplete predicate leaves
  the discipline in the skill layer while the documentation claims otherwise, which is worse
  than no hook: it retires the vigilance that would have compensated.
- **A router rule deserves a test suite — and a per-rule test suite is not enough.** In the
  install where this was found, 3 of 9 hooks had tests and the router was not one of them. A
  test suite is what catches a predicate gap; a reading is not. **But 2026-08-23 refuted the
  sufficient half of that claim**: a second rule on the same install had a suite that *refused
  to accept any rule carrying no asserting fixture*, and it still certified a rule whose
  broadest pattern was inert, because its coverage check was per-rule. All the fixtures landed
  on the narrower patterns. Measured that day: 33 of 72 patterns were reachable by no fixture
  at all. **Count coverage per pattern, not per rule, and give every deliberately-broad
  pattern a fixture only it can satisfy** — otherwise the broad pattern is not falsifiable.
  See `gotchas.md`.
- The dedupe-per-session behaviour is a real trap when probing. Vary `session_id` every time.

## References

Verified against a live `skill-router.py` UserPromptSubmit hook on one machine, 2026-08-18.
The stdin envelope shape (`session_id`, `prompt`) and the dedupe behaviour are properties of
that hook implementation; re-read the hook before assuming them elsewhere.
