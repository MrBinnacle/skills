---
"mrbinnacle-skills": patch
---

The changeset step now decides on content: a branch named for an issue needs a changeset newer than its base that cites that issue, so a copy of `.changeset/` that resets file times no longer passes a branch that added none. It replaces the file-time test added in the brand-kit fix.
