---
"mrbinnacle-skills": patch
---

The verify-gate demo picture is drawn in the site's own tokens and type (#699): colours from `assets/tokens.json`, the IBM Plex stacks with their system fallbacks, no embedded fonts, planks or grain, and red for FAIL only. It now ships as four files, `demo-dark.svg`, `demo-light.svg` and a one-column `-narrow` pair for phones, served through `<picture>` by scheme and width on the README and the landing page; phones see the picture again instead of a link. Each file is 10 KB instead of 78 KB. The Barlow and Overpass Mono subsets are gone. The site link check now resolves `srcset` as it does `src`.
