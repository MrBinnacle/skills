/**
 * The `ancestor` head policy: a receiver accepts a packet HEAD that differs from the current HEAD
 * when the work it names is still reachable, still on origin, or was squash-merged. Every route
 * is tied to the packet HEAD itself: a branch name that exists, or a PR that merged, is no
 * evidence about a commit that branch or PR does not hold. Everything else is drift, reported with
 * the route each check took. No Pi imports.
 */
import { type Exec, type ExecResult, execNetwork, FULL_OBJECT_ID, isBranchName, networkGit } from "./repo";

/** The head commits of the merged PRs whose head was the branch, or why that was not checked. */
export type SquashMergeResult = { mergedHeads: string[] } | { unavailable: string };
/** The merged PRs of `branch`. Injectable; the default asks `gh`. */
export type SquashMergeProbe = (branch: string, repoRoot: string) => Promise<SquashMergeResult>;

export function ghSquashMergeProbe(exec: Exec): SquashMergeProbe {
  return async (branch, repoRoot) => {
    const args = ["pr", "list", "--state", "merged", "--head", branch, "--json", "number,headRefOid", "--limit", "100"];
    const result = await execNetwork(exec, "gh", args, repoRoot);
    if (result.code !== 0) return { unavailable: result.stderr.trim() || `gh exited ${result.code}` };
    let list: unknown;
    try {
      list = JSON.parse(result.stdout);
    } catch {
      return { unavailable: "gh output was not JSON" };
    }
    if (!Array.isArray(list)) return { unavailable: "gh output was not a list" };
    const heads = list.map((pr) => (typeof pr === "object" && pr !== null ? (pr as { headRefOid?: unknown }).headRefOid : undefined));
    return { mergedHeads: heads.filter((h): h is string => typeof h === "string" && h.length > 0) };
  };
}

const run = (exec: Exec, repoRoot: string, ...args: string[]): Promise<ExecResult> => exec("git", args, { cwd: repoRoot });
const firstLine = (result: ExecResult, what: string) => result.stderr.trim().split(/\r?\n/)[0] || `${what} exited ${result.code}`;
const hasCommit = async (exec: Exec, repoRoot: string, id: string) => (await run(exec, repoRoot, "cat-file", "-e", `${id}^{commit}`)).code === 0;
const isAncestor = async (exec: Exec, repoRoot: string, id: string, of: string) =>
  (await run(exec, repoRoot, "merge-base", "--is-ancestor", id, of)).code === 0;

/** The remote-tracking ref of origin's default branch, e.g. `origin/main`, or undefined. */
async function originDefault(exec: Exec, repoRoot: string): Promise<string | undefined> {
  const local = await run(exec, repoRoot, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD");
  if (local.code === 0 && local.stdout.trim()) return local.stdout.trim();
  const remote = await networkGit(exec, repoRoot, "ls-remote", "--symref", "origin", "HEAD");
  const match = remote.code === 0 ? /^ref: refs\/heads\/(\S+)\s+HEAD$/m.exec(remote.stdout) : null;
  if (!match) return undefined;
  const ref = `origin/${match[1]}`;
  return (await run(exec, repoRoot, "rev-parse", "--verify", "--quiet", `refs/remotes/${ref}`)).code === 0 ? ref : undefined;
}

/**
 * Whether origin has exactly `refs/heads/<branch>`. `git ls-remote` matches a pattern against
 * the tail of each ref, so `refs/heads/x/refs/heads/wip` would answer for `wip`; only an exact
 * ref name counts. Exit 2 is absent; any other failure means origin was not reached.
 */
export async function remoteBranch(exec: Exec, repoRoot: string, branch: string): Promise<"present" | "absent" | { unreachable: string }> {
  const ref = `refs/heads/${branch}`;
  const result = await networkGit(exec, repoRoot, "ls-remote", "--exit-code", "--heads", "origin", ref);
  if (result.code === 0) {
    const refs = result.stdout.split(/\r?\n/).map((line) => line.split("\t")[1]);
    return refs.includes(ref) ? "present" : "absent";
  }
  if (result.code === 2) return "absent";
  return { unreachable: firstLine(result, "git ls-remote") };
}

/**
 * Judge a packet HEAD that differs from the current HEAD. Accepted routes, in order: reachable
 * from HEAD, reachable from origin's default branch, held by its branch on origin (fetched), held
 * by a merged PR of its branch once that branch is deleted on origin. A packet HEAD that is not a
 * full object id is drift before any route runs. A missing tool or an unreachable origin is a
 * note and never converts drift into a pass.
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
  const drift = () => ({ errors: [`HEAD drift: packet=${packetHead} current=${currentHead}: ${failed.join("; ")}`], notes });

  if (!FULL_OBJECT_ID.test(packetHead)) {
    failed.push("the packet HEAD is not a full object id, so no route can be tied to it");
    return drift();
  }

  if (await hasCommit(exec, repoRoot, packetHead)) {
    if (await isAncestor(exec, repoRoot, packetHead, currentHead)) {
      return accept(`HEAD moved: packet HEAD ${packetHead} is reachable from HEAD ${currentHead}`);
    }
    const defaultRef = await originDefault(exec, repoRoot);
    if (defaultRef && (await isAncestor(exec, repoRoot, packetHead, `refs/remotes/${defaultRef}`))) {
      return accept(`HEAD moved: packet HEAD ${packetHead} is reachable from ${defaultRef}`);
    }
    failed.push(defaultRef ? `not reachable from HEAD or ${defaultRef}` : "not reachable from HEAD, and origin has no default branch here");
  } else {
    failed.push("the packet HEAD is absent from this repository");
  }

  if (!packetBranch) {
    failed.push("the packet records no branch");
    return drift();
  }
  if (!(await isBranchName(exec, repoRoot, packetBranch))) {
    failed.push(`branch ${JSON.stringify(packetBranch)} is not a valid branch name`);
    return drift();
  }

  const remote = await remoteBranch(exec, repoRoot, packetBranch);
  if (remote === "present") {
    const tracking = `refs/remotes/origin/${packetBranch}`;
    const fetched = await networkGit(exec, repoRoot, "fetch", "-q", "origin", `+refs/heads/${packetBranch}:${tracking}`);
    if (fetched.code !== 0) {
      notes.push(`could not fetch branch ${packetBranch} from origin: ${firstLine(fetched, "git fetch")}`);
      failed.push(`branch ${packetBranch} on origin not checked for the packet HEAD`);
      return drift();
    }
    if ((await hasCommit(exec, repoRoot, packetHead)) && (await isAncestor(exec, repoRoot, packetHead, tracking))) {
      return accept(`HEAD moved: packet branch ${packetBranch} still exists on origin and holds the packet HEAD`);
    }
    failed.push(`branch ${packetBranch} on origin does not hold the packet HEAD`);
    return drift();
  }
  if (remote !== "absent") {
    notes.push(`could not reach origin to look for branch ${packetBranch}: ${remote.unreachable}`);
    failed.push(`branch ${packetBranch} not checked on origin`);
    return drift();
  }

  failed.push(`branch ${packetBranch} is absent on origin`);
  const probe = await args.squashMerged(packetBranch, repoRoot);
  if ("unavailable" in probe) {
    notes.push(`squash-merge probe unavailable for ${packetBranch}: ${probe.unavailable}`);
    failed.push(`squash merge of ${packetBranch} not checked`);
    return drift();
  }
  const present = await hasCommit(exec, repoRoot, packetHead);
  for (const mergedHead of probe.mergedHeads) {
    const holds = mergedHead === packetHead ||
      (present && FULL_OBJECT_ID.test(mergedHead) && (await hasCommit(exec, repoRoot, mergedHead)) &&
        (await isAncestor(exec, repoRoot, packetHead, mergedHead)));
    if (holds) {
      return accept(`HEAD moved: packet branch ${packetBranch} was deleted on origin after a PR holding the packet HEAD merged (squash-merge)`);
    }
  }
  failed.push(`no merged PR for ${packetBranch} holds the packet HEAD`);
  return drift();
}
