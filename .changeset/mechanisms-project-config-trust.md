---
"mrbinnacle-skills": patch
---

The Pi mechanisms now ignore `.pi/engineering-env.json` unless Pi trusts the project and the project has a `.pi/settings.json`. Before this change, a cloned repository's config supplied shell commands that `/packet-close` and `/packet-open` ran without asking. Pi 1.5.0 reports a project as trusted without asking when `.pi` holds nothing Pi gates, so both conditions are needed. Two behaviours change for an installed user. A project with the config file and no `.pi/settings.json` now gets the verification gate's default patterns, and `/packet-close` and `/packet-open` refuse. `pi -a` alone no longer makes that file count. Each case shows one notice naming the fix.

Action for installed users: if a project of yours carries `.pi/engineering-env.json` and no `.pi/settings.json`, add `.pi/settings.json` containing `{}`, then trust the project in Pi with `/trust`, or pass `-a` to trust it for one command.
