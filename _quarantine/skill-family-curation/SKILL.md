---
name: skill-family-curation
description: |
  Discipline for managing the long-term entropy of a growing skill library
  (~/.claude/skills/ + ~/.claude/skills/_quarantine/). Detects candidate
  "families" of overlapping skills surfaced via three touchpoints
  (extraction-time, promotion-time, search-time), runs a mechanical
  falsifiability gate (literal fixtures + pseudocode tests, NOT English
  assertions), surfaces dispositions to the human in a strict 3-line
  format, and on CONSOLIDATED dispositions performs Graduation cleanup
  (physical deletion of child SKILL.md files + grep verification). Defends
  against (a) skill-bloat from unchecked extraction, (b) doc-rot from stale
  child skills left after consolidation, (c) Theater (LLM-generated
  plausible but unfalsifiable family hypotheses), (d) global instruction-
  budget pollution. Use when: (1) a /claudeception extraction round produced
  ≥1 new skill and you want to check for family-candidate hints,
  (2) a manual §1.5 quarantine-promotion review is in progress, (3) a Skill
  tool search returned ≥K overlapping results for one query, (4) you notice
  multiple skills "sound similar" and want to test whether they should
  consolidate or stay distinct with see-also links. NEVER consolidate
  silently; the LLM proposes + provides mechanical evidence; the human
  dispositions.
disable-model-invocation: true
metadata:
  type: discipline
---

<!-- S305 gate run (private research repo, quarantine gate-0 audit): added
     disable-model-invocation per the topology rule in AGENTS.md. This card prescribes physical
     deletion of SKILL.md files and atomic commits, which makes it a PROCEDURE with side
     effects, not a model-pulled ability. It was authored without the flag. Cleared Gate 0;
     standing is CANT_TELL_YET pending a screen. Not promoted. -->


# Skill Family Curation

## Problem

A skill library grows over time. Each /claudeception extraction adds one or more skills to `_quarantine/`. Manual §1.5 reviews promote some to active. Without curation, three failure modes compound:

1. **Skill bloat**: many skills with overlapping triggers. Semantic search returns 4-5 candidates for one query; the agent doesn't know which to invoke; the user mental-model breaks.
2. **Doc rot**: a CONSOLIDATED-into-parent skill leaves stale child skills sitting in the directory. The agent's context window gets polluted; the agent gets confused over which one to apply.
3. **Theater**: the LLM, asked "is this a family?", will generate plausible English justifications regardless of whether the consolidation is actually warranted. LLMs are optimized to reward plausible-sounding answers; the easy path is to confidently assert a family exists and propose a manufactured parent.

The naive response — "have the LLM periodically scan skills and propose consolidations" — fails on all three. It accelerates bloat (more skills, more consolidations, more meta-skills), invites doc rot (consolidations without cleanup), and produces Theater by design.

This skill is the curation discipline that defends against all three.

## Trigger conditions

Apply at exactly these touchpoints (do NOT run continuously or on a schedule):

1. **Extraction-time** — at the END of a /claudeception extraction round, AFTER all new skills have been written to `_quarantine/`. The check is lightweight: grep existing skill names + descriptions for keyword/trigger overlap with each newly-extracted skill. If ≥3 existing skills match above threshold for a new one, APPEND a hint to your family-candidate registry (an append-only file you keep in your own skill library; this collection ships no registry, because the contents are specific to one library's skills). DO NOT propose consolidation immediately. The hint sits in the registry until the next promotion-time review.
2. **Promotion-time** — during a manual §1.5 quarantine-to-active promotion review, scan the registry for any DISPOSITION-PENDING entries. For each, run the falsifiability gate (below) and surface the result to the human in the structured disposition format.
3. **Search-time** — when a Skill tool search returns ≥4 overlapping results for one user query and the user is visibly choosing among them, surface "these N skills overlap on trigger X; want to disposition them as a family?" Do NOT block the user's current task; just offer.

Do NOT run this skill outside these three touchpoints. There is no cron trigger, no autonomous scan, no "let me check the library" behavior.

## Solution

### Step 1 — Hint generation (extraction-time)

After /claudeception writes a new skill `S_new` to `_quarantine/`:

```
overlap_candidates = []
for S_existing in (~/.claude/skills/**/SKILL.md + ~/.claude/skills/_quarantine/**/SKILL.md):
    overlap_score = compute_overlap(S_new.description, S_existing.description)
    if overlap_score > THRESHOLD (initial: keyword bag-of-words Jaccard >= 0.3):
        overlap_candidates.append((S_existing, overlap_score))

if len(overlap_candidates) >= 3:
    family_id = next_family_id()
    append_to_registry(family_id, S_new, overlap_candidates, "PROPOSED")
```

The registry append is purely a HINT for the next promotion review. No human surfacing, no skill proposal yet. The threshold is intentionally generous at extraction time — Theater is prevented by the downstream falsifiability gate, not by being stingy here.

### Step 2 — Falsifiability gate (promotion-time, mandatory before any consolidation)

For each PROPOSED registry entry, the LLM MUST produce all three of the following. English assertions alone fail the gate; mechanical fixtures + pseudocode required.

#### Test A — Distinct-trigger test (mechanical tracer-bullet)

Produce TWO literal text fixtures (short scenarios, 1-3 sentences each) AND pseudocode evaluation:

```
Fixture-A: "<concrete scenario where the candidate parent should fire>"
Fixture-B: "<concrete scenario where a specific child should fire but parent should NOT>"

Pseudocode evaluation:
  trigger_match(parent, Fixture-A) → expect: FIRES
  for each child: trigger_match(child, Fixture-A) → expect: SILENT (parent has unique coverage)
  
  trigger_match(parent, Fixture-B) → expect: SILENT (child has unique coverage parent doesn't subsume)
  trigger_match(target_child, Fixture-B) → expect: FIRES
```

The pseudocode evaluation is a thought-experiment match (not a literal regex/AST test) — the LLM walks each skill's `description` and `trigger conditions` and judges whether the fixture would fire it. Result must be RED-GREEN observable: parent fires fixture-A and stays silent on fixture-B; children stay silent on fixture-A and at least one fires fixture-B. If ANY of these conditions inverts, the family is mis-specified.

If the LLM cannot construct fixtures A and B without strain, the family is REJECT-AS-MANUFACTURED. The strain itself is the test failing.

#### Test B — Distinct-response test

For each child, produce a 1-line statement of the concrete response action the child produces (e.g., "rewrite the model id to `anthropic/<original>`"). Produce a 1-line statement of the parent's proposed response action.

If the parent's response is generic enough to be a superset of all children's responses (e.g., "verify before trusting"), the parent is vacuous — REJECT-AS-MANUFACTURED.

If the parent's response is a specific action and each child's response is ALSO a specific action distinct from the parent's, the family is real — children should KEEP-DISTINCT-WITH-SEE-ALSO links to the parent (the parent is a NEW skill that ADDS to the library, not one that REPLACES children).

If the parent's response is a specific action and the children's responses collapse INTO the parent's action (children were just different framings of the same response), CONSOLIDATE — children get deleted, parent absorbs the trigger coverage.

#### Test C — Evidence-anchored test

Name THREE concrete past sessions (with dates + identifiable references — commit SHAs, session-log filenames, council-fire archive paths) where the proposed family would have helped EARLIER or WIDER than the children alone. If three cannot be named, the family is hypothesis-only — DISPOSITION-PENDING until evidence accumulates.

Hallucinated sessions or "I can imagine a scenario where..." fail the test. The sessions must be verifiable from git/docs/transcripts.

### Step 3 — Structured disposition surfacing (promotion-time + search-time)

When surfacing a family disposition to the human, the LLM uses EXACTLY this 3-line format (each line ≤ 200 chars; hard cap):

```
Evidence: <overlap data summary + Test A/B/C results in 1-2 phrases>
Cost-of-action: <estimated token savings if CONSOLIDATED, OR estimated cognitive overhead if NOT-CONSOLIDATED, in concrete terms>
Disposition: <MERGE | KEEP-DISTINCT-WITH-SEE-ALSO | REJECT-AS-MANUFACTURED | DISPOSITION-PENDING (evidence-incomplete)>
```

NO prose justification beyond these three lines. Verbosity is the failure mode. The human dispositions based on these three lines; if more context is needed, the human asks.

### Step 4 — Graduation (only on MERGE / CONSOLIDATED disposition)

This step is mechanical. Each sub-step is falsifiable.

1. **Write the parent skill** to `_quarantine/<parent-name>/SKILL.md`. Parent must have its OWN description (not concatenated from children) + trigger conditions + solution structure. The parent skill must pass the existing `using-superpowers` quality bar (see CLAUDE.md `~/.claude/CLAUDE.md` §1.5 skill authoring conventions).
2. **Physically delete each child** `SKILL.md` and its parent directory if it becomes empty. Use explicit file-deletion operations; never leave a child file with a "deprecated, see parent" stub that's just stale-content-in-disguise.
3. **Grep verification**: search the entire skills tree (both active and quarantine) for any reference to the deleted child names (file paths, internal links, see-also references). For each match found, either (a) update to point at the new parent, or (b) delete if the reference was itself stale. Verify the post-cleanup grep returns empty.
4. **Single cohesive commit** containing: the new parent SKILL.md, the child deletions, the registry entry update (status → CONSOLIDATED-INTO-PARENT with disposition date + reason), and any see-also link updates. Commit message body lists every child deleted by full path. The atomicity is required: a half-applied consolidation that drops a child but doesn't write the parent is a worse state than either-and-or.
5. **Update the registry entry** status from DISPOSITION-PENDING to CONSOLIDATED-INTO-PARENT in the same commit. Add a `[UPDATE: yyyy-mm-dd]` line under the entry; never edit the original PROPOSED line.

For KEPT-DISTINCT-WITH-SEE-ALSO disposition, the Graduation steps are different: no child deletion, no parent skill creation, just add bidirectional `## See also` links between the family members. The disposition itself is recorded; the children stay as-is.

For REJECT-AS-MANUFACTURED, no cleanup needed; just record the disposition with the test result that failed.

## Verification

You applied this skill correctly when:

- Your family-candidate registry is append-only (no edits to prior entries; only `[UPDATE: yyyy-mm-dd]` appends).
- Every CONSOLIDATED disposition results in physical child-file deletion + grep-clean verification.
- Every disposition surfaced to the human uses the 3-line structured format with no prose padding.
- The falsifiability gate's tracer fixtures + pseudocode evaluation are present in the registry entry for every consolidated family. Future-you can audit them.
- This skill is invoked at the three named touchpoints only; not on a cron, not autonomously.

You misapplied this skill when:

- A child SKILL.md is still in the directory after its family CONSOLIDATED.
- The disposition surfacing was prose-heavy ("I think this might be a family because..."). The format is non-negotiable.
<!-- vale Taste.Evidence = NO -->
- The falsifiability gate was satisfied with English assertions only ("the trigger is clearly distinct because..."). Without fixtures + pseudocode, the gate didn't fire.
<!-- vale Taste.Evidence = YES -->
- The skill is loaded by `CLAUDE.md` or a settings.json hook for every session. It must remain just-in-time only.

## Instruction-budget discipline

This skill MUST NOT be referenced from CLAUDE.md or settings.json hooks. It loads only when:

- /claudeception invokes it at extraction-time (claudeception's own body may reference this skill as a final step)
- The human explicitly invokes it during a quarantine review
- The human's search behavior triggers the search-time touchpoint

Migrating this skill's trigger into a globally-loaded file taxes the LLM's instruction budget on every session, even when no skill writing or curation is happening. The empirically-observed LLM instruction budget is ~300-400 instructions before attention diffuses; this skill is meaningful enough to NOT be background noise on unrelated sessions.

## Example — FAMILY-001 worked example

From the 2026-06-09 session-end claudeception round:

The orchestrator extracted 6 skills across the day and observed in the closing summary: "4 of 6 skills relate to the discipline of 'look before you trust the spec/handoff/recipe/SDK assumption.'" The candidates: `halt-as-deliverable`, `two-phase-doc-honesty-then-engineering`, `walk-the-recipe-as-target-user`, `click-clirunner-env-none-deletes`.

Running this skill's falsifiability gate:

- **Test A (tracer-bullet)**: Fixture-A "I'm validating my own SOP doc before dispatching new work" — would `look-before-you-trust` (parent) fire? Plausibly. Would `halt-as-deliverable` fire? No (it fires AFTER a discipline catches an inconsistency, not BEFORE validation). Would `walk-the-recipe-as-target-user` fire? Yes (it fires on validating workflows). Parent and child both fire on the same fixture → parent does NOT have unique coverage that justifies its existence above the child. Fixture-B "I'm validating a workflow as a non-privileged user" — `walk-the-recipe-as-target-user` fires specifically; the parent would not specifically add value. **Test A: FAIL** (parent doesn't have unique trigger coverage that justifies separation).
- **Test B (distinct-response)**: Parent's proposed response: "verify before trusting." Children's responses: halt-as-deliverable → "reframe the catch as the deliverable" (specific narrative action); two-phase-doc-honesty → "Phase A inline + Phase B dispatched" (specific orchestration shape); walk-the-recipe → "simulate target user environment + walk steps" (specific validation action); clirunner-env-none-deletes → "pass `{key: None}` to delete" (specific test code). Parent's response is generic enough to be vacuous — REJECT-AS-MANUFACTURED.
- **Test C (evidence-anchored)**: only one session (today, 2026-06-09) where the pattern was retrospectively visible. Cannot name three. **Test C: FAIL** (evidence-incomplete).

**Disposition**: `REJECT-AS-MANUFACTURED`. Reason: Test A fails (no unique trigger coverage) AND Test B fails (vacuous response action) AND Test C fails (single-session evidence is hypothesis, not pattern).

Registry entry FAMILY-001 records this rejection. Future skill writers can read it and not re-litigate the same hypothesis until new evidence accumulates.

## Notes

- This skill is itself a candidate for its own gate. If a future curation skill is proposed as a parent of this skill + claudeception, the falsifiability gate applies recursively. Be honest.
- The skill library WILL grow without bound if curation never happens; this skill is the brake. But the brake itself can become bloat if invoked on a cron or applied recursively (a meta-meta-skill that curates curation-skills). The just-in-time touchpoints + the falsifiability gate are the structural prevention.
- The "evidence-anchored test" requirement of three concrete past sessions makes the discipline self-limiting: early in a project's life, no family can pass the test because there's not enough session history. This is correct — early curation is premature optimization.
- The structured 3-line disposition format is non-negotiable because LLMs default to verbose plausible-sounding justifications. The format constrains output before the LLM can generate Theater.
- Graduation must be atomic (single commit, parent + child-deletions + registry-update + see-also fixes all in one). A half-applied consolidation is worse than no consolidation.

## See also

- `[[halt-as-deliverable]]` — companion: when a curation gate REJECTS a family the orchestrator earlier proposed, that rejection IS the deliverable for the curation step. Surface it.
- `[[walk-the-recipe-as-target-user]]` — companion: when verifying that this skill's flow actually works for a future reviewer, simulate the reviewer's perspective.
- `[[two-phase-doc-honesty-then-engineering]]` — companion: when a curation pass discovers that prior consolidations have rotted (child stubs left behind), the response is doc-honesty pass + engineering cleanup.
- `[[claudeception]]` (global skill at `~/.claude/skills/claudeception/SKILL.md`) — the upstream skill whose extraction step generates the registry hints.
- `[[lossless-orchestrator-infrastructure]]` (referenced in MEMORY.md feedback) — the architectural principle that each piece has one job; this skill is the curation piece, distinct from extraction (claudeception) or promotion (manual §1.5).
