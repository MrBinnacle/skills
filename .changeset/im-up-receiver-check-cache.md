---
"mrbinnacle-skills": minor
---

`im-up` receiver checks may declare `cache_inputs`. The validator keys each such check on the blob hashes of those inputs, the Python version, `git --version` and the command string; a key matching its last passing run is not re-run and is reported `cached` with that key and the time of the run that produced it. Only passing runs are cached. Every receipt check gains `status` (`passed`, `cached`, `failed`) and `duration_ms`. Once a week every check runs uncached and is compared with its cached verdict; a disagreement fails the open and clears that entry. The cache file lives outside the tree. A config with no `cache_inputs` keeps the prior verdicts and fields, plus the two new ones. Card documentation states what `cached` promises. Shared validator and suite stay byte-identical across the `im-up`/`im-down` pair. Implements the session-boundary design step from the parent research ticket (#450, step 2 / design D3).
