---
cases:
  decision-rights-issue-bodies: fires
  decision-rights-near-miss: does-not-fire
  subagent-handback-brief: fires
  subagent-handback-celery-worker: does-not-fire
  subagent-handback-dispatch: fires
  subagent-handback-instructions: fires
  subagent-handback-self-dispatch: fires
controls:
  mrbinnacle-orchestration@mrbinnacle-skills: subagent-handback-celery-worker
---

# What this suite is supposed to contain

The eval cases for the `mrbinnacle-orchestration` plugin. `claude plugin eval` reads them from `evals/` under the plugin root.

`cases:` names every case with the direction it can fail in. `controls:` names the case that can fail in the should-not-fire direction for this plugin. The pre-flight in the research repo refuses a run when the declared set and the discovered set disagree.

Two cards have cases here. `decision-rights` has a should-fire case (`decision-rights-issue-bodies`) and its should-not-fire partner (`decision-rights-near-miss`). `subagent-handback` has four should-fire cases and one should-not-fire partner (`subagent-handback-celery-worker`). In `subagent-handback-dispatch`, the user dispatches and the agent writes the prompt. `subagent-handback-instructions` and `subagent-handback-brief` make the same request in other words, "Draft the instructions I should give it" and "Write me a brief for it", so the word "prompt" does not appear. In `subagent-handback-self-dispatch`, the agent under test dispatches. The sweep is the same in all four; the three variants were added for [#609](https://github.com/MrBinnacle/skills/issues/609).

## Runs

Every `subagent-handback` case has been run. The first three runs below checked `subagent-handback-dispatch` and `subagent-handback-self-dispatch` (for [#601](https://github.com/MrBinnacle/skills/issues/601) and #609) against the card's description as narrowed in #572, which opened "Use before dispatching a subagent for research". The later runs checked three candidate descriptions; see [The description that shipped](#the-description-that-shipped).

- 2026-10-22, Claude Code 2.1.308, `claude plugin eval` with `--runs 1 --model opus`. Each arm ran `claude-opus-5-5` once. The arm with the plugin did not invoke `subagent-handback`: it ran one `Glob` over `payments/` and then wrote the brief. The arm without the plugin did the same. The `skill-fires` grader scored both arms 0. The run cost USD 0.16.
- 2026-10-22, `subagent-handback-dispatch`, Claude Code 2.1.308, `--runs 5 -j 4 --model opus --no-publish`. Each arm ran `claude-opus-5-5`. With the plugin: scores `[0, 0, 0, 0, 0]`. Without: `[0, 0, 0, 0, 0]`. Cost USD 0.82. Recorded in [#609](https://github.com/MrBinnacle/skills/issues/609). Pooled with the first run, the card was invoked in 0 of 6 with-plugin runs.
- 2026-10-22, `subagent-handback-self-dispatch`, Claude Code 2.1.308, `--runs 5 -j 4 --model opus --no-publish --max-cost-usd 3`. Each arm ran `claude-opus-5-5`. With the plugin: scores `[1, 1, 1, 0, 1]`. Without: `[0, 0, 0, 0, 0]`. Cost USD 1.90. In each of the 4 runs that invoked the card, the `Skill` call was the first tool call, before any `Agent` call. In 3 of those 4 runs the agent then called `Agent`; in the fourth it ran the sweep itself with `Glob`. The run that did not invoke the card called `Agent` first. Every run in the arm without the plugin called `Agent` first.

### What the two cases separate

The sweep text is the same in both cases. These things differ:

- the opening sentence: "I am about to send a background agent" in the original, "Send a background agent" in the variant;
- the closing request: "Write me the prompt I should send it" in the original, "Dispatch it now" in the variant;
- `allowed_tools`: the variant adds `Agent`;
- `max_turns`: the variant sets 10, and the original sets none;
- `tags`: `seed` in the original, `variant` in the variant.

The first three are the one change under test: who dispatches. `tags` select cases for the runner. `max_turns` caps a run at 10 turns; the runs used 1 to 7, so the cap ended none of them.

The card was invoked in 0 of 6 runs when the user dispatches and in 4 of 5 when the agent under test dispatches. On this model and these prompts, the description narrowed in #572 reached the agent's own dispatch, and it did not reach a brief that the user will dispatch. This separates the two explanations in #609. It is an observation on one pair of cases at five or six runs each, not a measurement, and no disposition verdict follows from it.

### The description that shipped

#609 left one question open: does the card cover a prompt the agent writes for a subagent that the user will dispatch? It does. A user who asks for that prompt is about to dispatch a research subagent, and the card's checks (a named return channel, a matching tool grant) belong in the prompt. So `subagent-handback-dispatch` stays a should-fire case, and the description was the defect, not the case.

Three candidate descriptions were run on 2026-10-22 with Claude Code 2.1.309, `--model opus --no-publish`, 5 runs per arm, each arm on `claude-opus-5-5`. Each cell gives the runs that fired with the plugin. The arm without the plugin fired in none of the should-fire runs. "Not run" means the case did not yet exist or was not run under that description.

| Description opens | `-dispatch` ("the prompt") | `-instructions` | `-brief` | `-self-dispatch` | `-celery-worker` (correct = silent) |
|---|---|---|---|---|---|
| "Use when briefing or dispatching a research subagent" | 1 of 5 | not run | not run | 4 of 5 | 5 of 5 |
| "Use when prompting or dispatching a research subagent" | 5 of 5 | 4 of 5 | 2 of 5 | 5 of 5 | 10 of 10, in two runs of 5 |
| "Use when prompting, briefing or dispatching a research subagent" | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 |

Costs, both arms together: under the first description, USD 0.83 for `-dispatch` and USD 3.68 for `-self-dispatch` and `-celery-worker` run together. Under the second, USD 0.98 for `-dispatch`, USD 0.94 for `-instructions`, USD 0.81 for `-brief`, USD 2.28 for `-self-dispatch`, and USD 1.69 for one of the two `-celery-worker` runs. Under the third, all five cases ran in one invocation for USD 6.21.

For the control, a correct run is one where the card did not fire and the agent still answered the question; the arm without the plugin was also correct in every run.

The second description matched the user's own word in `-dispatch` ("Write me the prompt I should send it"), so its 5 of 5 there was partly a word match. The paraphrase cases show it: the same request worded as "instructions" fired in 4 of 5, and worded as "a brief" in 2 of 5. The third description names all three moments and fired in every run of every should-fire case. To stay within the 200-character limit, it drops the parenthesis "(SendMessage or file)" after "Name a return channel"; the card's body still names both channels.

The third description shipped: "Use when prompting, briefing or dispatching a research subagent, or when one goes idle with no report. Name a return channel, check its tool grant, verify every claim, negatives first."

All runs recorded here are observations at five runs per arm, not measurements, and no disposition verdict follows from them. `decision-rights-issue-bodies` and `decision-rights-near-miss` have not been run.
