/**
 * The `ancestor` head policy: a receiver accepts a packet HEAD that differs from the current HEAD
 * when the work it names is still reachable, still on origin, or was squash-merged. Everything
 * else is drift, reported with the route each check took. No Pi imports.
 */
import type { Exec, ExecResult } from "./repo";

export type SquashMergeResult = { merged: boolean } | { unavailable: string };
/** Whether `branch` was merged through a PR. Injectable; the default asks `gh`. */
export type SquashMergeProbe = (branch: string, repoRoot: string) => Promise<SquashMergeResult>;

export function ghSquashMergeProbe(exec: Exec): SquashMergeProbe {
  return async (branch, repoRoot) => {
    const args = ["pr", "list", "--state", "merged", "--head", branch, "--json", "number", "--limit", "1"];
    const result = await exec("gh", args, { cwd: repoRoot });
    if (result.code !== 0) return { unavailable: result.stderr.trim() || `gh exited ${result.code}` };
    try {
      const list: unknown = JSON.parse(result.stdout);
      return { merged: Array.isArray(list) && list.length > 0 };
    } catch {
      return { unavailable: "gh output was not JSON" };
    }
  };
}

const run = (exec: Exec, repoRoot: string, ...args: string[]): Promise<ExecResult> => exec("git", args, { cwd: repoRoot });

/** The remote-tracking ref of origin's default branch, e.g. `origin/main`, or undefined. */
async function originDefault(exec: Exec, repoRoot: string): Promise<string | undefined> {
  const local = await run(exec, repoRoot, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD");
  if (local.code === 0 && local.stdout.trim()) return local.stdout.trim();
  const remote = await run(exec, repoRoot, "ls-remote", "--symref", "origin", "HEAD");
  const match = remote.code === 0 ? /^ref: refs\/heads\/(\S+)\s+HEAD$/m.exec(remote.stdout) : null;
  if (!match) return undefined;
  const ref = `origin/${match[1]}`;
  return (await run(exec, repoRoot, "rev-parse", "--verify", "--quiet", `refs/remotes/${ref}`)).code === 0 ? ref : undefined;
}

/** `git ls-remote --exit-code`: 0 found, 2 absent, anything else means origin was not reached. */
export async function remoteBranch(exec: Exec, repoRoot: string, branch: string): Promise<"present" | "absent" | { unreachable: string }> {
  const result = await run(exec, repoRoot, "ls-remote", "--exit-code", "--heads", "origin", `refs/heads/${branch}`);
  if (result.code === 0) return "present";
  if (result.code === 2) return "absent";
  return { unreachable: result.stderr.trim().split("\n")[0] || `git ls-remote exited ${result.code}` };
}

/**
 * Judge a packet HEAD that differs from the current HEAD. Accepted routes, in order: reachable
 * from HEAD, reachable from origin's default branch, its branch still on origin, its branch
 * deleted on origin with a merged PR. A missing tool or an unreachable origin is a note and never
 * converts drift into a pass.
 */
export async function checkMovedHead(args: {
  packetHead: string;
  packetBranch: string;
  currentHead: string;
  repoRoot: string;
  exec: Exec;
  squashMerged: SquashMergeProbe;
}): Promise<{ errors: string[]; notes: string[] }> {
  const { packetHead, packetBranch, currentHead, repoRoot, exec } = args;
  const notes: string[] = [];
  const failed: string[] = [];
  const accept = (note: string) => ({ errors: [], notes: [...notes, note] });

  const exists = (await run(exec, repoRoot, "cat-file", "-e", `${packetHead}^{commit}`)).code === 0;
  if (exists) {
    if ((await run(exec, repoRoot, "merge-base", "--is-ancestor", packetHead, currentHead)).code === 0) {
      return accept(`HEAD moved: packet HEAD ${packetHead} is reachable from HEAD ${currentHead}`);
    }
    const defaultRef = await originDefault(exec, repoRoot);
    if (defaultRef && (await run(exec, repoRoot, "merge-base", "--is-ancestor", packetHead, `refs/remotes/${defaultRef}`)).code === 0) {
      return accept(`HEAD moved: packet HEAD ${packetHead} is reachable from ${defaultRef}`);
    }
    failed.push(defaultRef ? `not reachable from HEAD or ${defaultRef}` : "not reachable from HEAD, and origin has no default branch here");
  } else {
    failed.push("the packet HEAD is absent from this repository");
  }

  if (packetBranch) {
    const remote = await remoteBranch(exec, repoRoot, packetBranch);
    if (remote === "present") return accept(`HEAD moved: packet branch ${packetBranch} still exists on origin`);
    if (remote === "absent") {
      failed.push(`branch ${packetBranch} is absent on origin`);
      const probe = await args.squashMerged(packetBranch, repoRoot);
      if ("merged" in probe && probe.merged) {
        return accept(`HEAD moved: packet branch ${packetBranch} was deleted on origin after its PR merged (squash-merge)`);
      }
      if ("merged" in probe) failed.push(`no merged PR for ${packetBranch}`);
      else {
        notes.push(`squash-merge probe unavailable for ${packetBranch}: ${probe.unavailable}`);
        failed.push(`squash merge of ${packetBranch} not checked`);
      }
    } else {
      notes.push(`could not reach origin to look for branch ${packetBranch}: ${remote.unreachable}`);
      failed.push(`branch ${packetBranch} not checked on origin`);
    }
  } else {
    failed.push("the packet records no branch");
  }
  return { errors: [`HEAD drift: packet=${packetHead} current=${currentHead}: ${failed.join("; ")}`], notes };
}
