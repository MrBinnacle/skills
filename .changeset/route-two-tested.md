---
"mrbinnacle-skills": patch
---

Test `Check 0`'s two return routes against each other, and record what each one actually carries.

PR #118 recorded a second occurrence of the return-channel failure and stated one limit explicitly: route 2's standalone sufficiency was untested and not claimed. It has now been tested, against the same four agents in the same session.

**Route 1 — three attempts, zero findings recovered.** The original dispatch, a `SendMessage` restating the output contract verbatim, and a third wake. Each produced an idle notification carrying no content. Nine such notifications across four agents.

**Route 2 — one attempt.** Three agents were re-instructed with the bounded write escalation the check quotes, each given one absolute path. All three created their file. Two delivered complete content: 6 of 6 blocks (10,869 bytes) and 7 of 7 blocks (20,500 bytes, including the extra field requested for three published cards). The third created its file at 0 bytes.

**The returns were substantive.** One block quotes a card's origin paragraph verbatim, names the section heading it sits under, and lists the distinctive literals requested. The agents had done the work the whole time. None of it could reach the session through plain text.

## A gap in route 2, found by falling into it

This record first reported one return as incomplete — "five blocks where seven were asked for". **That was wrong, and how it went wrong is the more useful finding.** The file was read while the agent was still writing it: 5 blocks and 14,175 bytes at the moment of sampling, 7 blocks and 20,500 bytes when finished. A partial write was measured and recorded as an incomplete delivery.

`Check 0` tells the dispatcher to name one file path. **It does not say how the reader knows the write has finished.** File existence is not completion, and a file has no end-of-message marker the way a message does. The failure is quiet in the dangerous direction: a partially-written file reads as a complete short answer, and nothing distinguishes the two. The 0-byte third file is the same gap at its limit.

Route 2 needs a completion contract, not just a path — a signal when the write is done (a message naming the finished file, a sentinel final line, or an atomic rename from a temporary name), with an unsignalled file treated as still in flight.

## What each route is for

The completion signal that resolved this arrived *as* a `SendMessage` carrying a content-bearing summary — the first message from any of these agents to carry content rather than an idle notification. **Route 1 is not inert.** Across three attempts it failed to carry the *findings*; it succeeded at carrying a *pointer to where the findings were written*.

So the two routes are not redundancy, which is how the check currently frames them ("so one failing is survivable"). They carry different things: **the file path carries the payload, and the message carries completion.**

A future edit to `Check 0` should say that and add the completion contract. Neither edit is made here — changing the check is a change to the card's procedure and belongs in its own reviewable diff.

No published card changed. No count moved. The published tree is unmodified by this pull request.
