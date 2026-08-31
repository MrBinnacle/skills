# Meta — skills about the skill system itself

Disciplines for deciding what belongs in an agent's skill library at all, and for keeping
that library honest about its own cost.

### Skills

- **router-skill-predicate-gap**
  A router rule can be live, healthy, and still match nothing anyone types — because the
  pattern list omits the ordinary word for the thing, or because a JSON string escape left the
  pattern inert and `re.compile` accepted it anyway. Test the negative first against the live
  hook, with a positive control in the same run, before writing that a discipline is
  hook-enforced. See [router-skill-predicate-gap/SKILL.md](router-skill-predicate-gap/SKILL.md).
