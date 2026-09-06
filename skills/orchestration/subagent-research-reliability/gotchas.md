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
- **2026-08-04 / a personal research project — relocated here from that project's checkpoint.**
  Background research subagents **go idle WITHOUT delivering their final summary** (the idle
  notification carries nothing), and `SendMessage` sometimes gets no reply → **read their FILES
  rather than waiting for a handback.** Second half, and it is the pre-dispatch one: dispatch every
  web-research scout with an explicit `ToolSearch select:WebSearch,WebFetch` first step plus a
  STOP-if-unavailable clause — **web tools are DEFERRED in this harness, so they are absent from
  the agent's schema until fetched, and a scout without them answers from memory** while looking
  exactly like a scout that searched. This sharpens the skill's pre-dispatch check: a `tools:`
  grant naming web tools is necessary but NOT sufficient when the harness defers tool schemas.
- **2026-08-04 / a personal research project.** A background agent's file is **not final when you
  first read it** — a verifier idled at 253 lines and later reached 494. An md5 that matches current disk
  proves nothing if you only READ half of it. Re-check length before relying on any summary of a
  subagent's file. (Also recorded in `cite-verified-research-sweep/gotchas.md`; kept here too
  because it fires on ANY background-subagent read, not only during a research sweep.)
- **2026-08-24 / rotation and harvest pass, a different repository:** four `reader` subagents were
  dispatched to extract origin text from 25 skill cards. The dispatch named no return channel;
  each prompt ended "Your final message IS the data." All four idled without delivering content.
  Re-instructing with `SendMessage` alone (output contract restated, three rounds) produced nine
  idle notifications and zero recoveries. Naming one absolute file path per agent via the bounded
  write escalation then recovered 3 of 3 agents given a path; the fourth, never given a channel,
  never delivered. One of the three had its file write blocked by the host's own tooling guard and
  still delivered — full content fell back through `SendMessage`. This occurrence confirms Check 0's
  redundancy framing: the routes fail for unrelated causes, so one failing is survivable, and the
  load-bearing instruction is to name a payload channel at all.
- **2026-09-06 / rotation and harvest pass (issue #213):** live documentation verification against
  code.claude.com/docs/en/tools-reference.md (Agent tool behavior), sub-agents.md (foreground /
  background return), and cross-session-messaging.md (`notify_when_idle`). Claim 1 was imprecise:
  docs deliver a final text result to the parent; only intermediate tool outputs stay invisible.
  The dead-letter failure still holds as observed empty handback (2026-08-04, 2026-08-24), not as
  "all plain text is platform-invisible." Claim 2's "idle notification" was field language for the
  subagent stop signal; docs name that return a completion notification (carries the text result,
  which may be empty). Cross-session `notify_when_idle` is a different feature. Claim 3 holds —
  tool grants remain frontmatter-only, not surfaced at dispatch; registered kill criterion not
  fired on the docs half. Claim 4 remains empirical — docs state no large-return ceiling.
  SKILL.md Check 0 repaired to separate platform path from observed empty-handback failure.
