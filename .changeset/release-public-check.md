---
"mrbinnacle-skills": patch
---

A release now ends with a check of what readers outside the repository see. `scripts/check_release_public.py` fails when the release tag is missing or off `main`, when any `v*` tag has no published GitHub Release, when another release is marked Latest, or when the site's last change is not deployed, and it names the fix for each. Its first run found v4.0.0, v4.1.0 and v4.1.1 tagged with no GitHub Release, and v3.1.0 still marked Latest. `.changeset/README.md` adds two steps: read the new changelog section as an outside reader before you commit, and run the check after the tag.
