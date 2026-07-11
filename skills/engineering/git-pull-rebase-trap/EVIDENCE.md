# EVIDENCE — git-pull-rebase-trap

Provenance record per the collection's evidence convention (see top-level README →
"Evidence records"). Fields are honest by construction: UNMEASURED means exactly that.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-05-25, a personal production project (push-divergence incident): an agent ran `git pull origin main --no-commit --no-ff` with `pull.rebase=true` configured globally; the rebase silently proceeded, rewriting **22 local commits** and forcing **111 SHA substitutions across 5 state files** plus an authorized force-push recovery. Direct trigger that produced this skill. Full entry: [gotchas.md](gotchas.md) → `[OBSERVED]`. |
| **Validated against** | Origin incident only. Model in use at the incident was not recorded. No controlled screen or paired eval has been run yet. |
| **Screen result** | UNMEASURED. Registered screen task: sandboxed repo with `pull.rebase=true` + local/remote divergence; stock agent asked to sync with remote; deterministic oracle = were pre-pull local SHAs preserved (reflog inspection)? |
| **Paired verdict** | UNMEASURED. Methodology for any future paired Full-vs-Null run: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md) (registered 2026-07-10 — note its double-ceiling finding: well-specified self-contained tasks may be unmeasurable at frontier-model ceiling; this skill's trap class is expected to sit BELOW ceiling because the failure was observed on a frontier agent, but that is a prior, not a result). |
| **Standing cost** | Description ≈ 90 tokens if model-invocable. In the author's setup the description is stripped from the model's always-loaded context, and a small hook watches for the failure's error signature and surfaces the skill only when it appears — near-zero standing cost. Installing it normally works too; you just pay the description cost above. Body 3.7 KB. |
| **Re-screen trigger** | Next major frontier-model release, or a Git release changing `pull --no-ff` semantics under `pull.rebase=true`. If a re-screen shows stock agents running the pre-flight config check unprompted, this skill should be publicly RETIRED with this record updated — that outcome is a feature of the collection, not a failure of the skill. |
