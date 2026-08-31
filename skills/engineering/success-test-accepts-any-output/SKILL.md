---
name: success-test-accepts-any-output
description: A success check accepting any non-empty output passes on failure, because failure output is non-empty too. Use when a script reports OK but nothing happened, or a probe says NOT-FOUND batch-wide.
---

# A Success Test That Accepts Any Output Is Not a Test

## Problem

A check reports success and the operation did not happen. The check is not
lying about what it saw — it is reporting truthfully on a predicate that cannot
distinguish success from failure, because **failure output satisfies the
predicate too.** This is not the same bug as a missing check. A missing check
is loud: nothing claims the work is done. This one is silent and worse, because
it manufactures positive evidence.

## Use when

Any of these, in any language:

- A shell retry loop whose success test is `[ -n "$out" ]`, `[ $? -eq 0 ]` on a
  command that exits 0 on API errors, or a grep for a substring that appears in
  both outcomes.
- `gh api ... --jq .some_field` — `gh` prints the API's error JSON to stdout,
  so `--jq` on a 4xx/5xx body yields a non-empty string.
- A test helper that stringifies both sides before comparing:
  `String(got) === String(want)` passes on `check('x', 1, '1')`.
- A verification script that counts lines, checks a file exists, or greps for a
  header, where the failure mode also produces lines, a file, or that header.

**The tell:** you can describe the failure mode and it still satisfies the
predicate. If you cannot construct a failing input that the check rejects, the
check is decorative.

## Solution

Four rules, in order of how often they pay.

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

For `gh` specifically: prefer `--silent` (documented) plus an explicit
exit-code test, or capture stderr separately when you need the body.
`2>/dev/null` hides the diagnostic while leaving the error body on stdout —
check where a tool actually writes errors before redirecting. The *stream* an
error body lands on is undocumented for `gh api`: that claim rests on this
card's dated Example, reproduced once, not specified — so assert the success
shape rather than rely on where the error text lands.

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
the caller knows which property it means: `check('ids', set.size, 4)` states
its subject; `check('ids', set, 4)` does not.

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
print the same thing, so the predicate cannot tell a true negative from a
probe that never ran. Put a known-good case in the batch and require it to come
back positive:

```sh
# WRONG — every line is a finding, and a bad path prints the same six lines
for p in "$SUSPECT_1" "$SUSPECT_2"; do
  probe "$p" | grep -q "$MARKER" && echo "HIT $p" || echo "MISS $p"
done

# RIGHT — the control fails loudly, before any MISS is believed
for p in "$KNOWN_GOOD" "$SUSPECT_1" "$SUSPECT_2"; do ... done
[ "$known_good_result" = HIT ] || { echo "HARNESS BROKEN, findings void"; exit 1; }
```

**The tell is a clean sweep.** When every probe in a batch returns the
negative — including cases you expected to pass — suspect the harness before
the subject. A real predicate gap is usually partial.

## Verification

Prove the check can fail. Force the failure and confirm the check reports it:

- Point the write at a nonexistent resource, or unset the auth token.
- Swap a passing assertion's `want` to a different-typed equal-looking value
  (`4` vs `'4'`) and confirm it now goes red.

When replacing a loose comparison with a strict one, record the pass/fail
counts before and after: identical counts prove nothing was relying on the
looseness; a new failure is a genuine find, not a regression.

## Example

Session of 2026-08-17, `workspace_lint`. GitHub's GraphQL endpoint returned
HTTP 503 for roughly fifteen minutes while REST reads kept working — `gh issue
create` and `gh issue comment` both route through GraphQL. A retry loop
testing `[ -n "$url" ]`, with `2>/dev/null` hiding the diagnostic, printed
`#44 OK {"message":"No server is currently available…"}` for both targets;
re-reading the comment lists showed neither had posted. The fix was the `case`
statement in rule 1 plus the re-read in rule 3. In the same session, the
project's own test harness carried `String(got) === String(want)` in two
copies; one shared `Object.is` harness replaced both, and the assertion counts
held at 52 and 73 with zero failures — behaviour-preserving, not merely green.

## Notes

- **The instrument is not exempt.** Both Example instances sat inside
  verification machinery — a retry loop and a test harness — in a repository
  whose product detects false-green reporting. Verification code is written
  once, read never, and tested by nobody: audit it first, not last. Confirmed
  a third time 2026-08-23, when a throwaway probe harness built *to audit a
  router* produced the false finding itself — see `gotchas.md`.
- **Rule 4 is the one this card was missing.** The 2026-08-17 instances were
  false positives. A false *negative* reads as diligence, which is why it
  survives longer: nobody re-examines a probe that found a problem.
- **The family this belongs to.** The same defect wears more than one costume: a
  link checker green because throttling suppressed the requests, a CI gate
  that only fires on a trigger nobody pulls, and a test passing because the
  mock satisfied it — the last is
  [`mock-masked-stub-trap`](../mock-masked-stub-trap/SKILL.md). In every case
  the predicate is satisfied by the failure it was written to catch, so the
  question to ask of any green is: what input would make this red?
