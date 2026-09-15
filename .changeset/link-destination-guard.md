---
"mrbinnacle-skills": patch
---

The maintainer workflow installs the collection and holds a pinned copy; it no longer links into the clone. `link-skills.ps1` refuses a destination inside a git working tree that does not ignore the link path, because git records a link as ordinary files and a consumer repository was therefore tracking this repo's bytes in a second index. A seeded suite asserts the refusal by the phrase it prints.
