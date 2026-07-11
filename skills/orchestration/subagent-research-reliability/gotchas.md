# gotchas — subagent-research-reliability

## [ANTICIPATED]

- **The verification subagent can itself fabricate verdicts.** It's an LLM too. Keep its job
  mechanical (fetch URL, compare content, emit enum verdict) and spot-check any `UNRESOLVED`
  that would kill a load-bearing finding — a transient 404 or a bot-blocked domain reads the
  same as a fabricated source.
- **`tools: *` doesn't guarantee searching happens.** A general-purpose agent with full tools
  can still answer from training data if the prompt doesn't demand live retrieval. Require
  "every claim carries a fetched URL" in the dispatch prompt, not just the right tool grant.
- **Agent definition and skill documentation drift apart.** A project's research SKILL.md may
  describe capabilities the agent's `tools:` frontmatter no longer grants (or never did). The
  frontmatter is ground truth; re-check it when either file changes.
- **Rate-limited fetches masquerade as dead links.** A verification pass run during heavy
  parallel agent activity can see 429s/timeouts and report `UNRESOLVED` for live sources.
  Re-verify failures once, serially, before dropping a finding.

## [OBSERVED]

*(Append observed gotchas here as they surface. Do not delete entries — gotchas are
stress-test signal.)*

- **2026-05-28 / a personal production project (threat-watch beat):** a `research-scout` agent
  whose description claimed "performs web research ... with citations" had
  `tools: Read, Bash, Grep` — no web tools at all. Dispatching it would have produced a no-op or
  fabricated beat. Caught pre-dispatch by reading the agent frontmatter; logged as a work item.
- **2026-05-28 / same session:** the post-return verification pass caught a fabricated
  cross-reference — real Cursor CVEs (CVE-2025-54136/54135) attributed to an arXiv paper that
  does not cite them. The CVEs were real, the linkage was invented. Direct trigger for Check 2's
  "verify the cross-reference, not just the ID" wording.
