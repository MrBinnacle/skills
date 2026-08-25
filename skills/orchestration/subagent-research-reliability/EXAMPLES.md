# Examples — subagent-research-reliability

## Threat-watch verification pass

3 `general-purpose` subagents (NOT the web-toolless `research-scout` agent) ran clusters in
parallel → 9 findings. A 4th general-purpose subagent WebFetched all 9 source URLs → 7 VERIFIED,
2 PARTIAL, and flagged one fabricated CVE-to-paper linkage. Only verified findings were recorded as
actionable; the fabrication was corrected in the log.

## Dead letter, 2026-08-18

Three `Explore` scouts were dispatched over one repository with no return channel named. All three
researched correctly. Four idle notifications arrived carrying no content; a state file was
committed saying the scouts "have not reported" and telling the next session to re-dispatch.
Re-instructing them with `SendMessage` plus one authorised scratchpad path recovered every finding
— including one that **contradicted an accepted ADR in an already-approved plan**. The research
was never the problem. The channel was, and it cost a wrong commit.

## Dead letter, 2026-08-24

Four `reader` subagents were dispatched to extract origin text from 25 skill cards. The dispatch
named no return channel. All four idled without delivering. `SendMessage` alone (three rounds)
produced nine idle notifications and zero recoveries. Naming one absolute file path per agent via
the bounded write escalation recovered 3 of 3 given a path; the fourth, never given a channel,
never delivered. One of those three had the file write blocked by the host's tooling guard and
still delivered — full content fell back through `SendMessage`. Check 0's redundancy framing held:
the routes fail for unrelated causes, and naming a payload channel at all is what separates
delivery from silence.

## Notes

- Claude Code discipline (custom agents, `subagent_type`, WebSearch/WebFetch tools, agent
  frontmatter).
- A verification subagent is cheap relative to the cost of acting on a hallucinated citation
  (e.g., filing a security finding against a fake CVE, or bumping a dependency for a CVE that
  doesn't exist).
- Background dispatch pairs well with this (curate on return rather than blocking) — provided
  Check 0 gave the return a channel. Echo the verdict inline; a background temp file is the
  redundant route, never the only one.
- **A verified return is worth more than an unverified one, not less.** Check 2 caught three false
  claims in one repo-only return whose substantive disposition was correct. Verification is what
  makes a scout's work usable; treating it as distrust is how the step gets skipped.
- A project's research-agent SKILL may define the finding schema, but the AGENT definition is
  where the tool-capability trap lives — they can drift apart. See also
  `superpowers:subagent-driven-development` (spec/review loops) for the broader dispatch
  discipline family.
