# EVIDENCE — github-pages-deploy-verification

Provenance record per the collection's evidence convention (see top-level README →
"Evidence records"). Fields are honest by construction: UNMEASURED means exactly that.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-05-27, the author's public [azimuth](https://github.com/MrBinnacle/azimuth) repo (WCAG-contrast fix session, commits `17e8361` and onward): (1) a poll predicate matched pre-deploy content (`case-footnote` existed before; only its color value changed) — instant false-positive "verified"; (2) a `sleep 35 && curl` chain was blocked by the Claude Code Bash harness, cancelling parallel tool calls. Both hit within ~30 minutes of one task. This is the collection's rare **publicly checkable origin** — the repo and the deployed page are public. Full entries: [gotchas.md](gotchas.md) → `[OBSERVED]`. |
| **Validated against** | Origin incidents only. Model in use at the incidents was not recorded. No controlled screen or paired eval has been run yet. |
| **Screen result** | UNMEASURED. Candidate screen task: a repo with a Pages-style deploy where a committed change alters only a CSS *value* on an existing selector; deterministic oracle = did the agent's verification poll on content unique to the new deploy (vs. exiting on pre-existing content)? |
| **Paired verdict** | UNMEASURED. Methodology for any future paired Full-vs-Null run: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md) (registered 2026-07-10 — note its double-ceiling finding: well-specified self-contained tasks may be unmeasurable at frontier-model ceiling; that finding is a prior here, not a result). |
| **Standing cost** | Description ≈ 45 tokens if model-invocable. In the author's setup it runs as a name-only entry (near-zero standing cost); adopters can run it either way. Body ≈ 5.6 KB, loads only on invocation. |
| **Re-screen trigger** | Next major frontier-model release, or a Claude Code harness change to the sleep-chain blocking behavior (which would obsolete half the skill). If a re-screen shows stock agents picking deploy-unique poll markers unprompted, this skill should be publicly RETIRED with this record updated — that outcome is a feature of the collection, not a failure of the skill. |
