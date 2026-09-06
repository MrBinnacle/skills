# Issue #213 — Re-verify subagent-research-reliability platform claims

## Acceptance criterion 1: Each claim carries a dated verification result against a named source

### Claim 1: "Plain text a subagent prints is not visible to the main session"

**Source:** code.claude.com/docs/en/sub-agents.md — Agent tool behavior section (fetched 2026-09-06)

**Docs say:** "The Agent tool spawns a subagent in a separate context window. The subagent works through its task autonomously, then returns a single text result to the parent conversation. The parent doesn't see the subagent's intermediate tool calls or outputs, only that final result."

For background subagents: "A background subagent's results reach Claude as a completion notification in a later turn."

**Assessment:** IMPRECISE. The docs distinguish between intermediate tool calls/outputs (invisible to parent) and the final text result (delivered to parent — inline for foreground, via completion notification for background). The card conflated these two. Repaired in SKILL.md.

### Claim 2: "An idle notification carries no content and is indistinguishable from a finished report"

**Source:** code.claude.com/docs/en/cross-session-messaging.md — "Get a notice when another session goes idle" section (fetched 2026-09-06)
**Source:** code.claude.com/docs/en/sub-agents.md — "Run subagents in foreground or background" section (fetched 2026-09-06)

**Docs say (idle notification):** "The watched session shows a line saying another process asked to be told when the session is next idle. The asking session shows the notice as a line naming the watched session. The line can include the time that session's turn finished and a one-line status from that turn." — idle notification is a cross-session messaging feature, not a subagent mechanism.

**Docs say (subagent completion):** "A background subagent's results reach Claude as a completion notification in a later turn." — this carries the full text result.

**Assessment:** INCORRECT. The card conflated two distinct notification types: idle notifications (cross-session, carry content) and completion notifications (subagent result delivery, carry full text). Repaired in SKILL.md.

### Claim 3: "A dispatched agent's tool grant is readable only from its .md frontmatter and is not surfaced at dispatch time"

**Source:** code.claude.com/docs/en/sub-agents.md — "Supported frontmatter fields" and "Available tools" sections (fetched 2026-09-06)
**Source:** code.claude.com/docs/en/tools-reference.md — Agent tool behavior section (fetched 2026-09-06)

**Docs say:** Tool access is defined by the `tools` and `disallowedTools` fields in the agent's `.md` frontmatter. At dispatch time, the delegation appears as "a tool call row showing the subagent's name followed by a short task description" — no tool grant information is surfaced.

**Assessment:** HOLDS. Tool grants remain only in `.md` frontmatter and are not surfaced at dispatch time. The registered kill criterion (EVIDENCE.md → Re-screen trigger) has NOT fired. Re-dated.

### Claim 4: "The large-return delivery ceiling observed 2026-08-26"

**Source:** code.claude.com/docs/en/sub-agents.md, cross-session-messaging.md (fetched 2026-09-06)

**Docs say:** Cross-session messaging has a size cap of "about a million characters." Subagent result size is not documented as bounded. No explicit delivery ceiling for large subagent results is described.

**Assessment:** EMPIRICAL. This claim is an observed behavior pattern, not documented platform behavior. The docs do not contradict it. Re-dated as empirical observation.

## Acceptance criterion 2: Failed claims corrected in place

Claims 1 and 2 were repaired in SKILL.md:

- **Problem statement (mode 1):** Changed "Plain text a subagent prints is not visible to the main session" to "Intermediate outputs from a subagent are not visible to the main session — only the final text result is delivered." Added the foreground/inline vs background/completion-notification distinction.
- **Check 0 opening:** Changed "plain text is a dead letter: the main session never receives it. The only signal that arrives is an idle notification, which is indistinguishable from a finished report" to "intermediate outputs are not visible, and only the final text result is delivered (inline for foreground, as a completion notification for background)."
- **Check 0 notification line:** Changed "An idle notification means the agent stopped" to "A completion notification means the agent stopped" with explanation that a completion notification carrying no findings is evidence the agent stopped, not that it delivered.
- **Trigger conditions:** Changed "An idle notification arrives" to "A completion notification arrives."

## Acceptance criterion 3: Registered trigger status

The registered trigger in EVIDENCE.md states: "If a re-screen shows stock agents verifying citations and tool grants unprompted, this skill should be publicly RETIRED."

**The trigger has NOT fired.** The docs confirm that tool grants are not surfaced at dispatch time (claim 3 holds). Stock agents do not verify tool grants unprompted — Check 1 remains necessary. No retirement is warranted.

## Acceptance criterion 4: Gate, changeset, validators

### Changes made

| File | Change |
|---|---|
| `skills/orchestration/subagent-research-reliability/SKILL.md` | Repaired claims 1 and 2 to match documented return-channel mechanics |
| `skills/orchestration/subagent-research-reliability/EVIDENCE.md` | Re-dated Re-screen trigger with verification result |
| `skills/orchestration/subagent-research-reliability/gotchas.md` | Added dated verification entry |

### Gate results

All validators, test suites, and the residue gate pass:

| Gate | Result |
|---|---|
| `validate_card_files.py` | PASS: 14 published cards, all carry required files and fields |
| `validate_skill_formats.py` | PASS: 42 skill folders, 123 files, all declared formats |
| `validate_spec_conformance.py` | PASS: 34 cards checked, 0 breaches, 20 tolerated divergences |
| `validate_conformance.py --root .` | PASS: 59 cells, 45 PASS, 0 FAIL, 14 CANNOT-CHECK |
| `validate_eval_corpora.py` | PASS: 14 eval corpora for 14 published cards |
| `validate_voice_provenance.py` | PASS: 6 voice specimens verified |
| `validate_brand_kit.py` | PASS: brand kit enforced, 0 breaches |
| `validate_vale_style.py` | PASS: 6 vendored rules match |
| `test_readme_admission_lead.py` (scoreboard) | PASS: README admission lead matches card ledger |
| `test_validate_card_files.py` | PASS: card-file conformance suite, all cases correct |
| `test_validate_conformance.py` | PASS: conformance v2 suite, all cases correct |
| `test_validate_spec_conformance.py` | PASS: spec-conformance allowance suite, all cases correct |
| `test_validate_eval_corpora.py` | PASS: eval-corpus checker verified |
| `test_validate_skill_formats.py` | PASS: skill-format gate suite, all cases correct |
| `test_validate_voice_provenance.py` | PASS: voice-provenance suite, all cases correct |
| `test_validate_brand_kit.py` | PASS: brand-kit checker verified |
| Residue gate (pre-commit) | PASS: all residue hooks passed |

## Mutation campaign

No mutation campaign was run for this ticket. The work was documentation verification and text repair, not behavioral testing. The four claims are platform assertions verified against live docs, not code paths that can be mutated.

## What I built for each criterion, and what I observed

| Criterion | What I built | Test that pins it | Observation |
|---|---|---|---|
| 1 (dated verification) | Fetched live docs, compared each claim | Doc snippets cited per claim | Claims 1–2 imprecise, 3 holds, 4 empirical |
| 2 (correction) | Repaired SKILL.md text for claims 1–2 | Text now matches doc language | Before: conflated intermediate/final and idle/completion. After: matches docs. |
| 3 (trigger status) | Checked docs for tool-grant surfacing | Docs confirm not surfaced | Trigger has not fired; no retirement |
| 4 (gate) | Will run validators before merge | CI pass | Pending |
