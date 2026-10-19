import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { Exec } from "./repo";

export const FIXTURES = join(import.meta.dir, "fixtures");

export function fixture(name: string): string {
  return readFileSync(join(FIXTURES, name), "utf-8");
}

/** Real process runner for tests; same shape as Pi's `pi.exec`. */
export const nodeExec: Exec = (command, args, options) =>
  new Promise((resolve) => {
    const child = spawn(command, args, { cwd: options?.cwd, stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", (e) => resolve({ code: 127, stdout, stderr: String(e) }));
    child.on("close", (code) => resolve({ code: code ?? 1, stdout, stderr }));
  });

export async function git(cwd: string, ...args: string[]): Promise<string> {
  const r = await nodeExec("git", args, { cwd });
  if (r.code !== 0) throw new Error(`git ${args.join(" ")}: ${r.stderr}`);
  return r.stdout.trim();
}

/** A temp repo on branch main with README.md committed under `message`. */
export async function makeRepo(message = "fixture"): Promise<{ root: string; head: string }> {
  const root = mkdtempSync(join(tmpdir(), "session-packet-"));
  await git(root, "init", "-b", "main");
  await git(root, "config", "user.email", "test@example.com");
  await git(root, "config", "user.name", "Test");
  await git(root, "config", "core.autocrlf", "false");
  writeFileSync(join(root, "README.md"), "fixture");
  await git(root, "add", "README.md");
  await git(root, "commit", "-m", message);
  return { root, head: await git(root, "rev-parse", "HEAD") };
}

/** A bare repository in a temp dir, added to `root` as `origin` with main pushed and origin/HEAD set. */
export async function makeRemote(root: string): Promise<string> {
  const bare = mkdtempSync(join(tmpdir(), "session-packet-remote-"));
  await git(bare, "init", "--bare", "-b", "main");
  await git(root, "remote", "add", "origin", bare);
  await git(root, "push", "-q", "-u", "origin", "main");
  await git(root, "remote", "set-head", "origin", "main");
  return bare;
}

/** A second working clone of `bare`, standing in for another machine. */
export async function cloneRepo(bare: string): Promise<string> {
  const root = join(mkdtempSync(join(tmpdir(), "session-packet-clone-")), "clone");
  await git(tmpdir(), "clone", "-q", bare, root);
  await git(root, "config", "user.email", "test@example.com");
  await git(root, "config", "user.name", "Test");
  await git(root, "config", "core.autocrlf", "false");
  return root;
}

/** What the agent is asked to do with a scaffold: replace every marker with real content. */
export function fillScaffold(path: string): void {
  writeFileSync(path, readFileSync(path, "utf-8")
    .replace('"task": "__REQUIRED__"', '"task": "Run the suite"')
    .replace('"purpose": "__REQUIRED__"', '"purpose": "Confirm green"')
    .replaceAll("__REQUIRED__", "Filled in."));
}

/** Render a manifest object back into a packet with all four narrative sections. */
export function renderPacket(manifest: unknown, body = "x"): string {
  return [
    "<!-- SESSION-PACKET-V1",
    JSON.stringify(manifest, null, 2),
    "SESSION-PACKET-V1 -->",
    `## Narrative\n${body}\n## Decisions\n${body}\n## What We Tried\n${body}\n## Resume Bootstrap\n${body}\n`,
  ].join("\n");
}
