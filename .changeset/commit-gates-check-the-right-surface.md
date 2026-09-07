---
"mrbinnacle-skills": patch
---

Three commit gates now check the surface they were missing: a residue term in a file or directory name is refused in its underscore, hyphen and dot forms; the vale-prose hook lints the same three paths CI lints; and a new `_quarantine/<skill>/` directory is refused unless it carries `LANDING.md` declaring the landing intentional.
