---
"mrbinnacle-skills": major
---

Each plugin is now packaged at its own bucket, `skills/<bucket>/`, with a `.claude-plugin/plugin.json` that states its name, version and exact card list, and each marketplace entry points its `source` at that bucket. Before this change an install was a copy of the whole repository with no plugin manifest, so `claude plugin eval` loaded each plugin with no name, no version and no skills. The install path changes from the whole repository to one bucket, which ADR 0002 makes a major change; the decision is recorded in ADR 0004. The standing obligations move to `conformance v3`, because O7 now reads each plugin's own manifest. Two links between buckets now point at the published repository, since an install no longer carries the other buckets.
