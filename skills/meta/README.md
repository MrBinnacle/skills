# Meta — skills about the skill system itself

Disciplines for deciding what belongs in an agent's skill library at all, and for keeping
that library honest about its own cost.

### Skills

- **skill-necessity-gate**
  Six-gate procedure deciding whether a proposed capability should become a skill —
  layer triage, recurrence, measured worth, invocation topology, statefulness, low-cost
  shape — plus a refusal predicate, library-audit and absence-detection modes, and the
  reflexive rule that measurement instruments run the same gates. Default outcome is
  "not a skill," on purpose. See [skill-necessity-gate/SKILL.md](skill-necessity-gate/SKILL.md).

- **router-skill-predicate-gap**
  A router rule can be live, healthy, and still match nothing anyone types — because the
  pattern list omits the ordinary word for the thing, or because a JSON string escape left the
  pattern inert and `re.compile` accepted it anyway. Test the negative first against the live
  hook, with a positive control in the same run, before writing that a discipline is
  hook-enforced. See [router-skill-predicate-gap/SKILL.md](router-skill-predicate-gap/SKILL.md).
