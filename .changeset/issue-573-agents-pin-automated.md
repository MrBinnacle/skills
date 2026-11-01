---
---

`AGENTS.md` now describes the automated marketplace pin route. After a release squash merges, `release-pin.yml` opens the pin pull request, and the maintainer approves its workflow runs and merges it. `release-receipt.yml` then opens the install-receipt pull request. The hand-run `check_marketplace_pin.py --write` stays as the fallback. No card changes, and installed users need do nothing.
