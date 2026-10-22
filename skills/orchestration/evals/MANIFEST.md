---
cases:
  decision-rights-issue-bodies: fires
  decision-rights-near-miss: does-not-fire
  subagent-handback-celery-worker: does-not-fire
  subagent-handback-dispatch: fires
controls:
  mrbinnacle-orchestration@mrbinnacle-skills: subagent-handback-celery-worker
---

# What this suite is supposed to contain

The eval cases for the `mrbinnacle-orchestration` plugin. `claude plugin eval` reads them from `evals/` under the plugin root.

`cases:` names every case with the direction it can fail in. `controls:` names the case that can fail in the should-not-fire direction for this plugin. The pre-flight in the research repo refuses a run when the declared set and the discovered set disagree.

Two cards have cases here. `decision-rights` has a should-fire case (`decision-rights-issue-bodies`) and its should-not-fire partner (`decision-rights-near-miss`). `subagent-handback` has a should-fire case (`subagent-handback-dispatch`) and its should-not-fire partner (`subagent-handback-celery-worker`).

## Runs

Only `subagent-handback-dispatch` has been run, once, for [#601](https://github.com/MrBinnacle/skills/issues/601). The run checked the case's prompt against the card's description as narrowed in #572.

- 2026-10-22, Claude Code 2.1.308, `claude plugin eval` with `--runs 1 --model opus`. Each arm ran `claude-opus-5-5` once. The arm with the plugin did not invoke `subagent-handback`: it ran one `Glob` over `payments/` and then wrote the brief. The arm without the plugin did the same. The `skill-fires` grader scored both arms 0. The run cost USD 0.16.

One run per arm is an observation, not a measurement. It does not show that the card fails to fire in general, and no verdict follows from it. It shows that this prompt, on this model, did not reach the card through the narrowed description. The other three cases have not been run.
