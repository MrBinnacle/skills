# Preventive recipes

These are recipes, not executable artifacts. Implement and test the guard where it must fire. The decision table is stable; language, paths, and messages are replaceable.

## Shared predicate

Parse shell syntax and then Git arguments. Never search the raw string for a `git` token followed later by a `pull` token: prose, paths, substitutions, and quoted data can contain both.

For each actual `git pull` invocation:

1. Pass if its arguments contain `--rebase`, `--rebase=<mode>`, or `--no-rebase`; that records intent. Pass `--ff-only` too when no `--ff` or `--no-ff` follows it: it cannot rebase (see its table row).
2. Otherwise resolve the current branch and effective `branch.<name>.rebase`, then `pull.rebase`, using normal config scope/includes. Block only when the value selects rebase (`true`, `merges`, `interactive`, or documented aliases).
3. On parse failure, config error, missing Git, or outside a work tree, pass. A preventive guard must fail open rather than wedge the session.

Do not evaluate config except for an actual `pull`. Config reads/writes and text merely naming this skill or guard must pass.

## Required acceptance table

Both recipes below MUST pass this table before use.

| Expected | Case |
|---|---|
| MUST BLOCK | Bare `git pull` with effective rebase config true |
| MUST PASS | `git pull --rebase` (intent recorded) |
| MUST PASS | `git pull --no-rebase` (intent recorded) |
| MUST PASS | `git pull --ff-only` with effective rebase config true. It cannot rebase: on diverged history git refuses and rewrites nothing. Measured on git 2.56.0, 2026-10-05, with `pull.rebase=true` and one local and one remote commit: exit 128, `fatal: Not possible to fast-forward, aborting.`, local commit SHA unchanged |
| MUST PASS | Reading or setting `pull.rebase` or `branch.<name>.rebase` |
| MUST PASS | Any command merely naming `pull-rebase` or the guard file, including a path glob or reading the guard source |
| MUST PASS | A refspec whose path contains the subcommand word, such as `git fetch origin pull/12/head:pr-12`, `git ls-remote origin 'pull/*/head'`, or `git push origin HEAD:refs/pull/12/head`. This is GitHub's documented form for a pull request head, so any adopter who reviews pull requests will run it |
| MUST PASS | A commit whose message body spells the subcommand in prose, such as `git commit -F msg.txt` where the file describes this trap |
| MUST PASS | Guard internal error, missing Git, or outside a repository (fail open; never wedge the session) |

## Pi extension `tool_call` handler

Put a TypeScript file in `~/.pi/agent/extensions/` (all projects) or `.pi/extensions/` (one project). The handler runs before each tool call, ignores every tool except `bash`, and returns `{ block: true, reason }` only for the block case. For every pass it returns nothing.

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// Implement the Shared predicate above: parse the shell syntax and Git arguments,
// then read the effective rebase config in `cwd`. Never scan the raw string.
async function isBlockedPull(command: string, cwd: string): Promise<boolean> {
  return false;
}

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return undefined;
    try {
      if (await isBlockedPull(event.input.command, ctx.cwd)) {
        return {
          block: true,
          reason: "Bare git pull blocked: effective rebase config is enabled; pass --rebase or --no-rebase explicitly.",
        };
      }
    } catch {
      // Fail open: a throwing handler would block the call.
    }
    return undefined;
  });
}
```

The `try`/`catch` is required, not defensive. In Pi a `tool_call` handler that throws blocks the tool as a fail-safe, which is the opposite of what the predicate requires. The handler must catch its own errors to fail open. This is loop-native because `tool_call` fires before every tool call, including calls another tool makes through `ctx.executeTool()`.

Written against Pi 1.1.0's `extensions.md`, read 2026-10-10, with the `bash` command field and `ctx.cwd` taken from the exported extension types and the bundled `permission-gate.ts` example. Not executed.

## Shell wrapper without an agent harness

Put a function named `git` in the operator or automation shell startup. Preserve the real Git path before defining it. Inspect the argument vector: if the subcommand is not `pull`, exec real Git unchanged; otherwise apply the predicate, refuse only the block case, and exec real Git for every pass/error. Never rebuild and rescan a string.

This covers that shell, not programs invoking real Git directly or non-loading shells. Guard every required entry point. Git has no pre-pull client hook: `pre-rebase` runs after `pull` fetched and misses merge-configured pulls. The shell is the non-harness interception point.

Verified 2026-08-12 against Git 2.54.0's live [`githooks`](https://git-scm.com/docs/githooks/2.54.0), [`pull`](https://git-scm.com/docs/git-pull/2.54.0), and [`config`](https://git-scm.com/docs/git-config/2.54.0) manuals. Re-checked 2026-10-05 against git 2.56.0: the `githooks` manual is unchanged since 2.54.0 and still lists no pre-pull hook, and the `git config` manual still lists `true`, `merges` and `interactive` as the rebasing values of `pull.rebase` and `branch.<name>.rebase`.

No repository test executes adopter-owned enforcement. Before relying on either form, run every table row in a disposable repository.
