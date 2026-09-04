# Format — Provider Envelope (returns that join across serial, nested and mixed dispatch)

The per-item block in [SKILL.md](SKILL.md) joins outputs from a flat panel of seats. When the
panel stops being flat — a stage feeds the next one, a seat recruits its own specialist, or the
providers are not all the same kind — the block no longer carries enough identity to reconstruct
which provider produced which finding under what access. This envelope wraps each return so it
does.

## The envelope

Each isolated return carries:

```yaml
run_id:
stage_id:
provider_id:
provider_type:     model | skill | mcp | agent | peer-session | human
role:
scope:
evidence_access:
write_authority:   none | bounded | parent-only
writes_performed:  false
status:            completed | abstained | unavailable | failed
findings:
assumptions:
conflicts:
recommended_verification:
latency:
cost:
```

`run_id` + `stage_id` + `provider_id` is the namespace that makes the finding identifier in
SKILL.md's fifth element globally unique without a consolidator renumbering step.

## Authority

**One named parent adjudicates and writes.** Providers return; the parent decides. Give every
provider the same frozen subject when comparability matters, and preserve raw returns before
normalizing them — the normalized copy is a reading, and the raw one is what a later reader
checks it against.

**Record every skipped, failed and unavailable provider.** A panel that reports four returns
when it dispatched six has published a smaller disagreement than it found. `abstained` is a
legitimate outcome when the subject falls outside a provider's declared scope, and it is
different from `failed`; keep the states distinct so the parent can tell a scope boundary from a
tooling fault.

**Detect invocation cycles and declare a maximum nesting depth before dispatch.** A provider that
can recruit a provider can recruit its own caller.

Agreement across providers is a fact about the panel, never a verdict about the subject.

## `writes_performed` is a claim, not a check

The field is the provider's assertion about itself. **Verify it by tool grant**: a provider
holding no write tools cannot write, and that is evidence. A provider stating it did not write is
not. Where the claim carries weight, dispatch into a seat whose grant makes the claim true by
construction.

## What a hook may decide

A hook may verify envelope **shape** and the presence of required receipts. Adjudicating a
finding is the parent's, and stays outside every deterministic check — a subjective finding that
a hook can block is a subjective finding a hook has decided.

## A provider that never returns produces no envelope

This format describes returns that arrive. It says nothing about the return that does not, which
is a different failure with a different control: a subagent answering in plain text emits nothing
the caller receives, and the only signal is an idle notification that reads like completion.
Name the return channel in the dispatch itself before relying on any envelope. Call the Skill
tool with `subagent-research-reliability`.
