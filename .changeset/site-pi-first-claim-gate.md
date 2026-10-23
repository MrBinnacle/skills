---
---

The landing page no longer calls Pi the runtime this work targets first. Claims ledger row C2 has forbidden that wording on a public surface since the #547 ruling of 2026-10-20, and #561 removed it from the README, but no copy check read the site. `scripts/validate_brand_kit.py` now reads `site/index.html` as a copy surface, and a new `public_claims` block in `assets/tokens.json` refuses the C2 wording on the site, the README, the SVG assets and the repository description. Each claim pattern is tested against its own forbidden and allowed examples. No card changes.
