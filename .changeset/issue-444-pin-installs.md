---
"mrbinnacle-skills": patch
---

A fresh install now receives the latest release, not the tip of `main`. Each plugin entry in `.claude-plugin/marketplace.json` pins the release commit as a `git-subdir` source, with the release tag as `ref` and its commit as `sha` ([#444](https://github.com/MrBinnacle/skills/issues/444)). The marketplace name and the plugin names do not change, so an installed user keeps the same plugin ids.

One behaviour changes for projects. Claude Code auto-fetches only relative-path plugin sources onto a new machine. A project that enables these plugins in a committed `.claude/settings.json` no longer installs them by itself on a fresh clone; run `claude plugin install <plugin>@mrbinnacle-skills` once on that machine.
