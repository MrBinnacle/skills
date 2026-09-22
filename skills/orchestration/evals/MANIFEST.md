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

Two cards have cases here. `decision-rights` has a should-fire case (`decision-rights-issue-bodies`) and its should-not-fire partner (`decision-rights-near-miss`). `subagent-handback` has a should-fire case (`subagent-handback-dispatch`) and its should-not-fire partner (`subagent-handback-celery-worker`). None has been run.
