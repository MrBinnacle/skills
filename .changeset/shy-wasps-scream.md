---
---

Deliberately empty: adding `PRODUCT.md` changes no shipped card, so nothing reaches an installed
user and no version bump is owed.

Recorded as an explicit empty changeset rather than omitted. `AGENTS.md` step 4 and ADR 0002 make
the merge of a version bump the delivery event, so a bump here would announce a delivery that did
not happen. But omitting the changeset entirely leaves no record that the question was considered,
and `changeset status` cannot tell that case apart from an author who simply forgot — it fails
both the same way, which is correct of it.

An empty changeset is the difference between "no release was decided" and "no release was needed".
