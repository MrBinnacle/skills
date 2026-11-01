---
---

Repository tooling only. `pi/scripts/` adds the Pi acceptance tooling: an offline regression suite, the live acceptance runner and its evidence capture. A new workflow, `pi-acceptance.yml`, runs the offline suite on Ubuntu and Windows when those paths change. `.pi/engineering-env.json` no longer counts `release_gate.py --write` as a verification check, and it now counts `bun test`. No card, install path or plugin manifest changes, so installed users need do nothing.
