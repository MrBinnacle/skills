import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { snapshotPacket, validateFilled } from "./close";
import { ghSquashMergeProbe, remoteBranch } from "./head";
import { extract } from "./packet";
import { type Exec, validateRepository } from "./repo";
import type { PacketConfig } from "./settings";
import { listPackets, publishPacket } from "./store";
import { fillScaffold, fixture, git, makeRemote, makeRepo, nodeExec } from "./testkit";

const NETWORK = new Set(["fetch", "ls-remote", "push"]);
const NON_INTERACTIVE = ["-c", "credential.interactive=never", "-c", "core.askPass=", "-c", "core.sshCommand=ssh -o BatchMode=yes"];

/** The git subcommand of an argv, past any leading `-c <key=value>` pairs. */
function subcommand(args: readonly string[]): string | undefined {
  let i = 0;
  while (args[i] === "-c") i += 2;
  return args[i];
}

const config = (): PacketConfig => ({
  dir: ".pi/session-packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [],
  store: { kind: "branch", ref: "session-log", worktree: "var/session-log-worktree" },
});

const SLOW = 30_000;

describe("network git calls", () => {
  test("every fetch, ls-remote and push carries the non-interactive config and a timeout", async () => {
    const calls: { args: string[]; timeout?: number }[] = [];
    const recording: Exec = (command, args, options) => {
      if (command === "git") calls.push({ args, timeout: options.timeout });
      return nodeExec(command, args, options);
    };
    const { root } = await makeRepo();
    await makeRemote(root);
    // origin/HEAD unset, so the ancestor policy asks origin for its default branch too.
    await git(root, "remote", "set-head", "origin", "-d");
    const snap = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: recording });
    if (!snap.ok) throw new Error(snap.error);
    fillScaffold(snap.path);
    const text = readFileSync(snap.path, "utf-8");
    expect((await validateFilled({ snapshot: snap, repoRoot: root, config: config(), exec: recording })).verdict).toBe("ACCEPTED");
    expect((await publishPacket({ repoRoot: root, config: config(), path: snap.path, text, exec: recording })).status).toBe("pushed");
    await listPackets({ repoRoot: root, config: config(), exec: recording });
    const data = extract(fixture("fixture-clean.md"));
    data.repository = { ...(data.repository as Record<string, unknown>), head: "d".repeat(40), branch: "main" };
    await validateRepository({ data, repoRoot: root, exec: recording, headPolicy: "ancestor", squashMerged: async () => ({ mergedHeads: [] }) });

    const network = calls.filter((c) => NETWORK.has(subcommand(c.args) ?? ""));
    expect(new Set(network.map((c) => subcommand(c.args)))).toEqual(NETWORK);
    for (const call of network) {
      expect(call.args.slice(0, NON_INTERACTIVE.length)).toEqual(NON_INTERACTIVE);
      expect(call.timeout).toBeGreaterThan(0);
    }
  }, SLOW);

  test("a hanging network call is cut off by its timeout and reported, never read as success", async () => {
    // Pi's exec resolves a killed child with code 0 and killed: true. Without a timeout, the call
    // hangs far past the test's own timeout (a live timer, so the runner can still time it out).
    const hanging: Exec = (command, args, options) => {
      const network = (command === "git" && NETWORK.has(subcommand(args) ?? "")) || command === "gh";
      if (!network) return nodeExec(command, args, options);
      if (options.timeout) return Promise.resolve({ code: 0, stdout: "", stderr: "", killed: true });
      return new Promise((resolve) => setTimeout(() => resolve({ code: 0, stdout: "", stderr: "" }), 10 * SLOW));
    };
    const { root } = await makeRepo();
    await makeRemote(root);
    const listing = await listPackets({ repoRoot: root, config: config(), exec: hanging });
    expect(listing.notes.some((n) => n.startsWith("store fetch failed") && n.includes("timed out"))).toBe(true);
    const remote = await remoteBranch(hanging, root, "main");
    expect(typeof remote === "object" && "unreachable" in remote && remote.unreachable.includes("timed out")).toBe(true);
    const gh = await ghSquashMergeProbe(hanging)("feature", root);
    expect("unavailable" in gh && gh.unavailable.includes("timed out")).toBe(true);

    const snap = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: nodeExec });
    if (!snap.ok) throw new Error(snap.error);
    fillScaffold(snap.path);
    const text = readFileSync(snap.path, "utf-8");
    const published = await publishPacket({ repoRoot: root, config: config(), path: snap.path, text, exec: hanging });
    expect(published.status).toBe("unpushed");
    expect(published.message).toContain("timed out");
  }, SLOW);
});
