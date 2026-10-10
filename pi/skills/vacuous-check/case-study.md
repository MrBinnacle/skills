# Case study — vacuous-check

The two origin incidents behind rules 1 to 3. Both happened in one working session on
2026-08-17, in a repository whose own product detects false-green reporting. The session's
work was filing and commenting on issues through `gh`, and maintaining that repository's test
harness.

## The retry loop (rules 1 and 3)

GitHub's GraphQL endpoint returned HTTP 503 for roughly fifteen minutes while REST reads kept
working. The session's `gh issue create` and `gh issue comment` calls failed for that window.

A retry loop wrapped the writes. Its success test was `[ -n "$url" ]`, and `2>/dev/null` hid
the diagnostic. For both targets it printed:

```
#44 OK {"message":"No server is currently available…"}
```

Re-reading the comment lists through a separate call showed that neither comment had posted.
The error body was non-empty, so the predicate accepted it as a URL.

The fix was the `case` statement in rule 1, which accepts only a URL-shaped value, plus the
re-read in rule 3.

## The test harness (rule 2)

In the same session, the repository's test harness compared values with
`String(got) === String(want)`, in two copies. That comparison accepts `check([1], '1')` and
`check(1, '1')`.

One shared `Object.is` harness replaced both copies. The assertion counts held at 52 and 73
with zero failures before and after the swap. Identical counts show that no assertion relied on
the looseness, so the swap preserved behaviour and was not merely green.

## Why both count as one occasion

The retry loop and the harness are two symptoms of one session. They count as one
occasion, because fan-out from a single run is not recurrence.
