---
"mrbinnacle-skills": patch
---

`scripts/test_install_form.py` now reads the landing page with its `<wbr>` tags removed. The page writes the install address as `https://github.com/<wbr>MrBinnacle/skills.git` so a phone can break the line, and the check compared raw HTML, so it reported the HTTPS install command as missing although a visitor sees and copies it whole. Repository tooling only; installed users need do nothing.
