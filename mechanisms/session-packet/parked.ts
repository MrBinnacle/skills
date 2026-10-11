/**
 * Receive-mode probes for `parked[]`: work the packet says was set aside (a branch, a remote
 * branch, a stash, a worktree) must still exist. The structure rules live in packet.ts.
 */
import { realpathSync } from "node:fs";
import { resolve } from "node:path";
import { remoteBranch } from "./head";
import type { Manifest } from "./packet";
import type { Exec } from "./repo";

function record(value: unknown): Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

/** A comparable form of a path: real, resolved, and case-folded where the file system folds case. */
function canonical(path: string): string {
  let real = resolve(path);
  try {
    real = realpathSync.native(real);
  } catch {
    // A path that does not exist keeps its resolved form; it will simply match nothing.
  }
  return process.platform === "win32" ? real.toLowerCase() : real;
}

async function worktreePaths(exec: Exec, repoRoot: string): Promise<string[]> {
  const result = await exec("git", ["worktree", "list", "--porcelain"], { cwd: repoRoot });
  if (result.code !== 0) return [];
  return result.stdout
    .split(/\r?\n/)
    .filter((line) => line.startsWith("worktree "))
    .map((line) => canonical(line.slice("worktree ".length)));
}

export async function verifyParked(args: { data: Manifest; repoRoot: string; exec: Exec }): Promise<{ errors: string[]; notes: string[] }> {
  const { repoRoot, exec } = args;
  const errors: string[] = [];
  const notes: string[] = [];
  const entries = Array.isArray(args.data.parked) ? args.data.parked : [];
  for (const [i, raw] of entries.entries()) {
    const entry = record(raw);
    const kind = String(entry.kind);
    const ref = String(entry.ref);
    const fail = () => errors.push(`parked[${i}] ${kind} probe failed: ${ref} (${String(entry.reason)})`);
    if (kind === "branch-exists") {
      const result = await exec("git", ["show-ref", "--verify", "--quiet", `refs/heads/${ref}`], { cwd: repoRoot });
      if (result.code !== 0) fail();
    } else if (kind === "remote-branch-exists") {
      const remote = await remoteBranch(exec, repoRoot, ref);
      if (remote === "absent") fail();
      else if (remote !== "present") notes.push(`parked[${i}] remote-branch-exists not verified: could not reach origin: ${remote.unreachable}`);
    } else if (kind === "stash-exists") {
      const result = await exec("git", ["stash", "list", "--format=%H"], { cwd: repoRoot });
      const shas = result.code === 0 ? result.stdout.split(/\r?\n/).filter(Boolean) : [];
      if (!shas.some((sha) => sha.toLowerCase().startsWith(ref.toLowerCase()))) fail();
    } else if (kind === "worktree-exists") {
      if (!(await worktreePaths(exec, repoRoot)).includes(canonical(resolve(repoRoot, ref)))) fail();
    }
  }
  return { errors, notes };
}
