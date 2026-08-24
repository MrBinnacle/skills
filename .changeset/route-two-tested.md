---
"mrbinnacle-skills": patch
---

Test `Check 0`'s second return route directly, and record that the two routes are not redundant.

PR #118 recorded a second occurrence of the return-channel failure and stated one limit explicitly: route 2's standalone sufficiency was untested and not claimed. It has now been tested, against the same four agents in the same session, and the result changes what the check should say.

**Route 1 — three attempts, zero recoveries.** The original dispatch, a `SendMessage` restating the output contract verbatim, and a third wake. Each produced an idle notification carrying no content. Nine such notifications across four agents.

**Route 2 — one attempt, immediate recovery.** Three agents were re-instructed with the bounded write escalation quoted in `Check 0`, each naming one absolute path. Two of three wrote their file within the same wake — 10,869 and 14,175 bytes of the requested verbatim card extracts, in the requested block format. The third had not written at the time of recording. One of the two returns carried five blocks where seven were asked for: route 2 delivered, and delivered incompletely, in the same run.

**The returns were substantive.** One block quotes a card's origin paragraph verbatim, names the section heading it sits under, and lists the distinctive literals requested. The agents had done the work the whole time. None of it could reach the session through plain text.

**Finding.** Route 2 is sufficient on its own; route 1 is not. `Check 0` currently presents the two routes as redundancy — "so one failing is survivable" — and that framing understates the asymmetry. Route 1 failed three times against the identical task, agents and session in which route 2 succeeded on the first attempt. The dispatch should state the file path, and treat `SendMessage` as a supplement to it rather than as the channel. A future edit to `Check 0` should reorder the routes to match.

This is recorded in the candidate's `PROVENANCE.md` as a separate dated section rather than folded into the occurrence above it, so the order of evidence stays visible: the limit was stated first, then removed by testing it.

No published card changed. No count moved. The published tree is unmodified by this pull request.
