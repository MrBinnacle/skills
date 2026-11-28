---
"mrbinnacle-skills": patch
---

A Binnacle HUD page joins the site at `hud.html`, linked from the landing page footer. It shows the three paths (Log, Memory, Heads-ups or Observer) side by side, states each host's limits beside the claim, and draws the Memory, Claude Code heads-up and Pi observer transitions in the site's own type and both colour schemes, each with a table naming the code. `mechanisms/binnacle-hud/transitions/observer.dot` is the new Pi observer routing source. The site link check now reads every page in `site/`, not only `index.html`.
