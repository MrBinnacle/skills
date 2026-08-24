---
"mrbinnacle-skills": patch
---

Record a second, independent occurrence of the return-channel failure, and answer admission criterion 2 for the `subagent-research-reliability` patch staged in `_quarantine/`.

The rotation pass exists to collect evidence that accrues faster than anyone records it. This pass produced one countable occasion, and it happened inside the pass itself.

**What happened.** On 2026-08-24 the pass dispatched four `reader` subagents to extract origin text from 25 skill cards. The dispatch named no return channel; each prompt ended `Your final message IS the data`. A subagent's plain text is a dead letter — the main session never receives it. Four idle notifications arrived carrying no content, and no extract reached the session. The extraction was abandoned and redone by a mechanical script over the same 25 cards.

**Why it counts.** The staged patch documents its origin as `workspace_lint` S026, 2026-08-18/19: three `Explore` scouts dispatched with no return channel named, four idle notifications carrying no content. The 2026-08-24 occurrence is a different repository, a different agent type, and a different task, six days later. The four agents in one dispatch are one occasion, not four — `ADMISSION.md` criterion 2 refuses fan-out from a single run.

**The discipline that would have caught it was staged, not live.** `grep -c "dead letter"` returns `0` against the promoted card and `3` against the candidate's `SKILL.md`. `Check 0` is the patch. The promoted skill was installed and active throughout and carries no such check, so the failure recurred in exactly the gap the patch closes.

**One narrowing the new occurrence adds, which the origin could not.** `Check 0` offers two return routes so that one failing is survivable. Occurrence 1 recovered with `SendMessage` **plus** one authorised absolute path. Occurrence 2 used `SendMessage` alone — all four agents were re-instructed with the output contract restated verbatim, each woke, and each emitted a second idle notification carrying no content. Nothing was recovered. On this evidence the file at a named path is the load-bearing route and `SendMessage` is not a substitute for it. Route 2 was not exercised alone, so its standalone sufficiency remains untested and is not claimed.

**What this does and does not license.** Criterion 2 is answered for the `Check 0` branch, and criterion 2 was the standing blocker on every candidate in `_quarantine/`. It is the only criterion this pass measured. Criteria 1, 3 and 4 are untouched. The candidate still carries no `EVIDENCE.md` and has not been through the frontmatter normalization in `AGENTS.md` step 2a, so this records evidence rather than proposing a promotion.

No published card changed. No count on any published card moved. The published tree is unmodified by this pull request.
