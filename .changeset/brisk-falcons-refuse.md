---
"mrbinnacle-skills": patch
---

Remove the stale `_quarantine/subagent-research-reliability/` directory. Its provenance describes
the dead-letter patch shipped in `756403a`; the live `subagent-handback` card still contains the
three references the provenance names, so no unique copy was lost. Conformance O8 now rejects a
quarantine directory whose name matches a published card, preventing promotion residue from
returning. The standing obligations move to `conformance v4` because O8 is a new obligation.
