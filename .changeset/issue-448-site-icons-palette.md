---
---

The landing page's two raster icons, `site/favicon-32.png` and `site/apple-touch-icon.png`, are re-rendered from `assets/favicon.svg` in the current palette. They last changed on 2026-09-06 and still drew the ink #429 retired, `#1F2328`; the touch icon also had a white ground. The touch icon's ground is now `#F2F4EF` (`structural_light.bg`), the light scheme's backdrop for the SVG's default ink `#1E2020`. `scripts/validate_brand_kit.py` gains a `raster_icon` surface kind. It decodes each listed PNG and refuses any opaque pixel that lies more than the stated tolerance from the listed token colours and the blends between them. `assets/tokens.json` lists one such surface per icon. No card changes, and installed users need do nothing.
