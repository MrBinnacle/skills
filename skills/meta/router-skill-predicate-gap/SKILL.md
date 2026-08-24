---
name: router-skill-predicate-gap
description: "A router rule can be live, healthy and match nothing anyone types: the pattern list omits the ordinary word, or a JSON escape left the pattern inert. Use before claiming a discipline is hook-enforced."
---

# Router skill predicate gap

## Problem

A skill is documented as MANDATORY and wired into a `UserPromptSubmit` router hook, so the
rule looks enforced rather than remembered. It is not: **the hook runs, exits 0, and matches
nothing**, because its regex list omits the word users most often type for the thing it
guards. The wiring is present, the hook is healthy, the config is valid — and nothing
distinguishes "the predicate did not match" from "no prompt needed it."

## Use when

- A rule file says a skill is MANDATORY, and you cannot recall the reminder arriving.
- You are about to write, or repeat, the claim that a discipline is hook-enforced.
- A rule's `patterns` list was seeded from error signatures or example phrasings and never
  re-read.
- The skill did fire once, and you have not checked *which* pattern matched.

## Root cause

Router patterns are seeded from the highest-precision triggers —
error strings, slash commands, distinctive nouns — because the ordinary word for the
artifact looks too broad to add safely. The predicate then matches specialist phrasing and
misses the common request: **model-pull wearing a hook's clothes**.

## Solution

### 1. Test the negative first, against the live hook

Do this before editing anything. Probe the suspect prompt **and a known-good fixture in the
same run** — the known-good is a positive control, and without it the run is
uninterpretable:

```sh
cd ~/.claude/hooks
for p in "write me a plan for issue 18" "<a phrase you know this rule matches>"; do
  out=$(echo "{\"session_id\":\"neg-$RANDOM$RANDOM\",\"prompt\":\"$p\"}" | python skill-router.py)
  echo "$out" | grep -q "<skill-name>" && echo "FIRES  : $p" || echo "SILENT : $p"
done
```

Empty output on the suspect prompt means it did not fire — **but only if the control
fired**. Empty is also what a crashed interpreter prints; a silent control means the harness
is broken, not the predicate
([`success-test-accepts-any-output`](../../engineering/success-test-accepts-any-output/SKILL.md)
→ rule 4). Make `session_id` unique per probe — these routers dedupe per session, so a
reused id makes a firing rule look silent.

### 2. Assert that no pattern holds a control character

A JSON string escape is not a regex escape: in a JSON rule file `"\b"` is the **backspace
character**, and a regex word boundary must be written `"\\b"`. The damaged pattern is still
a valid regex, so `re.compile()` accepts it, and it matches nothing forever. Grep the
compiled patterns rather than reading them:

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

### 3. Read the actual patterns

```sh
python -c "
import json;d=json.load(open('skill-rules.json'))
for r in d['rules']:
    if r['skill']=='<skill-name>': print(json.dumps(r['patterns'],indent=1))
"
```

Compare against how the artifact is actually requested, not how it is named in the rule
file.

### 4. Add patterns that target authoring, not mention

Match the *verb plus the noun*, so conversation about the thing stays silent while a request
to produce one fires:

```json
"\\b(writ(e|ing)|draft(ing)?|creat(e|ing)|produc(e|ing)|author(ing)?|updat(e|ing)|need|want|give me)\\b.{0,30}\\bplans?\\b",
"\\b(implementation|execution|migration|rollout|remediation|tooling|project|build)\\s+plans?\\b",
"\\bplans?\\b.{0,20}\\bfor\\b.{0,25}(#\\d+|issue|ticket)"
```

Then validate the file:
`python -c "import json;json.load(open('skill-rules.json'));print('JSON valid')"`.

### 5. Probe positives, then false positives, through the step-1 loop

Run the positive set — the prompts a user actually types (`I need a plan`). Every line
must read `FIRES`. Then run the false-positive set through the
same loop, and **include words that share the stem** (`the plane landed`, `explain the
planner architecture`) — probing them is the only way to know the `\b` boundaries hold.
Every line must read `SILENT`; a `FIRES` here is a boundary that does not hold.

## Verification

The finding is proven by a before/after pair on the *same* prompt string against the *same*
hook:

```
before:  "write me a plan for issue 18"  -> silent
after:   "write me a plan for issue 18"  -> fires
```

Best case, use the user's own message from the session that exposed the gap — a probe you
invented can be accused of being chosen to fire.

## Example

2026-08-18. A machine-level rule file marked `downstream-instruction-framing` as
*router-enforced, MANDATORY before ANY handoff / plan / ADR / subagent-prompt* — and the
bare word "plan" was in no pattern. The skill had fired earlier that session only because
the work also involved an ADR: `\bADR\b` matched, and the correct behaviour was
coincidence. Tested negative first (`write me a plan for issue
18` → silent), three patterns added, and the user's own previously-unmatched message then
fired; five false-positive probes stayed silent, including `plane` and `planner`. The full
record and the 2026-08-23 second occurrence live in `gotchas.md`.

## Notes

- **A passing read is not evidence.** The gap is invisible in the rule file and
  `settings.json`; only piping a prompt into the live hook finds it.
- **This is not dead wiring.** A hook that never fires at all, or that reads the wrong stdin
  shape, is a different diagnosis with a different fix.
- **The stake is the layer-placement rule.** A discipline that must fire cannot live in the
  skill layer, because skill retrieval is model-pull. A router rule moves it to the hook
  layer *only to the extent its predicate is complete* — an incomplete one leaves the
  discipline unenforced while the documentation claims otherwise, which is worse than no
  hook: it retires the vigilance that would have compensated.
- **A router rule deserves a test suite. A test suite is what catches a predicate gap; a
  reading is not.** And a per-rule suite is not enough: count fixture coverage per pattern,
  and give every deliberately-broad pattern a fixture only it can satisfy — a green
  per-rule suite is compatible with any number of dead patterns, because fixtures land on
  whichever pattern matches first and the broad ones collect none. The measured case is in
  `gotchas.md`.

Verified against a live `skill-router.py` UserPromptSubmit hook, 2026-08-18.
The stdin envelope shape (`session_id`, `prompt`) and the dedupe behaviour are properties of
that hook implementation; re-read the hook before assuming them elsewhere.
