---
"mrbinnacle-skills": patch
---

`parallel-review-disposition-schema`: the schema now prescribes namespaced finding identifiers, and a provider envelope covers returns that are not a flat panel.

The card already knew about this failure. Its `gotchas.md` records an observed incident dated 2026-08-17 in which two reviewers each numbered their findings `M1`–`M5` locally, a consolidator flattened both lists into one, kept one reviewer's `M4` under the name `M3`, and silently dropped that reviewer's actual `M3`. The dropped bug survived four commits and was later re-reported by a fresh reviewer as a new finding. The entry names three mitigations.

None of them had reached the instructions the card gives. The prescribed schema was four elements and the identifier rule was not among them, so a reader following `SKILL.md` exactly still built the collision. That gap is what this change closes: a fifth element requires each seat to prefix its findings with its seat of origin at dispatch, and requires the consolidator to paste those identifiers through unchanged.

A new `PROVIDER-ENVELOPE.md` carries the return contract for panels that are not flat — mixed provider kinds, one stage feeding the next, a seat recruiting its own specialist, or a provider that can fail or abstain. Its `run_id` + `stage_id` + `provider_id` supply the namespace the fifth element needs. The file also fixes three things that are easy to get wrong: one named parent adjudicates and writes; skipped, failed and unavailable providers are recorded rather than dropped, so a panel cannot silently shrink; and `writes_performed` is the provider's own assertion, verified by tool grant rather than believed.

Two boundaries are stated rather than assumed. A hook may verify envelope shape and required receipts; adjudicating a finding stays with the parent, because a subjective finding a hook can block is a subjective finding a hook has decided. And a provider that never returns produces no envelope at all — that is a delivery failure with a different control, and the file points at `subagent-research-reliability` for it instead of restating it.

The public trigger is unchanged and the description is byte-identical: at 196 characters it holds four characters against the published 200 bar, and the trigger stays narrow until serial, nested and parallel comparisons support broadening it. No controlled evidence row is touched and the card remains `UNMEASURED`; only the `Standing cost` row moves, because the card now carries a second template. This change closes an observed drop and claims no lift.
