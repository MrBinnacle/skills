---
"mrbinnacle-skills": patch
---

style(brand): recolour the landing page and the brand assets onto the owner's field palette. The
light scheme becomes warm light, the dark scheme becomes dark wood, and the one accent becomes moss
green on focus and hover only. `assets/tokens.json` replaces the GitHub Primer sets and retires the
`crib` group for `field`, `accent` and `state`. The social preview, both banners and the favicon
are recoloured with every text node and label byte-identical, and the social-preview PNG is
re-exported with its hash pair re-recorded. Patch, under ADR 0002's surface rules: neither the
install path, the card format nor any card name changes, so this touches no declared surface.
