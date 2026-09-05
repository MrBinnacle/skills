---
"mrbinnacle-skills": patch
---

`AGENTS.md` step 5 of the rotation pass now names the writer of the `Re-screen trigger` attestation and states the clause's shape. `git-pull-rebase-trap` carries the first attestation, and its `Paired verdict` row now records the sized run.

**What was wrong.** The currency gate added on 2026-08-30 (#183, PR #189) required an attestation clause on every card's `Re-screen trigger` row and typed its absence as `attestation_missing`. The only step that mentioned writing one was step 6, which runs only for receipts that already passed step 5. The clause's shape, and the pass as its writer, were both in the maintainer's decision record the gate was built from (the current-receipt rule, resolved 2026-08-29) and did not survive transcription into this file. The first run of the gate (#219, 2026-09-04) measured the consequence: three axes passed for the sized receipt, the fourth failed for it and for all fourteen published cards, because no card carried a date on that row and the word "attestation" appeared nowhere in the collection. No receipt could reach the record step.

**What changed.** Step 5 states the clause shape (`Attested <date>: no named trigger has fired since <receipt source.date>; checked <what was read>`), makes step 5 the writer, and says when it is written and re-dated. `attestation_expired` now also fires when the attestation predates the newest release tag, which is the lease the decision record specified. Step 6 no longer claims to re-date the attestation.

**On the card.** The `Re-screen trigger` row carries `Attested 2026-09-04`, with the two sources read named. The `Paired verdict` row's verdict of record is the 2026-09-03 sized receipt: `CANT_TELL_YET`, typed reason hazard not met, because zero of 64 epochs ran `git pull` and under the `skill-harness#403` ruling a Null arm that never enters the hazard fails the fixture's qualification. The row previously told a reader the sized run had not happened. The k=8 micro-run stays in the row as history with its measurements intact, and the row states why its GO datum did not transfer: the two runs used different subjects, and one pulled in 8 of 8 untreated epochs while the other pulled in 0 of 32.

**Not changed.** No verdict word moved: both receipts read `CANT_TELL_YET`. The three required rows are unchanged. No validator changed; none reads the attestation.
