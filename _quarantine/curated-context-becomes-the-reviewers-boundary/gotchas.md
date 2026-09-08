# gotchas — curated-context-becomes-the-reviewers-boundary

Append-only. Never rewrite or delete an entry; add a new one naming the earlier.

## [OBSERVED 2026-09-06] The write-up blamed the reviewer, and that was the real failure

The collision itself cost nothing — a proposed section that a house rule forbids, noticed immediately.

What cost something was the sentence written next: *"the tree overrides the reviewer."* It closed the question. It attributed an error to the reviewer that the brief had caused. And it meant nobody tested the house rule, which turned out to be defective in a way that had already produced 21 unreachable files across the collection.

The operator caught it with one question: *"Do you bother considering what's right before you assume our way is unchangeable."* Nothing in the environment would have.

## [OBSERVED 2026-09-06] The exemplar could not adjudicate, and that was not checked first

The rules in question had been written from a specific card twelve hours earlier. That card was the strongest available evidence about what the maintainer actually endorsed, and it was one read away.

It contains zero markdown links. All three of its auxiliary files are unreferenced. It demonstrates the opening rule and the plain-writing rule and says nothing whatsoever about cross-referencing, so it supports neither side.

The lesson is not "check the exemplar." It is that an exemplar can be silent on the question, and a silent exemplar is a finding rather than a null result — it means the rule was generalised past what it was drawn from.

## [OBSERVED 2026-09-06] The first measurement was wrong in the direction that favoured the argument

The count offered as evidence was "32 of 59 aux files are never named in their own card." It counted six test fixtures and a test script as discoverability failures. No reader should ever traverse those.

The corrected figure, by role, is 21 of 47. Still a real finding, and the correction came from the reviewer, not from the person who produced the number.

Two habits this argues for: classify by role before counting, and expect your own first measurement to be flattering.

## [OBSERVED 2026-09-06] A causal claim rode along with the count

Alongside the count went the claim that the prohibition *caused* the omission. The data shows only that referencing is incomplete. Nothing in it distinguishes "the ban suppressed the positive half" from "nobody wrote pointers either way."

It reached a pull-request body before being caught. The repair was to keep the count, label the causal reading a hypothesis in the rule text itself, and make the fix independent of it.

## [ANTICIPATED] A recommendation that fits your framing perfectly is a warning

The mechanism has no error signal. A curated brief returns a well-argued answer, and its fit with your existing view is exactly what you would expect if you had briefed it properly. Fit is not confirmation. The check is mechanical — for every collision, ask whether the rule was in the brief — because judgement will not surface it.

## [ANTICIPATED] The mirror failure is over-constraining, and it is harder to see

A brief that presents house conventions as immovable gets a recommendation that designs around them and never says they are wrong. That produces no collision at all, so nothing prompts the check. The only defence is stating explicitly, in the brief, which constraints are amendable — and meaning it.

## [ANTICIPATED] Six items is a floor, not a ceiling, and it does not scale by pasting more

The failure mode this skill prevents is omission. The adjacent failure is dumping a repository into a brief, which degrades the answer and hides the decision-relevant material. Both are the brief deciding the answer. The test is decision-relevance, and it needs judgement each time rather than a fixed list of files.
