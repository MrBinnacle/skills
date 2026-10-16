/**
 * Where packets live. The dir store is files in `config.dir`. The branch store (opt-in) commits
 * each packet to an orphan branch through a private worktree and pushes it to origin, so a packet
 * reaches the next machine without entering the code history. No Pi imports.
 */
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { publishScan } from "./packet";
import { dirPackets, type Exec, type ExecResult, git, networkGit, type StoredPacket } from "./repo";
import type { PacketConfig } from "./settings";

export type ResolvedStore = { kind: "dir"; dir: string } | { kind: "branch"; ref: string; worktree: string };

export function resolveStore(repoRoot: string, config: PacketConfig): ResolvedStore {
  const store = config.store ?? { kind: "dir" };
  return store.kind === "branch"
    ? { kind: "branch", ref: store.ref, worktree: resolve(repoRoot, store.worktree) }
    : { kind: "dir", dir: resolve(repoRoot, config.dir) };
}

/** Paths the status_porcelain comparison leaves out: the packet dir, and the store's worktree. */
export function statusExcludes(config: PacketConfig): string[] {
  return config.store?.kind === "branch" ? [config.dir, config.store.worktree] : [config.dir];
}

export interface PacketListing {
  /** Newest first by name. */
  packets: StoredPacket[];
  /** Receive-mode notes: a failed fetch, an unpushed store. */
  notes: string[];
}

const run = (exec: Exec, cwd: string, ...args: string[]): Promise<ExecResult> => exec("git", args, { cwd });
const firstLine = (result: ExecResult) => result.stderr.trim().split(/\r?\n/)[0] || `exit ${result.code}`;
const refExists = async (exec: Exec, cwd: string, ref: string) => (await run(exec, cwd, "rev-parse", "--verify", "--quiet", ref)).code === 0;

/** Update origin/<ref>. A store origin does not have yet is not a failure. */
async function fetchStore(exec: Exec, cwd: string, ref: string): Promise<string | undefined> {
  const result = await networkGit(exec, cwd, "fetch", "-q", "origin", `+refs/heads/${ref}:refs/remotes/origin/${ref}`);
  if (result.code === 0 || /couldn't find remote ref/i.test(result.stderr)) return undefined;
  return `store fetch failed, reading the local copy: ${firstLine(result)}`;
}

/** Stored packets, newest first. The branch store reads its local branch and origin's, after a fetch. */
export async function listPackets(args: { repoRoot: string; config: PacketConfig; exec: Exec }): Promise<PacketListing> {
  const { repoRoot, exec } = args;
  const store = resolveStore(repoRoot, args.config);
  if (store.kind === "dir") return { packets: dirPackets(store.dir), notes: [] };

  const notes: string[] = [];
  const fetchNote = await fetchStore(exec, repoRoot, store.ref);
  if (fetchNote) notes.push(fetchNote);
  const local = `refs/heads/${store.ref}`;
  const remote = `refs/remotes/origin/${store.ref}`;
  const hasLocal = await refExists(exec, repoRoot, local);
  const hasRemote = await refExists(exec, repoRoot, remote);
  const byName = new Map<string, StoredPacket>();
  for (const [full, label, present] of [[local, store.ref, hasLocal], [remote, `origin/${store.ref}`, hasRemote]] as const) {
    if (!present) continue;
    const names = (await git(exec, repoRoot, "ls-tree", "--name-only", full)).split(/\r?\n/).filter((n) => n.endsWith(".md"));
    for (const name of names) {
      if (byName.has(name)) continue;
      byName.set(name, {
        name,
        source: `${label}:${name}`,
        read: async () => {
          const result = await run(exec, repoRoot, "show", `${full}:${name}`);
          if (result.code !== 0) throw new Error(`cannot read ${label}:${name}: ${firstLine(result)}`);
          return result.stdout;
        },
      });
    }
  }
  if (hasLocal && !hasRemote) notes.push(`packet unpushed: store branch ${store.ref} has no copy on origin`);
  if (hasLocal && hasRemote) {
    const ahead = Number(await git(exec, repoRoot, "rev-list", "--count", `${remote}..${local}`));
    if (ahead > 0) notes.push(`packet unpushed: ${ahead} store commit(s) on ${store.ref} are not on origin/${store.ref}`);
  }
  const packets = [...byName.values()].sort((a, b) => (a.name < b.name ? 1 : a.name > b.name ? -1 : 0));
  return { packets, notes };
}

const MIN_GIT = [2, 42] as const;

async function requireOrphanCapableGit(exec: Exec, repoRoot: string): Promise<void> {
  const result = await run(exec, repoRoot, "--version");
  const match = /(\d+)\.(\d+)(?:\.\d+)?/.exec(result.stdout);
  const major = Number(match?.[1]);
  const minor = Number(match?.[2]);
  if (!match || major < MIN_GIT[0] || (major === MIN_GIT[0] && minor < MIN_GIT[1])) {
    throw new Error(
      `the branch store needs git ${MIN_GIT.join(".")} or later (git worktree add --orphan); found ${match?.[0] ?? (result.stdout.trim() || "no git version")}`,
    );
  }
}

/** Keep a worktree inside the repository out of `git status` and out of a `git add -A`. */
async function excludeLocally(exec: Exec, repoRoot: string, worktree: string): Promise<void> {
  const rel = relative(repoRoot, worktree).split(sep).join("/");
  if (!rel || rel.startsWith("..") || isAbsolute(rel)) return;
  const file = join(resolve(repoRoot, await git(exec, repoRoot, "rev-parse", "--git-common-dir")), "info", "exclude");
  const line = `/${rel}/`;
  const current = existsSync(file) ? readFileSync(file, "utf-8") : "";
  if (current.split(/\r?\n/).includes(line)) return;
  mkdirSync(dirname(file), { recursive: true });
  appendFileSync(file, `${current && !current.endsWith("\n") ? "\n" : ""}${line}\n`);
}

/**
 * Make the store's private worktree if it is absent: from the local store branch, else from
 * origin's, else as a new orphan branch. An existing worktree must be on the store branch.
 */
export async function ensureStoreWorktree(args: { repoRoot: string; store: Extract<ResolvedStore, { kind: "branch" }>; exec: Exec }): Promise<void> {
  const { repoRoot, store, exec } = args;
  const { ref, worktree } = store;
  if (existsSync(join(worktree, ".git"))) {
    const branch = (await run(exec, worktree, "branch", "--show-current")).stdout.trim();
    if (branch !== ref) throw new Error(`the branch store worktree ${worktree} is on ${branch || "a detached HEAD"}, not ${ref}`);
    return;
  }
  await requireOrphanCapableGit(exec, repoRoot);
  await excludeLocally(exec, repoRoot, worktree);
  await run(exec, repoRoot, "worktree", "prune");
  await fetchStore(exec, repoRoot, ref);
  if (await refExists(exec, repoRoot, `refs/heads/${ref}`)) await git(exec, repoRoot, "worktree", "add", "-q", worktree, ref);
  else if (await refExists(exec, repoRoot, `refs/remotes/origin/${ref}`)) {
    await git(exec, repoRoot, "worktree", "add", "-q", "--track", "-b", ref, worktree, `origin/${ref}`);
  } else await git(exec, repoRoot, "worktree", "add", "-q", "--orphan", "-b", ref, worktree);
}

export interface PublishResult {
  /** pushed: on origin. unpushed: committed locally only. refused: the scan blocked the commit. failed: the commit itself failed. */
  status: "pushed" | "unpushed" | "refused" | "failed";
  message: string;
}

/**
 * Commit an accepted packet to the store branch and push it. The bytes committed are the bytes
 * validated: the blob is written first, compared with `text` (the bytes produce mode accepted),
 * scanned, and only then staged, and the commit is refused unless the staged set is exactly that
 * one file. A failed push never refuses; a non-fast-forward is resolved by fetch and rebase, which
 * cannot conflict because every packet file name is unique.
 */
export async function publishPacket(args: {
  repoRoot: string;
  config: PacketConfig;
  path: string;
  /** The packet text that was validated. Absent, the file as it is now is what gets committed. */
  text?: string;
  exec: Exec;
}): Promise<PublishResult> {
  const { exec } = args;
  const store = resolveStore(args.repoRoot, args.config);
  if (store.kind !== "branch") throw new Error("publishPacket needs a branch store");
  const { ref, worktree } = store;
  const name = basename(args.path);
  const refuse = (why: string): PublishResult => ({ status: "refused", message: `refusing to commit ${name} to ${ref}: ${why}` });

  const blob = await git(exec, worktree, "hash-object", "-w", "--", name);
  const bytes = (await run(exec, worktree, "cat-file", "blob", blob)).stdout;
  if (args.text !== undefined && bytes !== args.text) {
    return refuse("the packet file changed since it was validated. Close again so the bytes committed are the bytes validated.");
  }
  const leaks = publishScan(bytes);
  if (leaks.length) return refuse(`${leaks.join("; ")}. Remove it from the packet and close again.`);
  await git(exec, worktree, "update-index", "--add", "--cacheinfo", `100644,${blob},${name}`);
  // The commit takes the whole index, and only the packet file was scanned.
  const staged = (await git(exec, worktree, "diff", "--cached", "--name-only", "-z")).split("\0").filter(Boolean);
  const stray = staged.filter((path) => path !== name);
  if (stray.length || !staged.includes(name)) {
    return refuse(`the staged set must be exactly the packet file, and it also holds ${stray.join(", ") || "nothing else"}. Unstage those in ${worktree} and publish again.`);
  }
  // --no-verify on the store's own commit and push only: the repository's hooks are written for
  // the code tree, and in this orphan tree (no hook config) they fail every store commit. The
  // publishScan above is the gate on these bytes instead.
  const commit = await run(exec, worktree, "commit", "--no-verify", "-q", "-m", `session-packet: ${name}`);
  if (commit.code !== 0) return { status: "failed", message: `store commit of ${name} failed: ${firstLine(commit)}` };

  const push = () => networkGit(exec, worktree, "push", "--no-verify", "-q", "-u", "origin", `refs/heads/${ref}:refs/heads/${ref}`);
  const unpushed = (why: string): PublishResult => ({
    status: "unpushed",
    message: `packet ${name} committed to ${ref} but unpushed: ${why}. The next open reports it unpushed; push ${ref} when origin is reachable.`,
  });
  const first = await push();
  if (first.code === 0) return { status: "pushed", message: `packet ${name} committed to ${ref} and pushed to origin` };
  const fetchNote = await fetchStore(exec, worktree, ref);
  if (fetchNote) return unpushed(firstLine(first));
  const rebase = await run(exec, worktree, "rebase", "-q", `refs/remotes/origin/${ref}`);
  if (rebase.code !== 0) {
    await run(exec, worktree, "rebase", "--abort");
    return unpushed(`rebase onto origin/${ref} failed: ${firstLine(rebase)}`);
  }
  const second = await push();
  if (second.code !== 0) return unpushed(firstLine(second));
  return { status: "pushed", message: `packet ${name} committed to ${ref} and pushed to origin after fetch and rebase onto origin/${ref}` };
}
