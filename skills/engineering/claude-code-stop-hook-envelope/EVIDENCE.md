# EVIDENCE — claude-code-stop-hook-envelope

Provenance record per the collection's evidence convention (see top-level README →
"Evidence records"). Fields are honest by construction: UNMEASURED means exactly that.

| Field | Value |
|---|---|
| **Origin** | OBSERVED 2026-06-03, a personal production project (structural-reset audit): two Stop-hook discipline predicates — a `[values decision]`-marker detector and a vocabulary-novelty corpus check — were wired in `.claude/settings.json` on 2026-05-26 and had **never fired once**. Both read stdin expecting the response text; a Stop hook receives a JSON envelope, so the greps matched nothing, exited 0, and read as healthy on every response. Caught only by the audit question "has this control *ever* fired?" — the failure produces no error, so nothing bounded how long it would have persisted. Full entry: [gotchas.md](gotchas.md) → `[OBSERVED]`. |
| **Validated against** | The origin incident's two hooks, repaired with this pattern and trial-fired against realistic envelopes; and an independent verified-correct public reference implementation (Trail of Bits' [`skill-improver` plugin stop hook](https://github.com/trailofbits/skills), which reads the envelope → `transcript_path` → last-assistant extraction). The negative-looking-positive harness in SKILL.md reproduces the dead hook and confirms the fix. |
| **Screen result** | UNMEASURED. Registered screen-task sketch: sandboxed project; stock agent asked to write a Stop hook that fires when the response contains a marker; deterministic oracle feeds a realistic envelope + transcript and checks for the fire. Caution from this collection's own screening history: the last four candidates screened all hit Null ceiling (see [RETIRED.md](../../../RETIRED.md)) — this class may too. |
| **Paired verdict** | UNMEASURED. Methodology for any future paired Full-vs-Null run: [skill-harness v0.2 pre-registration](https://github.com/MrBinnacle/skill-harness/blob/main/docs/findings/v0.2-preregistration.md). |
| **Standing cost** | Description ≈ 50 tokens if model-invocable. In the author's setup the description is stripped from the model's always-loaded context, and a small hook watches for the failure's signature (a Stop hook that never fires) and surfaces the skill only then — near-zero standing cost. Installing it normally works too; you just pay the description cost above. Body ≈ 8 KB + gotchas. |
| **Re-screen trigger** | Next major frontier-model release; or a Claude Code release that changes the Stop-hook stdin payload (e.g., delivering response text inline) — the latter retires the skill as platform-fixed, record intact. |

**Honesty note on duration:** an earlier private write-up of this incident described the hooks
as "dead for months." The dated records show wired 2026-05-26 → audit 2026-06-03, i.e. dead
for ~8 days. The corrected figure is used here; the load-bearing fact is unchanged — the
failure mode is silent, so only the audit bounded its duration, not the failure itself.
