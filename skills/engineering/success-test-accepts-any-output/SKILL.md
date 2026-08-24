---
name: success-test-accepts-any-output
description: A success check accepting any non-empty output passes on failure, because failure output is non-empty too. Use when a script reports OK but nothing happened, or a probe says NOT-FOUND batch-wide.
---

# A Success Test That Accepts Any Output Is Not a Test

## Problem

A check reports success and the operation did not happen. The check is not
lying about what it saw — it is reporting truthfully on a predicate that cannot
distinguish success from failure, because **failure output satisfies the
predicate too.**

This is not the same bug as a missing check. A missing check is loud: nothing
claims the work is done. This one is silent and worse, because it manufactures
positive evidence.

## Context / Trigger Conditions

Any of these, in any language:

- A shell retry loop whose success test is `[ -n "$out" ]`, `[ $? -eq 0 ]` on a
  command that exits 0 on API errors, or a grep for a substring that appears in
  both outcomes.
- `gh api ... --jq .some_field` — **`gh` prints the API's error JSON to stdout**,
  so `--jq` on a 4xx/5xx body yields a non-empty string. Verified 2026-08-17:
  during a GitHub GraphQL outage, a loop testing `[ -n "$url" ]` printed
  `#44 OK {"message":"No server is currently available..."}` twice while zero
  comments posted.
- A test helper that stringifies both sides before comparing:
  `String(got) === String(want)`. `check('x', 1, '1')` passes. So does
  `check('x', [1], '1')`. Verified 2026-08-17 in a repo whose entire purpose was
  detecting false-green reporting.
- A verification script that counts lines / checks a file exists / greps for a
  header, where the failure mode also produces lines, a file, or that header.

**The tell:** you can describe the failure mode and it still satisfies the
predicate. If you cannot construct a failing input that the check rejects, the
check is decorative.

## Solution

Three rules, in order of how often they pay.

### 1. Assert the shape success produces, not the absence of nothing

```sh
# WRONG — an error body is non-empty
url=$(gh api "repos/$R/issues/$N/comments" -F body=@msg.md --jq .html_url)
[ -n "$url" ] && echo OK

# RIGHT — only success is URL-shaped
case "$url" in
  https://github.com/*) echo "POSTED $url" ;;
  *)                    echo "FAILED: $url"; exit 1 ;;
esac
```

For `gh` specifically: prefer `--silent` plus an explicit exit-code test, or
capture stderr separately. `2>/dev/null` hides the diagnostic while leaving the
error body on stdout, which is the worst combination.

**Claim status, re-checked 2026-08-23 against the published `gh api` manual.**
`--silent` ("Do not print the response body") is documented, so the recommended
fix stands on the manual. The **stream** an error body is written to is *not*
documented either way — the manual describes `gh api` only as printing "the
response". That claim therefore rests on the dated 2026-08-17 observation in
this card's Example and nothing else. Treat it as reproduced-once, not
specified: assert the success shape (rule 1) rather than relying on where the
error text lands.

### 2. Compare identity, never stringification

```ts
// WRONG — passes on a type mismatch
const ok = String(got) === String(want);

// RIGHT — Object.is: NaN equals NaN, -0 does not equal 0.
// Stringify only for the human-readable message.
const ok = Object.is(got, want);
console.log(`${ok ? 'PASS' : 'FAIL'} ${name}: got=${show(got)} want=${show(want)}`);
```

Non-primitives must be reduced to a primitive **by the caller**, because only
the caller knows which property it means: `check('ids', set.size, 4)` states its
subject; `check('ids', set, 4)` does not.

### 3. Verify by re-reading the external state

A command's own output is not evidence that its effect occurred. After a write
that matters, read it back through a different call:

```sh
gh api "repos/$R/issues/$N/comments" --jq '.[].html_url' | tail -3
```

This is the only step that catches a success test you have not yet realised is
broken, so it is the one to keep when the others feel like overkill.

### 4. A finding of absence needs a positive control in the same run

Rules 1 through 3 defend a claim that something *happened*. The mirror claim —
**nothing happened** — has the same defect and no external state to re-read.
`NOT FOUND`, `SILENT`, `no match`, `0 results` and a crashed interpreter all
print the same thing, so the predicate cannot tell a true negative from a probe
that never ran.

Put a known-good case in the batch and require it to come back positive:

```sh
# WRONG — every line is a finding, and a bad path prints the same six lines
for p in "$SUSPECT_1" "$SUSPECT_2"; do
  probe "$p" | grep -q "$MARKER" && echo "HIT $p" || echo "MISS $p"
done

# RIGHT — the control fails loudly, before any MISS is believed
for p in "$KNOWN_GOOD" "$SUSPECT_1" "$SUSPECT_2"; do ... done
[ "$known_good_result" = HIT ] || { echo "HARNESS BROKEN, findings void"; exit 1; }
```

**The tell is a clean sweep.** When every probe in a batch returns the negative
— including cases you expected to pass — suspect the harness before the
subject. A real predicate gap is usually partial.

## Verification

Prove the check can fail. Force the failure and confirm the check reports it:

- Point the write at a nonexistent resource, or unset the auth token.
- Swap a passing assertion's `want` to a different-typed equal-looking value
  (`4` vs `'4'`) and confirm it now goes red.

**Behaviour-preservation check when replacing a loose comparison with a strict
one:** record the pass/fail counts before and after. Identical counts prove
nothing was relying on the looseness; a new failure is a genuine find, not a
regression. Verified: two suites held at exactly 52 and 73 assertions with zero
failures across a `String(...)` → `Object.is` swap.

## Example

Session of 2026-08-17, `workspace_lint`. GitHub's GraphQL endpoint returned
HTTP 503 for roughly fifteen minutes while REST reads kept working — `gh issue
create` and `gh issue comment` both route through GraphQL. A retry loop:

```sh
url=$(gh api ".../comments" -F "body=@$f" --jq .html_url 2>/dev/null)
if [ -n "$url" ]; then echo "#$1 OK $url"; return 0; fi
```

printed `#44 OK {"message":"No server is currently available…"}` for both
targets. Re-reading the comment lists showed neither had posted. The fix was the
`case` statement in rule 1 plus the re-read in rule 3.

In the same session, the project's own test harness carried
`String(got) === String(want)` in two copies. Replacing both with one shared
`Object.is` harness held the assertion counts exactly, which is what proved the
swap was behaviour-preserving rather than merely green.

## Notes

- **The instrument is not exempt.** Both instances above sat inside verification
  machinery — a retry loop and a test harness — in a repository whose product
  detects false-green reporting. Verification code is written once, read never,
  and tested by nobody. Audit it first, not last. Confirmed a third time on
  2026-08-23, in a hygiene pass over this very collection: the throwaway probe
  harness built *to audit a router* was itself the thing that produced the false
  finding. See `gotchas.md`.
- **Rule 4 is the one this card was missing.** The 2026-08-17 instances were both
  false positives — a check that said yes when the answer was no. A false
  negative reads as diligence, which is why it survives longer: nobody
  re-examines a probe that found a problem.
- `2>/dev/null` on a CLI that writes errors to stdout converts a loud failure
  into a silent one. Check where the tool actually writes errors before
  redirecting.
- **The family this belongs to.** The same defect wears several costumes: a link checker
  reporting green because throttling suppressed the requests, a CI gate that only fires on a
  trigger nobody pulls, and a test passing because the mock rather than the code satisfied it.
  The last of those is
  [`mock-masked-stub-trap`](../mock-masked-stub-trap/SKILL.md). In every case the predicate is
  satisfied by the failure it was written to catch, so the question to ask of any green is:
  what input would make this red?
