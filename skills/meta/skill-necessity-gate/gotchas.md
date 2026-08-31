# gotchas — skill-necessity-gate

Append-only log. Never delete entries — gotchas are stress-test signal. `[ANTICIPATED]`
seeds are hypotheses; replace/supplement with observed session gotchas as they occur.

## [ANTICIPATED] Using the gate to rationalize a decision already made
The gate's default outcome is "not a skill." If you enter with the answer pre-decided and
just want a rubber stamp, you'll skim Gate 0/1/2. Symptom: every candidate "passes." Fix:
treat a run that keeps everything as evidence the gate isn't being applied honestly.

## [ANTICIPATED] Skipping the measurement, arguing the worth
Gates 1 and 2 say MEASURE (park-and-count frequency; with-skill-vs-without eval). The failure
mode is asserting
<!-- vale Taste.Evidence = NO -->
"this will obviously be used a lot" / "this obviously helps"
<!-- vale Taste.Evidence = YES -->
and skipping the
park-and-observe + eval. Prediction is not evidence; the whole point is that even Pocock
mis-predicts ("too simple" prompts that became core skills).

## [ANTICIPATED] Auto-deciding invocation topology instead of asking
Gate 3 (auto-invoke vs manual) is partly a user-values call. Don't silently set
`disable-model-invocation` because "Pocock prefers procedures" — surface the budget math AND
the control tradeoff and let the human choose. Certain skills (e.g. situational diagnosis) are
MORE valuable auto-invoked.

## [ANTICIPATED] Confusing "narrow" with "not worth it"
Hyper-narrow gotcha/trap skills are individually fine (precise descriptions, low misfire). The
real cost is AGGREGATE standing tokens across many of them. The fix is usually
`disable-model-invocation` (pull when you hit the exact bug), not deletion. Don't reject a
narrow skill on narrowness alone — reject on frequency × standing cost.

## [ANTICIPATED] Treating the 300–500 instruction number as fact
Pocock's memorable "300–500 instructions" is NOT Anthropic-backed and mis-states the shape.
If you cite it as a hard threshold you've skipped triangulation. Say "continuous,
model-dependent degradation" and cite IFScale.

## [ANTICIPATED] The gate becoming the deliverable
Running the gate and producing verdicts can feel like progress. The deliverable is a correct
routing decision (often "don't build it") and, for absence mode, a *promoted skill that passed
the worth eval* — not a pile of analysis.

## [ANTICIPATED] Locking a loop-consumed skill to human-only (making it inert)
Gate 3's default lean toward "procedures should be `disable-model-invocation`" is DANGEROUS for
any skill that must fire inside an autonomous loop. In Claude Code, a `disable-model-invocation`
skill passed to `/loop` does not execute — it arrives as plain text. So the control move that
keeps a human in charge (GD-6) makes the procedure useless in autonomy (GD-10). Always ask "will
this run in a loop?" before recommending `disable-model-invocation`.

## [ANTICIPATED] Trusting a naive success signal in an autonomous skill
For loop/AFK skills, "tests pass" is a reward-hacking magnet — agents fake it (sys.exit(0),
modifying/deleting tests). If Gate 2 accepts a subjective or single-check success signal for an
autonomous skill, it will pass skills that green themselves. Require compound, machine-verifiable,
held-out criteria. Known gap: no tool reliably stops test DELETION — keep that human-gated.

## [OBSERVED 2026-07-04] The gate correctly REJECTED a candidate of its own genre
A Windows-traps skill for a browser-automation tool was drafted (3 real, debugged gotchas)
and run through the gate. Verdict: NOT a standalone skill — Gate 1 (recurrence near-zero:
setup is one-time + the affected code path had been abandoned), Gate 2 (benefit ≤ cost right
after a description-budget reclaim), Gate 0 (tool-coupled reference → co-locate with the
tool). Disposition: appended to the tool's own skill as a troubleshooting reference (loaded
only when that skill is active = zero standing cost). Evidence the gate is not a rubber
stamp — it refused a plausible, genre-typical candidate. The trap-skill instinct ("I
debugged something non-obvious → make a skill") frequently fails Gate 1/2; the right home is
usually WITH the tool or in memory.

## [OBSERVED 2026-07-04] Mined candidate routed to MERGE, not authorship
Candidate: an adversarial-verification dispatch template, surfaced by transcript mining with
recurrence apparently pre-measured. Verdict: not a standalone skill; merged into an existing
sibling review skill as a template file (the sibling's trigger section had explicitly carved
out that upstream gap). Two sharpenings for future runs:
1. Miner-sourced candidates arrive with Gate 1 seemingly pre-passed — adjudication weight
   shifts to Gates 0/2/3.
2. Gate 0's "trivially discoverable" clause generalizes to "already SUPPLIED BY THE HARNESS
   at point of use": if the runtime's own tool guidance pushes the pattern into context,
   re-encoding it as a skill pays budget for redundancy and rots against harness updates.
   Check what the harness already injects before authoring.

## [OBSERVED 2026-07-04] Correction to the above — count OCCASIONS, not transcripts
A second mined candidate arrived as "10× recurrence." Ground truth: all matching transcripts
were parallel batch seats of ONE orchestrated workflow fire — true recurrence n=1. VERDICT:
fails Gate 1 → park & observe. The earlier candidate's "22 occurrences" was the same fan-out
inflation (2 true occasions; its MERGE disposition stands on zero-standing-cost grounds, not
recurrence volume). RULE: Gate 1 recurrence mined from agent transcripts must be deduped by
run/occasion; one fire spawning N parallel seats is n=1, not n=N. Layer note (Gate 0): a
recurring fan-out orchestration crystallizes as a NAMED WORKFLOW script, not a SKILL.md —
workflows are a distinct layer alongside CLAUDE.md/memory/MCP/hooks.
