---
---

The de-personalization gate now reads private terms from outside the public tree: a git-ignored `.residue-private.local` file and a `RESIDUE_PRIVATE_TERMS` repository secret. It checks tracked contents, paths, commit messages and pull request text, and never prints a matched term. No card changes.
