# Engineering skills

Workflow disciplines for shipping software. Each one fires at a specific moment — before a
risky `git pull`, at the end of a work phase — rather than sitting in every conversation.
Ordered by how soon the failure is likely to bite you.

- [**git-pull-rebase-trap**](git-pull-rebase-trap/SKILL.md) — if git is configured with
  `pull.rebase=true`, then `git pull --no-ff` silently ignores your flag and rewrites every
  local commit with a new ID. This skill checks the setting before pulling and shows the safe
  alternative. Born from a real incident that rewrote 22 commits
  ([the receipt](git-pull-rebase-trap/EVIDENCE.md)).

- [**closure-mode-at-boundaries**](closure-mode-at-boundaries/SKILL.md) — the moment one phase
  of work finishes is exactly when an assistant is most tempted to charge into the next thing.
  This skill forces a structured wrap-up first: parallel reviewers look for what was missed,
  their fixes actually get executed, and only then is the next step decided.

- [**github-pages-deploy-verification**](github-pages-deploy-verification/SKILL.md) — "the
  deploy went green" is not "the site actually changed." Verify a CDN-fronted static deploy by
  polling for content that did not exist pre-deploy, and use poll patterns the agent harness
  won't block. Origin incident is on a public repo — the receipt is independently checkable
  ([the receipt](github-pages-deploy-verification/EVIDENCE.md)).

- [**session-close**](session-close/SKILL.md) — the producer side of the session-boundary
  pair: at the end of a work session, snapshot repository facts deterministically, write one
  atomic packet (hidden JSON manifest + human narrative), and validate it before claiming
  handoff readiness. The next session must not depend on conversational memory
  ([the receipt](session-close/EVIDENCE.md)).

- [**session-start-from-state**](session-start-from-state/SKILL.md) — the receiver side: a
  fresh session treats the packet as untrusted data, verifies branch and HEAD against the
  repository, probes every verified claim, runs only repository-configured checks, and emits
  an explicit acceptance receipt before any work. The receiver defines packet sufficiency —
  the producer cannot grade itself ([the receipt](session-start-from-state/EVIDENCE.md)).
