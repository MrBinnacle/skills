/**
 * Assertions a packet makes about a repository, checked against the live tree. No Pi imports:
 * process execution is injected as `Exec` (same shape as Pi's `pi.exec`) so tests run real git
 * or a fake.
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, isAbsolute, join, relative, resolve, sep } from "node:path";
import { checkMovedHead, type SquashMergeProbe } from "./head";
import { extract, type Manifest } from "./packet";
import type { HeadPolicy } from "./settings";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export interface ExecResult {
  code: number;
  stdout: string;
  stderr: string;
  /** Set by Pi's exec when it killed the child (a timeout); the code is then 0 and means nothing. */
  killed?: boolean;
}
export type Exec = (command: string, args: string[], options: { cwd: string; timeout?: number }) => Promise<ExecResult>;

/** How long a call that reaches the network (git fetch, ls-remote, push; gh) may run. */
export const NETWORK_TIMEOUT_MS = 30_000;
/** The exit code a timed-out network call reports, as coreutils `timeout` does. */
export const TIMED_OUT_CODE = 124;

/**
 * Run a command that reaches the network, with a timeout. A killed child is reported as a
 * failure carrying "timed out", never read as success: Pi's exec resolves it with code 0.
 */
export async function execNetwork(exec: Exec, command: string, args: string[], cwd: string): Promise<ExecResult> {
  const result = await exec(command, args, { cwd, timeout: NETWORK_TIMEOUT_MS });
  if (!result.killed) return result;
  return { code: TIMED_OUT_CODE, stdout: result.stdout, stderr: `${command} timed out after ${NETWORK_TIMEOUT_MS / 1000}s` };
}

/**
 * The argv of a git call that reaches origin: no credential prompt, no askpass helper, no ssh
 * password prompt. A prompt with no terminal to answer it hangs the session instead of failing.
 */
export function networkGitArgs(args: readonly string[]): string[] {
  return ["-c", "credential.interactive=never", "-c", "core.askPass=", "-c", "core.sshCommand=ssh -o BatchMode=yes", ...args];
}

/** Every git fetch, ls-remote and push goes through here. */
export function networkGit(exec: Exec, cwd: string, ...args: string[]): Promise<ExecResult> {
  return execNetwork(exec, "git", networkGitArgs(args), cwd);
}

/** A full object id: 40 hex (SHA-1) or 64 hex (SHA-256). Not an abbreviation, a ref or a revision. */
export const FULL_OBJECT_ID = /^(?:[0-9a-f]{40}|[0-9a-f]{64})$/;

/** Whether `name` is a valid branch name. A glob such as `*` is not. */
export async function isBranchName(exec: Exec, cwd: string, name: string): Promise<boolean> {
  if (!name || name.startsWith("-")) return false;
  return (await exec("git", ["check-ref-format", `refs/heads/${name}`], { cwd })).code === 0;
}

export async function git(exec: Exec, cwd: string, ...args: string[]): Promise<string> {
  const result = await exec("git", args, { cwd });
  if (result.code !== 0) throw new Error(result.stderr.trim() || `git ${args.join(" ")} failed`);
  return result.stdout.trim();
}

/** Run a trusted command line. `sh` resolves to Git's sh on Windows; `bash` may resolve to WSL. */
export function shell(exec: Exec, cwd: string, command: string): Promise<ExecResult> {
  return exec("sh", ["-c", command], { cwd });
}

/**
 * `git status --porcelain`, excluding the packet directory (and the branch store's worktree): a
 * packet written into the tree after the snapshot must not make itself stale. The text is
 * whitespace-trimmed when compared, so a packet from validate_packet.py (which strips its stdout)
 * compares equal.
 */
export async function statusPorcelain(exec: Exec, repoRoot: string, packetDir?: string | readonly string[]): Promise<string> {
  const args = ["status", "--porcelain"];
  const excludes: string[] = [];
  for (const dir of typeof packetDir === "string" ? [packetDir] : packetDir ?? []) {
    const rel = relative(repoRoot, resolve(repoRoot, dir)).split(sep).join("/");
    if (rel && !rel.startsWith("..") && !isAbsolute(rel)) excludes.push(`:(exclude)${rel}`);
  }
  if (excludes.length) args.push("--", ".", ...excludes);
  const result = await exec("git", args, { cwd: repoRoot });
  if (result.code !== 0) throw new Error(result.stderr.trim() || "git status failed");
  return result.stdout.trimEnd();
}

export interface RepositoryResult {
  errors: string[];
  notes: string[];
}

export async function validateRepository(args: {
  data: Manifest;
  repoRoot: string;
  exec: Exec;
  /** Commands the repository owner authorised (receiverChecks + trustedProbeCommands). */
  allowedCommands?: readonly string[];
  /** Packet directory (or directories), excluded from the status comparison. */
  packetDir?: string | readonly string[];
  /** Absent means "exact". The caller passes "ancestor" in receive mode only. */
  headPolicy?: HeadPolicy;
  /** Consulted by the ancestor policy only. */
  squashMerged?: SquashMergeProbe;
}): Promise<RepositoryResult> {
  const { data, repoRoot, exec } = args;
  const allowed = new Set(args.allowedCommands ?? []);
  const errors: string[] = [];
  const notes: string[] = [];
  const currentHead = await git(exec, repoRoot, "rev-parse", "HEAD");
  const currentBranch = await git(exec, repoRoot, "branch", "--show-current");
  const expected = isRecord(data.repository) ? data.repository : {};
  const ancestor = args.headPolicy === "ancestor";
  const headMoved = expected.head !== currentHead;
  if (headMoved && !ancestor) errors.push(`stale HEAD: packet=${expected.head} current=${currentHead}`);
  if (headMoved && ancestor) {
    const moved = await checkMovedHead({
      packetHead: String(expected.head ?? ""),
      packetBranch: typeof expected.branch === "string" ? expected.branch : "",
      currentHead,
      repoRoot,
      exec,
      squashMerged: args.squashMerged ?? (async () => ({ unavailable: "no squash-merge probe supplied" })),
    });
    errors.push(...moved.errors);
    notes.push(...moved.notes);
  }
  if (expected.branch !== currentBranch) {
    // Ancestor mode judges lineage by the HEAD routes above, so a branch change alone is a note.
    if (ancestor) notes.push(`branch changed: packet=${expected.branch} current=${currentBranch}`);
    else errors.push(`branch drift: packet=${expected.branch} current=${currentBranch}`);
  }
  if (ancestor && headMoved) {
    notes.push("status_porcelain not compared: HEAD moved since the packet, so its recorded tree no longer applies");
  } else {
    const recorded = String(expected.status_porcelain ?? "").trim();
    const status = (await statusPorcelain(exec, repoRoot, args.packetDir)).trim();
    if (recorded !== status) errors.push(`status drift: packet='${recorded}' current='${status}'`);
  }
  for (const raw of Array.isArray(data.claims) ? data.claims : []) {
    const claim = isRecord(raw) ? raw : {};
    if (claim.status !== "verified") continue;
    const probe = isRecord(claim.probe) ? claim.probe : {};
    const value = String(probe.value);
    if (probe.kind === "path") {
      if (!existsSync(resolve(repoRoot, value))) errors.push(`claim ${claim.id} path probe failed: ${value}`);
    } else if (probe.kind === "commit") {
      const result = await exec("git", ["cat-file", "-e", `${value}^{commit}`], { cwd: repoRoot });
      if (result.code !== 0) errors.push(`claim ${claim.id} commit probe failed: ${value}`);
    } else if (probe.kind === "command") {
      // A command supplied only by the packet is never executed. An unexecuted probe cannot
      // support "verified", so the claim is rejected rather than passed on an advisory note.
      if (!allowed.has(value)) {
        errors.push(
          `claim ${claim.id} command probe is absent from the trusted config allowlist, ` +
            `so a verified status is unsupported: ${value}`,
        );
        continue;
      }
      const result = await shell(exec, repoRoot, value);
      if (result.code !== 0) errors.push(`claim ${claim.id} command probe failed (exit ${result.code}): ${value}`);
      else notes.push(`claim ${claim.id} command probe passed: ${value}`);
    }
  }
  return { errors, notes };
}

/**
 * Produce mode: refuse a packet whose HEAD is not the session-close commit. The close commits
 * first and only then may the packet record HEAD; reversed, the close moves HEAD out from under
 * the packet and the next session rejects it as stale. Opt-in; `contains` is a literal substring.
 */
export async function validateCloseCommit(args: {
  closeCommit: { contains: string } | undefined;
  repoRoot: string;
  exec: Exec;
}): Promise<string[]> {
  const marker = args.closeCommit?.contains;
  if (!marker) return [];
  const message = await git(args.exec, args.repoRoot, "log", "-1", "--pretty=%B");
  if (message.includes(marker)) return [];
  return [
    `HEAD is not the close commit: its message does not carry ${JSON.stringify(marker)}. ` +
      "Close first, then produce the packet -- a packet made before the close records a HEAD the close then moves.",
  ];
}

/** Packet files in `dir`, newest first by name (names start with a UTC timestamp). */
export function packetFiles(dir: string): string[] {
  if (!existsSync(dir) || !statSync(dir).isDirectory()) return [];
  return readdirSync(dir)
    .filter((name) => name.endsWith(".md"))
    .sort()
    .reverse()
    .map((name) => join(dir, name));
}

/** One stored packet: a file in the packet directory, or a file on the branch store. */
export interface StoredPacket {
  /** File name, `<UTC stamp>-<id8>.md`; the newest-first order is by name. */
  name: string;
  /** Where it was read from: an absolute path, or `<ref>:<name>`. */
  source: string;
  read: () => Promise<string>;
}

/** Packets in `dir`, newest first, as stored packets. */
export function dirPackets(dir: string): StoredPacket[] {
  return packetFiles(dir).map((path) => ({ name: basename(path), source: path, read: async () => readFileSync(path, "utf-8") }));
}

/**
 * Produce mode: refuse a HEAD the most recent prior packet already claimed -- this session has
 * not closed yet. Walks newest-first to the first file that parses and records a head, so a stray
 * file cannot disable the guard. The packet under validation is not its own prior. With no usable
 * prior (a fresh clone) the check passes.
 */
export async function validateUnclaimedHead(args: {
  repoRoot: string;
  packetDir: string;
  packetPath: string;
  exec: Exec;
}): Promise<string[]> {
  const own = resolve(args.packetPath);
  const priors = dirPackets(resolve(args.repoRoot, args.packetDir)).filter((p) => resolve(p.source) !== own);
  return unclaimedHeadErrors({ priors, repoRoot: args.repoRoot, exec: args.exec });
}

/** The unclaimed-HEAD walk over priors from any store, newest first. */
export async function unclaimedHeadErrors(args: { priors: readonly StoredPacket[]; repoRoot: string; exec: Exec }): Promise<string[]> {
  if (args.priors.length === 0) return [];
  const currentHead = await git(args.exec, args.repoRoot, "rev-parse", "HEAD");
  for (const prior of args.priors) {
    let claimed: unknown;
    try {
      const repository = extract(await prior.read()).repository;
      claimed = isRecord(repository) ? repository.head : undefined;
    } catch {
      continue;
    }
    if (!claimed) continue;
    if (claimed !== currentHead) return [];
    return [
      `HEAD ${currentHead} is already claimed by prior packet ${prior.name}: this session has not closed yet. ` +
        "Close first, then produce -- the close moves HEAD, and a packet made before it records a HEAD the receiver will reject as stale.",
    ];
  }
  return [];
}
