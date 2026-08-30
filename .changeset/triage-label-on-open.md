---
"mrbinnacle-skills": patch
---

Repository automation: an issue that opens with no label now receives `needs-triage` from a workflow on `issues: opened`. An unlabeled issue is invisible to every selector that keys on a triage role, and the only guard for that ran on one host. The workflow adds the one label and touches nothing else; no published card changed.
