---
"mrbinnacle-skills": patch
---

Make the maintainer instructions state the delivery-event model rather than the old "tag by hand if wanted".

AGENTS.md step 4 still described the pre-ADR-0002 model: "tag by hand if wanted", which treats the tag as optional decoration. Under ADR 0002 the merge of the version-bump pull request is the delivery event, not a tag push. The procedure now names the maintainer as who performs the delivering merge, names `python scripts/release_gate.py --write` as the command that stamps plugin versions and reports release fitness (listing every stale surface in one run rather than failing at the first), states that release immutability is enabled and a tag name cannot be reused once spent, and retains the GITHUB_TOKEN prerequisite. `.changeset/README.md` carried the same pre-ADR model ("tag it by hand if you want a tag", "reading aid, not a pin") and now points at the procedure. Pinned by scripts/test_release_model_disclosure.py.
