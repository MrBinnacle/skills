/**
 * Assertions a packet makes about a repository, checked against the live tree. No Pi imports:
 * process execution is injected as `Exec` (same shape as Pi's `pi.exec`) so tests run real git
 * or a fake.
 */
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, isAbsolute, join, relative, resolve, sep } from "node:path";
import { extract, type Manifest } from "./packet";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export interface ExecResult {
  code: number;
  stdout: string;
  stderr: string;
}
export type Exec = (command: string, args: string[], options: { cwd: string; timeout?: number }) => Promise<ExecResult>;

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
 * `git status --porcelain`, excluding the packet directory: a packet written into the tree after
 * the snapshot must not make itself stale. The text is whitespace-trimmed when compared, so a
 * packet from validate_packet.py (which strips its stdout) compares equal.
 */
export async function statusPorcelain(exec: Exec, repoRoot: string, packetDir?: string): Promise<string> {
  const args = ["status", "--porcelain"];
  if (packetDir) {
    const rel = relative(repoRoot, resolve(repoRoot, packetDir)).split(sep).join("/");
    if (rel && !rel.startsWith("..") && !isAbsolute(rel)) args.push("--", ".", `:(exclude)${rel}`);
  }
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
  /** Packet directory, excluded from the status comparison. */
  packetDir?: string;
}): Promise<RepositoryResult> {
  const { data, repoRoot, exec } = args;
  const allowed = new Set(args.allowedCommands ?? []);
  const errors: string[] = [];
  const notes: string[] = [];
  const currentHead = await git(exec, repoRoot, "rev-parse", "HEAD");
  const currentBranch = await git(exec, repoRoot, "branch", "--show-current");
  const expected = isRecord(data.repository) ? data.repository : {};
  if (expected.head !== currentHead) errors.push(`stale HEAD: packet=${expected.head} current=${currentHead}`);
  if (expected.branch !== currentBranch) errors.push(`branch drift: packet=${expected.branch} current=${currentBranch}`);
  const recorded = String(expected.status_porcelain ?? "").trim();
  const status = (await statusPorcelain(exec, repoRoot, args.packetDir)).trim();
  if (recorded !== status) errors.push(`status drift: packet='${recorded}' current='${status}'`);
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
  const priors = packetFiles(resolve(args.repoRoot, args.packetDir)).filter((p) => resolve(p) !== own);
  if (priors.length === 0) return [];
  const currentHead = await git(args.exec, args.repoRoot, "rev-parse", "HEAD");
  for (const path of priors) {
    let claimed: unknown;
    try {
      const repository = extract(readFileSync(path, "utf-8")).repository;
      claimed = isRecord(repository) ? repository.head : undefined;
    } catch {
      continue;
    }
    if (!claimed) continue;
    if (claimed !== currentHead) return [];
    return [
      `HEAD ${currentHead} is already claimed by prior packet ${basename(path)}: this session has not closed yet. ` +
        "Close first, then produce -- the close moves HEAD, and a packet made before it records a HEAD the receiver will reject as stale.",
    ];
  }
  return [];
}
