---
"mrbinnacle-skills": patch
---

`scripts/test_install_form.py` now counts only plugins from the `mrbinnacle-skills` marketplace when it reads `claude plugin list --json`. Claude Code 2.1.332 lists its four built-in plugins (`cc-plugin-*@builtin`, version `unknown`) in that output even from an empty config, which its plugin CLI reference says it never does; 2.1.287 to 2.1.331 list none (measured 2026-11-25). The extra rows failed the cold-install check's exact plugin set. Two offline cases cover a built-in row and our plugin name from another marketplace. Repository tooling only; installed users need do nothing.
