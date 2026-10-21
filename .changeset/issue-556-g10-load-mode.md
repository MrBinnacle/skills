---
"mrbinnacle-skills": patch
---

Release gate G10 now prices a change to a card's load mode, as ADR 0008 decides. A changeset whose diff moves a card from always-on to by hand (it gains `disable-model-invocation: true`) must declare major, and the reverse must declare at least minor. Both prices are read from ADR 0008's decision sentences, and the gate refuses when either sentence is missing. A card added or removed in the same diff is still priced as an admission or a retirement. Installed users need do nothing.
