---
name: success-test-accepts-any-output
description: |
  Fix for a hand-rolled success check that passes when the operation failed,
  because the check tests the SHAPE of the output rather than the fact of
  success. Use when: (1) a retry loop or script reports OK but the effect did
  not happen — no comment posted, no file written, no row inserted; (2) a `gh
  api ... --jq .field` call prints an error body to stdout and a `[ -n "$var" ]`
  test accepts it; (3) a test helper compares `String(got) === String(want)` so
  `check(1, '1')` and `check([1], '1')` pass; (4) a CI step or verification
  script goes green while the thing it verifies is broken. Root cause is that
  the success predicate accepts any non-empty / stringifiable output, and
  failure output is also non-empty and stringifiable. Fix: assert the specific
  shape success produces (a URL, an ID, a matching type), and verify by
  RE-READING the external state rather than trusting the command's own output.
author: Claude Code
version: 1.0.0
date: 2026-08-17
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
  and tested by nobody. Audit it first, not last.
- `2>/dev/null` on a CLI that writes errors to stdout converts a loud failure
  into a silent one. Check where the tool actually writes errors before
  redirecting.
- See also: `github-linkcheck-404-throttle-false-negative` (a link checker
  reporting green because throttling suppressed the requests),
  `ci-npm-audit-step-false-negative-trap` (a gate that only fires on a trigger
  nobody pulls), `mock-masked-stub-trap` (a test passing because the mock, not
  the code, satisfied it). Family candidate: FAMILY-005 in
  `_quarantine/_family-candidates.md` (was FAMILY-002; that id was assigned
  twice and this entry renumbered at S305).
