---
"mrbinnacle-skills": minor
---

The landing page stylesheet joins the declared-hex check. `site/style.css` drew every colour from `assets/tokens.json` and nothing verified that: `scripts/validate_brand_kit.py` read `assets/*.svg` through a hard-coded glob, so a colour reaching a reader through the page was unchecked while the same colour in an asset was refused. A stranger meets the palette on the page first.

The scanned surfaces are now data, under `color.declared_hex_surfaces`, for the same reason the copy surfaces are: a glob hard-coded in the script hides the widening decision inside a diff. Two kinds ship — `svg_hex`, which parses the asset, and `css_hex`, which reads the stylesheet with `/* ... */` removed, because a hex inside a comment paints nothing and the SVG path already gets that exemption from its parser.

The vacuity guards travel with it. The script refuses a surface list that is empty, a kind nothing reads, and a glob matching no file, so a check cannot quietly stop running. Five poison controls and a live non-vacuity case cover the new surface, including the one that matters: planting the sibling instrument's green in the stylesheet is now refused by name, and was not before.
