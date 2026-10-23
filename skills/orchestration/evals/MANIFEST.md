---
cases:
  decision-rights-issue-bodies: fires
  decision-rights-near-miss: does-not-fire
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

Two cards have cases here. `decision-rights` has a should-fire case (`decision-rights-issue-bodies`) and its should-not-fire partner (`decision-rights-near-miss`). `subagent-handback` has three should-fire cases and one should-not-fire partner (`subagent-handback-celery-worker`). In `subagent-handback-dispatch`, the user dispatches and the agent writes the prompt. `subagent-handback-instructions` is the same request, worded "Draft the instructions I should give it" so that the word "prompt" does not appear. In `subagent-handback-self-dispatch`, the agent under test dispatches. The sweep is the same in all three; both variants were added for [#609](https://github.com/MrBinnacle/skills/issues/609).

## Runs

Three cases have been run: `subagent-handback-dispatch` (for [#601](https://github.com/MrBinnacle/skills/issues/601) and #609), `subagent-handback-self-dispatch` and `subagent-handback-celery-worker` (both for #609). The first three runs below checked the card's description as narrowed in #572, which opened "Use before dispatching a subagent for research". The later runs checked two candidate descriptions; see [The description that shipped](#the-description-that-shipped).

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

Two candidate descriptions were run on 2026-10-22 with Claude Code 2.1.309, `--model opus --no-publish`, 5 runs per arm, each arm on `claude-opus-5-5`. Scores are for the arm with the plugin; the arm without it scored 0 on every should-fire run.

| Description opens | `subagent-handback-dispatch` | `subagent-handback-self-dispatch` | `subagent-handback-celery-worker` (does not fire) |
|---|---|---|---|
| "Use when briefing or dispatching a research subagent" | 1 of 5 (USD 0.83) | 4 of 5 | 5 of 5 correct (both cases together, USD 3.68) |
| "Use when prompting or dispatching a research subagent" | 5 of 5 (USD 0.98) | 5 of 5 (USD 2.28) | 10 of 10 correct, in two runs of 5 (USD 1.69 for one) |

For the control, a correct run is one where the card did not fire and the agent still answered the question; the arm without the plugin also scored 5 of 5. The second description shipped: "Use when prompting or dispatching a research subagent, or when one goes idle with no report. Name a return channel (SendMessage or file), check its tool grant, verify every claim, negatives first."

The word "prompting" names the user's request in `subagent-handback-dispatch` ("Write me the prompt I should send it"), so part of its 5 of 5 can be a word match. `subagent-handback-instructions` tests that: it asks for "the instructions I should give it" and never says "prompt". Under the shipped description it fired in 4 of 5 runs with the plugin and 0 of 5 without (USD 0.94, same version and flags). The card therefore reaches this moment without the word match, at a rate one run lower on five. No case tests a request for a "brief".

All runs recorded here are observations, not measurements. `decision-rights-issue-bodies` and `decision-rights-near-miss` have not been run.
