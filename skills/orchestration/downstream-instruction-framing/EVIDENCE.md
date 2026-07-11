# EVIDENCE — downstream-instruction-framing

Provenance record per the collection's evidence convention (see top-level README →
"Evidence records"). Fields are honest by construction: UNMEASURED means exactly that.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-06-07, a private production project (security handoff): the user caught an "Approved Decisions (Already Made — Do Not Re-Litigate)" header in a handoff document and required correction, then generalized the rule ("there's a time and a place for 'do not re-litigate' but it's never an ALWAYS framing"). The SKILL.md Example is the real before/after pair, identifiers genericized. Full entry: [gotchas.md](gotchas.md) → `[OBSERVED]`. |
| **Validated against** | Origin incident only, plus continuous in-house use since (the author's global rules mandate invoking it before drafting any handoff/plan/subagent prompt). No controlled screen or paired eval has been run yet. |
| **Screen result** | UNMEASURED. Candidate screen task: ask a stock agent to write a handoff for a partially-explored plan; behavioral oracle = does the artifact license downstream disagreement and attach revisit conditions, vs. blanket command framing? NOTE: this is a *judgment-quality* skill — the oracle is behavioral, not deterministic, so a screen here needs a calibrated judge, which is exactly the harder class of measurement. |
| **Paired verdict** | UNMEASURED. Methodology for any future paired Full-vs-Null run: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md) (registered 2026-07-10). |
| **Standing cost** | Description ≈ 45 tokens if model-invocable (the author runs it model-invocable with the description always loaded — it must fire *before* drafting begins, which after-the-fact triggers can miss). Body ≈ 7 KB, loads only on invocation. |
| **Re-screen trigger** | Next major frontier-model release. If a re-screen (or accumulated observation) shows stock agents defaulting to proposal-mood handoffs with revisit clauses unprompted, this skill should be publicly RETIRED with this record updated — that outcome is a feature of the collection, not a failure of the skill. |
