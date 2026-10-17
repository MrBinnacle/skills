# Receipt: `core.longpaths` and a long `CLAUDE_CONFIG_DIR` on Windows

Measured 2026-10-17 between 20:46 and 20:50 UTC. Requested by the owner for the README candidate in draft PR #456. Measured with the same Windows, Claude Code and git versions as #452.

Paths are published with the account name replaced by `<usr>`, which has the same length as the original, so every printed length still matches the path beside it.

## Host

| Item | Value | How measured |
|---|---|---|
| OS | Windows 11 Home 10.0.26300 | session environment |
| Claude Code | 2.1.302 | `claude --version` |
| git | 2.56.0.windows.1 | `git --version` |
| Node (for the read-back probe only) | v24.19.0 | `node --version` |
| `LongPathsEnabled` | `0x1` | `reg query HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled` |
| `core.longpaths`, every scope, before the runs | unset | `git config --show-origin --get-all core.longpaths` returns nothing, rc 1. `--global --get` and `--system --get` each return nothing, rc 1 |

`LongPathsEnabled = 1` matters for the read-back result below. A host with that value at 0 was not tested.

## Method

- Scripts: `lp-run.sh` (install) and `lp-readback.sh` (read-back), both kept with the run logs in the measuring session's temporary directory and not published. Each run sets `CLAUDE_CONFIG_DIR` to a fresh, empty directory in Windows form, prints its length, then runs the README commands in order: `claude plugin marketplace add https://github.com/MrBinnacle/skills.git`, then `claude plugin install <plugin>@mrbinnacle-skills` for `mrbinnacle-engineering`, `mrbinnacle-orchestration` and `mrbinnacle-meta`.
- **Location departs from the brief.** The brief asked for roots under the session's temporary working directory. That directory is already 128 characters, so a 109-character root cannot exist below it. The roots were placed directly under `C:\Users\<usr>\AppData\Local\Temp\` (34 characters), the same parent #452 used, and padded with `x` to the exact length.
- **How `--global` was emulated.** The real `~/.gitconfig` was not changed. For the ON runs, `GIT_CONFIG_GLOBAL` pointed at a temporary file containing:

  ```
  [include]
  	path = C:/Users/<usr>/.gitconfig
  [core]
  	longpaths = true
  ```

  Each ON run printed `git config --show-origin --get-all core.longpaths` and got `file:"...\lp-gitconfig-global"	true`, rc 0. Claude Code inherits the environment, so the git it spawns sees the same global scope.
- Lengths are Windows-form character counts without the terminating NUL, the same convention as #452. Where `cygpath -w` printed a `\\?\` prefix (paths of 260 or more), 4 characters are subtracted below.
- No model was called. No `claude -p` and no interactive session was started.

## Run OFF: root 109, `core.longpaths` unset

```
CLAUDE_CONFIG_DIR=C:\Users\<usr>\AppData\Local\Temp\lp-off109-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
root length: 109
core.longpaths (show-origin, all scopes):   rc=1
$ claude plugin marketplace add https://github.com/MrBinnacle/skills.git
Adding marketplace…✘ Failed to add marketplace: Failed to clone marketplace repository: Cloning into 'C:\Users\<usr>\AppData\Local\Temp\lp-off109-xxx…xxx\plugins\marketplaces\temp_git_1792269994097_cvckf0..clone'...
fatal: cannot create directory at 'scripts/fixtures/standing-cost-drift/skills/engineering/standing-cost-drift-card': Filename too long
warning: Clone succeeded, but checkout failed.
rc=1
$ claude plugin install mrbinnacle-engineering@mrbinnacle-skills
✘ Failed to install plugin "mrbinnacle-engineering@mrbinnacle-skills": Plugin "mrbinnacle-engineering" not found in marketplace "mrbinnacle-skills". ...
rc=1
```

The `orchestration` and `meta` installs fail with the same message, rc 1. Longest path on disk afterwards: 151 (`backups\.claude.json.backup.<ms>`). No plugin was installed, so there is no `installed_plugins.json` and no commit SHA.

**Finding.** The control holds: at a 109-character root without `core.longpaths`, `marketplace add` fails on the 80-character fixture directory inside the 59-character temporary clone prefix (109 + 59 + 80 = 248), exactly as #452 measured, and all three installs fail after it.

## Run ON: root 109, `core.longpaths=true` at emulated global scope

```
CLAUDE_CONFIG_DIR=C:\Users\<usr>\AppData\Local\Temp\lp-on109-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
root length: 109
$ claude plugin marketplace add https://github.com/MrBinnacle/skills.git
Adding marketplace…Refreshing marketplace cache (timeout: 120s)…
Cloning repository (timeout: 120s): https://github.com/MrBinnacle/skills.git
Clone complete, validating marketplace…
Cleaning up old marketplace cache…
✔ Successfully added marketplace: mrbinnacle-skills (declared in user settings)
rc=0
$ claude plugin install mrbinnacle-engineering@mrbinnacle-skills
✔ Successfully installed plugin: mrbinnacle-engineering@mrbinnacle-skills (scope: user)
rc=0
$ claude plugin install mrbinnacle-orchestration@mrbinnacle-skills
✔ Successfully installed plugin: mrbinnacle-orchestration@mrbinnacle-skills (scope: user)
rc=0
$ claude plugin install mrbinnacle-meta@mrbinnacle-skills
✔ Successfully installed plugin: mrbinnacle-meta@mrbinnacle-skills (scope: user)
rc=0
```

- Longest file on disk: 243, `...\plugins\cache\mrbinnacle-skills\mrbinnacle-orchestration\3.0.1\evals\subagent-handback-celery-worker\graders\answered-the-question.md`.
- Longest directory: 229, the fixture directory at the clone's final location `...\plugins\marketplaces\mrbinnacle-skills\scripts\fixtures\standing-cost-drift\skills\engineering\standing-cost-drift-card`.
- `installed_plugins.json`: all three plugins at version 3.0.1, `gitCommitSha` `eecd5a5c3700959f9c93b9e6093e1a3f0a7ca993`. That is `origin/main` at measurement time, `docs(product): cite the #452 path-limit receipt in the claims ledger (#457)`.

**Finding.** With `core.longpaths=true`, `marketplace add` and all three installs succeed at the 109-character root that fails without it.

### Read-back at root 109

| Command | rc | Result |
|---|---|---|
| `claude plugin list` | 0 | three plugins, version 3.0.1, `✔ enabled` |
| `claude plugin marketplace list` | 0 | `mrbinnacle-skills`, Source Git `https://github.com/MrBinnacle/skills.git` |
| `claude plugin details mrbinnacle-engineering@mrbinnacle-skills` | 0 | `Skills (10)` clirunner-env, closure-mode, halt-as-deliverable, im-down, im-up, mocked-stub, pretooluse-prose, pull-rebase, stale-deploy, vacuous-check |
| `claude plugin details mrbinnacle-orchestration@mrbinnacle-skills` | 0 | `Skills (3)` decision-rights, disposition-schema, subagent-handback |
| `claude plugin details mrbinnacle-meta@mrbinnacle-skills` | 0 | `Skills (1)` dead-predicate |
| `claude plugin validate <cache>\<plugin>\3.0.1\`, each of three | 0 | `✔ Validation passed` (advice only: plugin READMEs lack an install line) |
| `claude plugin validate <root>\plugins\marketplaces\mrbinnacle-skills` | 0 | `✔ Validation passed` |
| `cat` deepest cache file (243) and deepest clone file (241) | 0 | 971 and 599 bytes |
| `cat` every `SKILL.md` in the cache | 0 | 14 of 14 read |

The Claude Code documentation for `claude plugin details` states that it "reads the plugin's files without starting a session" and that its token counts are estimates (code.claude.com/docs/en/plugins/security and /plugins/measure, fetched through Context7 on 2026-10-17). It is therefore a model-free parse of the installed skills.

**Limit of this read-back.** At root 109 every final path is at most 243 characters. The only over-limit path in the 109 case was the temporary clone directory, which exists only during checkout. After the rename to `marketplaces\mrbinnacle-skills` (40 characters of prefix), nothing on disk reaches 260. So the 109 read-back shows that the install is readable, but it does not exercise long-path reading. The 140 run below does.

## Run ON at root 140 (optional third run)

```
CLAUDE_CONFIG_DIR=C:\Users\<usr>\AppData\Local\Temp\lp-on140-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
root length: 140
$ claude plugin marketplace add https://github.com/MrBinnacle/skills.git
✔ Successfully added marketplace: mrbinnacle-skills (declared in user settings)
rc=0
$ claude plugin install mrbinnacle-engineering@mrbinnacle-skills       rc=0
$ claude plugin install mrbinnacle-orchestration@mrbinnacle-skills     rc=0
$ claude plugin install mrbinnacle-meta@mrbinnacle-skills              rc=0
```

- Longest file on disk: 274 (`answered-the-question.md` in the cache, as above), past the 259-character file limit. Longest directory: 260 (the fixture directory in the clone), past the 247-character directory limit (`MAX_DIR` 248 less the NUL) that failed run OFF.
- Files of 260 characters or more: 5 in the plugin cache (all under `mrbinnacle-orchestration\3.0.1\evals\...\graders\`) and 14 in the clone.
- Longest `SKILL.md` in the cache: 231. Every installed `SKILL.md` is still under 260 at this root.
- `installed_plugins.json`: all three plugins at 3.0.1, `gitCommitSha` `eecd5a5c3700959f9c93b9e6093e1a3f0a7ca993`.

Read-back at root 140 gave the same results as at 109. `plugin list`, `marketplace list`, the three `plugin details` calls (10, 3 and 1 skills) and the four `plugin validate` calls all returned rc 0 and `✔ Validation passed`. All 14 `SKILL.md` files read. The two deepest files were then read by their plain Windows path, without a `\\?\` prefix:

| File | Length | `cat` | Node `fs.readFileSync` | `cmd /c type` |
|---|---|---|---|---|
| cache `...\graders\answered-the-question.md` | 274 | rc 0, 971 bytes | rc 0, 971 bytes | rc 0 |
| clone `...\standing-cost-drift-card\EVIDENCE.md` | 272 | rc 0, 599 bytes | rc 0, 599 bytes | rc 0 |

**Finding.** At a 140-character root with `core.longpaths=true`, the install succeeds and Claude Code's model-free subcommands list, inspect and validate all three plugins. Every `SKILL.md` those subcommands read is under 260 characters. The files of 260 or more characters were read back only by git-bash `cat`, Node and `cmd`, on a host where `LongPathsEnabled` is 1. No Claude Code subcommand is shown opening a file of 260 or more characters.

## Run ON at root 175: a second ceiling that `core.longpaths` does not lift

The 175 root was chosen to push the longest `SKILL.md` past 259 (231 + 35 = 266). The install never got that far:

```
CLAUDE_CONFIG_DIR=C:\Users\<usr>\AppData\Local\Temp\lp-on175-x…x
root length: 175
core.longpaths: file:"...\lp-gitconfig-global"	true   rc=0
$ claude plugin marketplace add https://github.com/MrBinnacle/skills.git
Adding marketplace…✘ Failed to add marketplace: Failed to clone marketplace repository: Cloning into 'C:\Users\<usr>\AppData\Local\Temp\lp-on175-x…x\plugins\marketplaces\temp_git_1792270286761_1wls8s..clone'...
fatal: '$GIT_DIR' too big
fatal: remote helper 'https' aborted session
rc=1
```

All three installs then failed with `Plugin "<name>" not found in marketplace "mrbinnacle-skills"`, rc 1.

**Bisection on the root length, ON mode, `marketplace add` only** (script `lp-add.sh`):

| Root | rc | Output |
|---|---|---|
| 157 | 0 | `✔ Successfully added marketplace: mrbinnacle-skills` |
| 158 | 1 | `fatal: '$GIT_DIR' too big` |
| 159 | 1 | same |
| 161 | 1 | same |
| 166 | 1 | same |

The ceiling is 157 characters. At 158 the git directory of the temporary clone is 158 + 58 (`\plugins\marketplaces\temp_git_<13 digits>_<6>..clone`) + 5 (`\.git`) = 221 characters. The failure is therefore consistent with a git check that refuses a `$GIT_DIR` longer than 220 characters. That reading of the git source is inferred from the arithmetic, not read from the source. The failure is independent of `core.longpaths`, which was set and confirmed in this run.

**Full install and read-back at root 157, ON.** `marketplace add` and all three installs returned rc 0, `gitCommitSha` `eecd5a5c3700959f9c93b9e6093e1a3f0a7ca993` for all three. Longest file 291, longest directory 277. Read-back: `plugin list`, `marketplace list`, the three `plugin details` calls (10, 3 and 1 skills) and the four `plugin validate` calls all rc 0 and `✔ Validation passed`. All 14 `SKILL.md` files read. The two deepest files (291 and 289) read with `cat`, rc 0, 971 and 599 bytes. The longest `SKILL.md` was 248 and 12 cache files were 260 or more.

**Finding.** `core.longpaths=true` lifts the install ceiling for the HTTPS form from 108 to 157 characters, not without limit. A root of 158 or more fails at clone with `'$GIT_DIR' too big`. Within that range the longest `SKILL.md` stays at 248 or less, so no `SKILL.md` past 259 can be installed by this form at head, and the question of Claude Code reading one does not arise.

## What was not tested

1. **Skill loading at session start.** Showing that a live session lists these skills needs a model call, which this repository forbids. `claude plugin details` is the nearest model-free evidence: it parses each installed `SKILL.md` and names every skill. Session-start loading is untested.
2. **A host with `LongPathsEnabled = 0`.** This host has it at 1. The over-260 reads above may depend on it. git for Windows handles its own long paths when `core.longpaths` is set, but Node and `cmd` reads would depend on the registry value. Not tested.
3. **Claude Code reading a file of 260 or more characters.** The only such files in the cache are the 5 to 12 eval grader files under `mrbinnacle-orchestration\3.0.1\evals\`. Nothing shows that `details` or `validate` opens them. Session start may or may not. Not tested.
4. **The shorthand install form** (`MrBinnacle/skills`). Only the HTTPS form the README publishes was run. Its clone prefix is 12 characters shorter (#452), so its ceilings are presumably 12 higher; not measured.
5. **The exact git source of `'$GIT_DIR' too big`.** Inferred as above, not read.

## Cleanup

- `rm -rf` on all ten run directories under `C:\Users\<usr>\AppData\Local\Temp\` (`lp-off109`, `lp-on109`, `lp-on140`, `lp-on157`, `lp-on175`, and bisection roots `lp-b157`, `lp-b158`, `lp-b159`, `lp-b161`, `lp-b166`): rc 0 for each, and each was confirmed absent afterwards. Deletion did not fail on the long paths (up to 291 characters).
- The temporary `lp-gitconfig-global` file was removed.
- In a plain shell with no `GIT_CONFIG_GLOBAL` in the environment (`env | grep -c GIT_CONFIG_GLOBAL` printed 0), `git config --global --get core.longpaths` returned nothing, rc 1, and `git config --show-origin --get-all core.longpaths` returned nothing, rc 1. The real `~/.gitconfig` and the registry were not changed.
- The run logs `run-off.log`, `run-on.log`, `run-on140.log`, `run-on157.log`, `run-on175.log` and `readback-on109.log`, `readback-on140.log`, `readback-on157.log` were kept in the measuring session's temporary directory and are not published.

## The README sentence the evidence supports

"On Windows, keep your Claude configuration directory path at 108 characters or fewer. If it is longer, run `git config --global core.longpaths true` before adding the marketplace. That raises the limit to 157 characters; above 157 the install fails even with the setting."

Reason: the control failed at 109, and ON passed at 109, 140 and 157, including the model-free read-back (`plugin list`, `plugin details`, `plugin validate`). ON failed at 158 with a different git error that `core.longpaths` does not address. The sentence replaces the candidate's "about 100" with the measured 108, and it states the 157 ceiling because the unbounded version of the advice is false for roots of 158 or more. Two conditions are not in the sentence and stay on record here: the host had `LongPathsEnabled = 1`, and skill loading at session start was not tested because it needs a model call.
