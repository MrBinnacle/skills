---
cases:
  decision-rights-issue-bodies: fires
  decision-rights-near-miss: does-not-fire
  subagent-handback-celery-worker: does-not-fire
  subagent-handback-dispatch: fires
  subagent-handback-self-dispatch: fires
controls:
  mrbinnacle-orchestration@mrbinnacle-skills: subagent-handback-celery-worker
---

# What this suite is supposed to contain

The eval cases for the `mrbinnacle-orchestration` plugin. `claude plugin eval` reads them from `evals/` under the plugin root.

`cases:` names every case with the direction it can fail in. `controls:` names the case that can fail in the should-not-fire direction for this plugin. The pre-flight in the research repo refuses a run when the declared set and the discovered set disagree.

Two cards have cases here. `decision-rights` has a should-fire case (`decision-rights-issue-bodies`) and its should-not-fire partner (`decision-rights-near-miss`). `subagent-handback` has two should-fire cases and one should-not-fire partner (`subagent-handback-celery-worker`). In `subagent-handback-dispatch`, the user dispatches and the agent writes the brief. In `subagent-handback-self-dispatch`, the agent under test dispatches. The sweep is the same in both; the variant was added for [#609](https://github.com/MrBinnacle/skills/issues/609).

## Runs

Two cases have been run: `subagent-handback-dispatch` (for [#601](https://github.com/MrBinnacle/skills/issues/601) and #609) and `subagent-handback-self-dispatch` (for #609). Each run checked a case's prompt against the card's description as narrowed in #572.

- 2026-10-22, Claude Code 2.1.308, `claude plugin eval` with `--runs 1 --model opus`. Each arm ran `claude-opus-5-5` once. The arm with the plugin did not invoke `subagent-handback`: it ran one `Glob` over `payments/` and then wrote the brief. The arm without the plugin did the same. The `skill-fires` grader scored both arms 0. The run cost USD 0.16.

One run per arm is an observation, not a measurement. It does not show that the card fails to fire in general, and no verdict follows from it. It shows that this prompt, on this model, did not reach the card through the narrowed description.

- 2026-10-22, `subagent-handback-dispatch`, Claude Code 2.1.308, `--runs 5 -j 4 --model opus --no-publish`. Each arm ran `claude-opus-5-5`. With the plugin: scores `[0, 0, 0, 0, 0]`. Without: `[0, 0, 0, 0, 0]`. Cost USD 0.82. Recorded in #609. Pooled with the first run, the card was invoked in 0 of 6 with-plugin runs.
- 2026-10-22, `subagent-handback-self-dispatch`, Claude Code 2.1.308, `--runs 5 -j 4 --model opus --no-publish --max-cost-usd 3`. Each arm ran `claude-opus-5-5`. With the plugin: scores `[1, 1, 1, 0, 1]`. Without: `[0, 0, 0, 0, 0]`. Cost USD 1.90. In each of the 4 runs that invoked the card, the `Skill` call was the first tool call, before any `Agent` call. In 3 of those 4 runs the agent then called `Agent`; in the fourth it ran the sweep itself with `Glob`. The run that did not invoke the card called `Agent` first. Every run in the arm without the plugin called `Agent` first.

The two cases differ in one variable: who dispatches. The closing request ("write me the prompt" or "dispatch it now") and the `Agent` grant follow from it. The card was invoked in 0 of 6 runs when the user dispatches and in 4 of 5 when the agent dispatches. This separates the two explanations in #609. The description narrowed in #572 still reaches the moment when the agent under test is about to dispatch. It does not reach the moment when the agent writes a brief that the user will dispatch. Five runs per arm is an observation, not a measurement, and no disposition verdict follows from it. `subagent-handback-dispatch` stays a should-fire case. Whether the card should cover a brief the user dispatches is a scope question for the card, not a defect in either case. `decision-rights-issue-bodies`, `decision-rights-near-miss` and `subagent-handback-celery-worker` have not been run.
