---
name: structure-at-the-write-site
description: |
  Fix for a downstream reader re-deriving a structural fact by pattern-matching
  prose that the program itself emitted. Use when: (1) a classifier greps an
  error/cause/log message for keywords to decide severity, retryability, or
  category; (2) a regex over a message string decides control flow, and adding a
  new message silently changes the outcome; (3) a status is inferred from an
  adjacent field that only correlates with it (a stage reached, a timestamp
  present, a count non-zero); (4) two consumers of the same message disagree
  about what it means. Root cause is that the site which KNEW the structural
  facts recorded only their prose summary, so every later reader must guess.
  Fix: record the facts as a value at the site that knows them, and delete the
  pattern match.
author: Claude Code
version: 1.0.0
date: 2026-08-17
---

# Record the Structure at the Site That Knows It

## Problem

Somewhere a function knows three things: what happened, whether the damage is
bounded, and what was established about the subject. It writes one sentence
containing all three, and returns.

Downstream, other code needs those facts back. It cannot ask, so it greps:

```ts
const UNBOUNDED = /remaining count unknown|abandoned after|stopped after/;
const bounded = !UNBOUNDED.test(cause);
```

This works for exactly the messages that existed when the regex was written. It
is not a parsing problem — it is an **information-destruction** problem, and the
destruction happened at the write site, several files away from where it hurts.

The failure is asymmetric in a way that makes it hard to spot: the pattern match
does not error, it returns the *wrong* answer, and by construction it returns
the answer that corresponds to "none of the known bad phrases were present" —
usually the optimistic one.

## Context / Trigger Conditions

- A regex, `includes()`, or `startsWith()` over a message/cause/reason string
  that decides a boolean, an enum, or a branch.
- Severity, retryability, or category derived from an error's *text* rather than
  its type or code.
- A structural fact inferred from a *correlated* field: "it reached stage 3, so
  the object must exist"; "the timestamp is set, so it succeeded".
- Two call sites producing messages for the same condition, only one of which
  matches the downstream pattern.
- **The tell:** you can add a legitimate new message at the write site and
  silently change a decision made three files away, with no test failing.

## Solution

### 1. Name the facts the write site knows

For each drop-out/error/exception site, list what it can state with certainty.
Typically: *what happened* (prose, for humans), plus two or three structural
facts (*is this bounded / recoverable / attributable*, *what did we establish
about the subject*).

### 2. Make them a record, and require it at every site

```ts
// BEFORE — one string, three facts destroyed
mark(id, stage, `root enumeration failed — ${cause}`);

// AFTER — the site states all three; a new site cannot omit them
export type Loss = {
  cause: string;              // specific and machine-readable; generic causes banned
  bounded: boolean;           // can the missing items be named and counted?
  target: 'present' | 'unreachable';   // what was established about the subject
};
mark(id, stage, {
  cause: `root enumeration failed — ${cause}`,
  bounded: false,   // the child list was never retrieved: cannot count or name what was missed
  target: 'present' // the parent itself was retrieved a moment earlier
});
```

Make the field **required**, not optional. The compiler then enumerates every
site that must decide, which is the whole benefit — each one is a small,
answerable question at the moment the answer is known.

### 3. Delete the pattern match, and read the field

Then hunt for the *other* readers. There is usually more than one, and they
usually disagree.

### 4. Keep the prose

The message still exists and is still for humans. This is not a replacement, it
is an addition — the record carries structure *alongside* the sentence.

## Verification

- **Grep for the deleted pattern** across the repo; a second consumer is common.
- **Write the test the regex could not pass.** Construct the case that fails
  *outright* and the case that fails *halfway*, and assert they classify
  correctly — the outright case is the one prose-matching usually gets wrong.
- **Check the direction of the old error.** If the old classification was
  optimistic, there is likely a green test asserting the optimistic value.
  Update it and record what it used to claim.

## Example

Session of 2026-08-17, `workspace_lint` (a coverage linter). A five-stage
traversal recorded each drop-out as a cause string. Two downstream readers
recovered structure from it, and **both were wrong**:

1. **Boundedness** was matched against three phrases. A root whose child list
   failed *outright* matched none of them and was classified **bounded** →
   report "qualified" → exit 3. One that failed *halfway* matched `stopped
   after` → **unbounded** → "disclaimed" → exit 2. **Failing harder produced the
   milder verdict.** A positive `request_status: incomplete` signal was misread
   the same way.
2. **Target state** was inferred from a correlated stage. The code stamped
   `resolved` on every child straight from the parent's listing — no retrieval —
   so a child whose own call returned 404 was reported `target: present`: a
   positive claim about an object the API had just refused.

One `Loss` record fixed both and deleted the regex. Each of the six drop-out
sites now states all three facts inline, and the reason for each is one comment
long because the site genuinely knows the answer.

## Notes

- **This is the write-side twin of "parse, don't validate."** That rule says to
  convert unstructured input into a structured value at the boundary. This one
  says: when *you* are the producer, never emit unstructured output that your
  own code must re-parse. The parsing you avoid is parsing you inflicted.
- **Error types are the same pattern.** `catch (e) { if (/timeout/.test(e.message)) retry() }`
  is this bug with a different noun. Throw a typed error carrying `retryable`.
- **Watch for the third reader.** Prose-derived facts spread: a log dashboard, an
  alert rule, and a report renderer can each grep the same sentence differently.
- See also: `append-only-evidence-design` (recording evidence so later readers
  cannot silently reinterpret it).
