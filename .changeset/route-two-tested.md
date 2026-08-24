---
"mrbinnacle-skills": patch
---

Test `Check 0` against its own claim, and confirm the redundancy it prescribes is load-bearing.

PR #118 recorded a second occurrence of the return-channel failure and stated one limit explicitly: route 2's standalone sufficiency was untested and not claimed. It has now been tested against the same four agents in the same session.

## The result

| agent | route 2 (named file) | route 1 (message) | outcome |
|---|---|---|---|
| A | 6 of 6 blocks, 10,869 bytes | — | complete via route 2 |
| B | 7 of 7 blocks, 20,500 bytes | completion summary | complete via route 2, signalled via route 1 |
| C | blocked by the host's own guard, 0 bytes | 6 of 6 blocks, full content | complete via route 1 fallback |
| D | never given a channel | — | never delivered |

**With no channel named: 0 of 4 agents delivered**, across three rounds and nine idle notifications carrying no content. **With a channel named: 3 of 3 delivered.** Agent D is a natural control — the only one never given a channel and the only one that never delivered.

The returns were substantive. One block quotes a card's origin paragraph verbatim, names the section heading it sits under, and lists the distinctive literals requested. The agents had done the work throughout; none of it could reach the session until a channel existed to carry it.

## Route 2 has two failure modes, and neither is the agent's fault

**It has no completion marker.** An earlier revision of this record reported one return as incomplete — "five blocks where seven were asked for". That was wrong: the file was read while the agent was still writing it, 5 blocks at sampling and 7 when finished. `Check 0` names a path but never says how the reader knows the write finished. A partially-written file reads as a complete short answer and nothing distinguishes the two.

**The host's tooling policy can forbid the write.** Agent C's file stayed at 0 bytes because a `PreToolUse` Bash guard on this machine refuses prose authored into a `.md` file through a heredoc — correctly, since that mechanism is known to fail here. The agent fell back to route 1 and returned everything in the message body.

## What the evidence actually establishes

This finding moved three times as evidence arrived, and the movement is recorded rather than smoothed over. First reading: route 2 is sufficient and route 1 is not. Second: the routes are not redundancy, the file carries payload and the message carries completion. **Current reading, on the full evidence: the check's redundancy framing is correct, and the reason is sharper than the check states** — the two routes fail for unrelated causes, so one failing genuinely is survivable. Agent C is the proof.

**The load-bearing instruction is to name a payload channel at all.** Which one mattered less than that one existed.

## Two additions `Check 0` would benefit from

1. A completion contract — a signal when the write is done, with an unsignalled file treated as still in flight.
2. Name the writing tool, not just the path, so the agent does not reach for a mechanism the host blocks.

Neither edit is made here. Changing the check is a change to the card's procedure and belongs in its own reviewable diff.

No published card changed. No count moved. The published tree is unmodified by this pull request.
