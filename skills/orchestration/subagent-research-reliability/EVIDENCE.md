# EVIDENCE — subagent-research-reliability

Provenance record per the collection's evidence convention (see top-level README →
"Evidence records"). Fields are honest by construction: UNMEASURED means exactly that.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-05-28, a personal production project (threat-watch beat), two catches in one session: (1) pre-dispatch, a `research-scout` agent described as "performs web research ... with citations" turned out to have `tools: Read, Bash, Grep` — no web tools; (2) post-return, a verification pass caught real Cursor CVEs (CVE-2025-54136/54135) attributed to an arXiv paper that does not cite them — a fabricated cross-reference on real IDs. Direct triggers for Check 1 and Check 2 respectively. Full entries: [gotchas.md](gotchas.md) → `[OBSERVED]`. |
| **Validated against** | Origin incidents only. Model in use at the incidents was not recorded. No controlled screen or paired eval has been run yet. |
| **Screen result** | UNMEASURED. Candidate screen task: a dispatch config containing a web-toolless "research" agent + a research request; deterministic oracle = did the stock agent detect the tool-grant gap (or route to a web-capable agent) before dispatch, and did it verify citations before curating? |
| **Paired verdict** | UNMEASURED. Methodology for any future paired Full-vs-Null run: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md) (registered 2026-07-10 — note its double-ceiling finding: well-specified self-contained tasks may be unmeasurable at frontier-model ceiling; verification-discipline behavior on OPEN research tasks is harder to oracle and may need behavioral scoring rather than a deterministic check). |
| **Standing cost** | Description ≈ 50 tokens if model-invocable (the author runs it model-invocable). Body ≈ 4.6 KB, loads only on invocation. |
| **Re-screen trigger** | Next major frontier-model release, or a Claude Code release that surfaces agent tool grants at dispatch time (which would subsume Check 1). If a re-screen shows stock agents verifying citations and tool grants unprompted, this skill should be publicly RETIRED with this record updated — that outcome is a feature of the collection, not a failure of the skill. |
