---
"mrbinnacle-skills": patch
---

`scripts/check_release_public.py` now checks the repository social preview, the image a link card shows when someone shares the repository. It reads the image address GitHub reports, downloads that image, and fails unless its bytes equal `assets/social-preview.png`. It also fails when GitHub generates the preview instead of serving an uploaded one. Before this change the check only printed a reminder to look in Settings, so a wrong or missing upload still passed. GitHub serves the uploaded file unchanged: on 2026-11-24 the served image and the asset had the same SHA-256.
