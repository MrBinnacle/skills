# Engineering skills

Workflow disciplines for shipping software. Each one fires at a specific moment — before a
risky `git pull`, at the end of a work phase — rather than sitting in every conversation.
Ordered by how soon the failure is likely to bite you.

- [**pull-rebase**](pull-rebase/SKILL.md) — if git is configured with
  `pull.rebase=true`, then `git pull --no-ff` silently ignores your flag and rewrites every
  local commit with a new ID. This skill checks the setting before pulling and shows the safe
  alternative. Born from a real incident that rewrote 22 commits
  ([the receipt](pull-rebase/EVIDENCE.md)).

- [**closure-mode**](closure-mode/SKILL.md) — the moment one phase
  of work finishes is exactly when an assistant is most tempted to charge into the next thing.
  This skill forces a structured wrap-up first: parallel reviewers look for what was missed,
  their fixes actually get executed, and only then is the next step decided.

- [**stale-deploy**](stale-deploy/SKILL.md) — "the
  deploy went green" is not "the site actually changed." Verify a CDN-fronted static deploy by
  polling for content that did not exist pre-deploy, and use poll patterns the agent harness
  won't block. Origin incident is on a public repo — the receipt is independently checkable
  ([the receipt](stale-deploy/EVIDENCE.md)).

- [**im-down**](im-down/SKILL.md) — the producer side of the session-boundary pair: at the end
  of a work session, snapshot repository facts deterministically, write one atomic packet
  (hidden JSON manifest + human narrative), and validate it before claiming handoff readiness.
  The next session must not depend on conversational memory
  ([the receipt](im-down/EVIDENCE.md)).

- [**im-up**](im-up/SKILL.md) — the receiver side: a fresh session treats the packet as
  untrusted data, verifies branch and HEAD against the repository, probes every verified
  claim, runs only repository-configured checks, and emits an explicit acceptance receipt
  before any work. The receiver defines packet sufficiency — the producer cannot grade itself
  ([the receipt](im-up/EVIDENCE.md)).

- [**clirunner-env**](clirunner-env/SKILL.md) — Click's
  `CliRunner.invoke(env=...)` overrides only the keys the dict names; a key you left out is
  not deleted. A test that builds a "clean" environment by omission runs with the variable
  still set, and can make the live API call it was written to prevent
  ([the receipt](clirunner-env/EVIDENCE.md)).

- [**vacuous-check**](vacuous-check/SKILL.md) — a check
  that accepts any non-empty output passes when the operation failed, because failure output
  is non-empty too. Covers the mirror case as well: a probe reporting NOT-FOUND across a whole
  batch when the tool never ran. Assert the shape success produces, re-read the external
  state, and carry a positive control in any run whose finding is an absence
  ([the receipt](vacuous-check/EVIDENCE.md)).

- [**mocked-stub**](mocked-stub/SKILL.md) — an implementation returns all
  gates green while a branch the shipped behaviour depends on is stubbed, because the test patches
  the very helper that is the stub. Green is evidence the test passed, never evidence the
  production path ran ([the receipt](mocked-stub/EVIDENCE.md)).

- [**pretooluse-prose**](pretooluse-prose/SKILL.md)
  — a `PreToolUse` Bash guard receives the whole command string, so it blocks commit messages,
  heredocs and documentation that only mention what it forbids. Writing about a trap is how
  you trip its guard. Anchor detection to command position, and strip heredoc bodies before
  the predicate runs ([the receipt](pretooluse-prose/EVIDENCE.md)).

- [**halt-as-deliverable**](halt-as-deliverable/SKILL.md) — when a pre-registration or
  pre-flight gate refuses to produce the thing you came for, the refusal is often worth more
  than the thing. A discipline catching its own author, published before the path forward is
  decided, is a claim nobody can copy ([the receipt](halt-as-deliverable/EVIDENCE.md)).
