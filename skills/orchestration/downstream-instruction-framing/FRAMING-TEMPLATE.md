# Framing template — downstream-instruction-framing

Paste and adapt. Name the actual evidence asymmetry in the brackets.

```
## How to Treat This Document

You are not being given orders. You are being given the prior session's best research
output, written by a session that [name the evidence asymmetry — e.g., could not read
the target codebase directly / worked from summaries only / had no test-run authority].

Each decision below is labeled revisable or non-negotiable. A `Revisit if:` clause names
the evidence that can reopen a revisable decision and who can access it.

Therefore: treat the prior decisions and recommendations as *informed proposals from a
less-informed reviewer*. They reflect what looked right from outside [the relevant
context]. You are inside [the relevant context] now. This default applies only where you
have better evidence access for that decision.

You are explicitly licensed and encouraged to:
- Disagree with the recommendations if [evidence access] reveals the framing was wrong.
  Surface the disagreement to the user with reasoning; don't silently follow a bad plan.
- Restructure sequencing if the real dependency graph differs.
- Reject items that turn out to be solved already, duplicative, or premature.
- Redesign approaches if the proposed design conflicts with what the actual code shows.

What you should NOT do:
- Reopen instructions labeled non-negotiable. Values decisions and explicit constraints
  remain imperative unless their decision authority changes them.
- Silently deviate. The user is the decision authority on scope changes; surface
  disagreement with reasoning, then let them decide.
- Infer that better facts grant decision rights. New evidence licenses the requested
  revisit named below; it does not license unilateral scope changes.
```

## Decision status block

```
## Decision Status

- **Revisable with new evidence:** Phase X expands to include items A, B, C. *Revisit if:*
  repository inspection shows any item is already done,
  duplicative, or has a wrong cost estimate by >2x.
- **Revisable with new evidence:** Design Y was approved. *Revisit if:* the actual architecture
  makes it incompatible,
  or there's a simpler/better way you can see from inside the tree.
- **Non-negotiable:** Do not send customer data to third parties. This is an explicit user
  constraint; surface any conflict, but do not override it.
```
