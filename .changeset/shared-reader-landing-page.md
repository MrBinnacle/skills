---
"mrbinnacle-skills": patch
---

`scripts/check_shared_readers.py` now refuses a new raw read of `site/index.html` in a script and names the owner to call instead: `landing_page` in `scripts/validate_site_links.py`, which drops the `<wbr>` tags a visitor's copy drops. Repository tooling only; installed users need do nothing.
