import { test as bunTest } from "bun:test";
import { AsyncLocalStorage } from "node:async_hooks";
import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { Exec } from "./repo";

export const FIXTURES = join(import.meta.dir, "fixtures");

/**
 * Per-test timeout for a test that spawns real `git`. On a green Windows CI
 * run such a test takes about 1.5 s; on a slow one, from 4 s to more than 5 s,
 * past bun's 5000 ms default (#501, #607). Pure tests keep the default, so a
 * slow pure test still fails.
 */
export const GIT_TIMEOUT = 30_000;

// bun does not cancel a timed-out body, so each test keeps its own list: a late makeRepo cannot land in the next test's.
const testDirs = new AsyncLocalStorage<string[]>();

/** A temp directory the running test owns. It goes when the test passes and stays when the test fails. */
function tempDir(prefix: string): string {
  const dir = realpathSync.native(mkdtempSync(join(tmpdir(), prefix)));
  testDirs.getStore()?.push(dir);
  return dir;
}

/** Hand a directory the test made itself, such as a sibling worktree, to the same cleanup. */
export function ownTempDir(dir: string): void {
  testDirs.getStore()?.push(dir);
}

type TestBody = (...args: never[]) => unknown;

const keep = (dirs: string[]) => {
  if (dirs.length > 0) console.error(`session-packet: kept ${dirs.length} temp directories for diagnosis: ${dirs.join(" ")}`);
};

// bun:test gives hooks no pass or fail status (1.3.11), and a module-level afterAll binds to one test file only,
// so the wrapper around each test body does the cleanup.
// shortcut: 5000 is bun's default timeout and ignores `bun test --timeout`, read the flag if a run ever lowers it.
const cleaned = (body: TestBody, timeout = 5_000) => (...args: never[]) => {
  const dirs: string[] = [];
  return testDirs.run(dirs, async () => {
    const started = Date.now();
    try {
      await body(...args);
    } catch (e) {
      keep(dirs);
      throw e;
    }
    if (Date.now() - started >= timeout) return keep(dirs); // the body outlived its test, which bun already failed
    for (const dir of dirs) {
      try {
        rmSync(dir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
      } catch (e) {
        console.error(`session-packet: could not remove ${dir}: ${e}`);
      }
    }
  });
};

/**
 * bun:test's `test` and `test.each` with temp directory cleanup. `skip` and `todo` run no body, so they are bun's own.
 * shortcut: other members, such as `test.if`, throw a TypeError here, add one when a test needs it.
 */
export const test = Object.assign(
  (name: string, body: TestBody, timeout?: number) => bunTest(name, cleaned(body, timeout), timeout),
  {
    each: (table: readonly unknown[]) => (name: string, body: TestBody, timeout?: number) =>
      bunTest.each(table as unknown[])(name, cleaned(body, timeout) as never, timeout),
    skip: bunTest.skip,
    todo: bunTest.todo,
  },
) as unknown as typeof bunTest;

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
  const root = tempDir("session-packet-");
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
  const bare = tempDir("session-packet-remote-");
  await git(bare, "init", "--bare", "-b", "main");
  await git(root, "remote", "add", "origin", bare);
  await git(root, "push", "-q", "-u", "origin", "main");
  await git(root, "remote", "set-head", "origin", "main");
  return bare;
}

/** A second working clone of `bare`, standing in for another machine. */
export async function cloneRepo(bare: string): Promise<string> {
  const root = join(tempDir("session-packet-clone-"), "clone");
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
