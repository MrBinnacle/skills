import { describe, expect, test } from "bun:test";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";
import { type Snapshot, snapshotPacket, validateFilled } from "./close";
import { extract } from "./packet";
import type { Exec } from "./repo";
import type { PacketConfig } from "./settings";
import { listPackets, publishPacket } from "./store";
import { cloneRepo, fillScaffold, git, makeRemote, makeRepo, nodeExec } from "./testkit";
import { validatePacket } from "./validate";

const REF = "session-log";
const config = (over: Partial<PacketConfig> = {}): PacketConfig => ({
  dir: ".pi/session-packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [],
  store: { kind: "branch", ref: REF, worktree: "var/session-log-worktree" }, ...over,
});

async function close(root: string, cfg: PacketConfig, second = 0): Promise<Snapshot> {
  const now = new Date(Date.UTC(2026, 0, 1, 0, 0, second));
  const result = await snapshotPacket({ repoRoot: root, config: cfg, objective: "Ship it", exec: nodeExec, now });
  if (!result.ok) throw new Error(result.error);
  fillScaffold(result.path);
  const receipt = await validateFilled({ snapshot: result, repoRoot: root, config: cfg, exec: nodeExec });
  if (receipt.verdict !== "ACCEPTED") throw new Error(JSON.stringify(receipt));
  return result;
}

/** Git on Windows is slow; a store test runs dozens of git processes and two clones. */
const SLOW = 30_000;

const refExists = async (cwd: string, ref: string) =>
  (await nodeExec("git", ["rev-parse", "--verify", "--quiet", ref], { cwd })).code === 0;

describe("branch store", () => {
  test("close writes into a private worktree on an orphan branch; publish commits and pushes it", async () => {
    const { root } = await makeRepo();
    const bare = await makeRemote(root);
    const snap = await close(root, config());
    const worktree = join(root, "var", "session-log-worktree");
    expect(snap.path.startsWith(worktree)).toBe(true);
    expect(basename(snap.path)).toMatch(/^\d{8}T\d{6}Z-[0-9a-f]{8}\.md$/);
    expect(await git(worktree, "branch", "--show-current")).toBe(REF);
    expect(readFileSync(join(root, ".git", "info", "exclude"), "utf-8")).toContain("/var/session-log-worktree/");
    expect(await git(root, "status", "--porcelain")).toBe("");
    expect((extract(readFileSync(snap.path, "utf-8")).repository as { status_porcelain: string }).status_porcelain).toBe("");

    const published = await publishPacket({ repoRoot: root, config: config(), path: snap.path, exec: nodeExec });
    expect(published.status).toBe("pushed");
    expect(await git(bare, "ls-tree", "--name-only", REF)).toBe(basename(snap.path));
    // Orphan: the store shares no history with the code.
    expect((await nodeExec("git", ["merge-base", "main", REF], { cwd: root })).code).not.toBe(0);
  }, SLOW);

  test("open on another clone reads the latest packet from origin after a fetch", async () => {
    const { root } = await makeRepo();
    const bare = await makeRemote(root);
    const snap = await close(root, config());
    await publishPacket({ repoRoot: root, config: config(), path: snap.path, exec: nodeExec });

    const other = await cloneRepo(bare);
    const listing = await listPackets({ repoRoot: other, config: config(), exec: nodeExec });
    expect(listing.packets.map((p) => p.name)).toEqual([basename(snap.path)]);
    const latest = listing.packets[0]!;
    const text = await latest.read();
    expect(extract(text).packet_id).toBe(snap.packetId);
    const receipt = await validatePacket({ text, packetPath: latest.source, mode: "receive", repoRoot: other, config: config(), exec: nodeExec, listing });
    expect(receipt.errors).toEqual([]);
    expect(receipt.verdict).toBe("ACCEPTED");
  }, SLOW);

  test("an offline push warns and does not refuse; the next open reports the packet unpushed", async () => {
    const { root } = await makeRepo();
    await git(root, "remote", "add", "origin", join(tmpdir(), "session-packet-no-such-remote.git"));
    const snap = await close(root, config());
    const published = await publishPacket({ repoRoot: root, config: config(), path: snap.path, exec: nodeExec });
    expect(published.status).toBe("unpushed");
    expect(published.message).toContain("unpushed");
    expect(await git(root, "ls-tree", "--name-only", REF)).toBe(basename(snap.path));

    const listing = await listPackets({ repoRoot: root, config: config(), exec: nodeExec });
    expect(listing.packets[0]?.name).toBe(basename(snap.path));
    const text = await listing.packets[0]!.read();
    const receipt = await validatePacket({ text, packetPath: listing.packets[0]!.source, mode: "receive", repoRoot: root, config: config(), exec: nodeExec, listing });
    expect(receipt.verdict).toBe("ACCEPTED");
    expect(receipt.notes?.some((n) => n.startsWith("packet unpushed:"))).toBe(true);
  }, SLOW);

  test("a non-fast-forward push is resolved by fetch and rebase", async () => {
    const chain = config({ chain: true });
    const { root: a } = await makeRepo();
    const bare = await makeRemote(a);
    const p1 = await close(a, chain, 0);
    expect((await publishPacket({ repoRoot: a, config: chain, path: p1.path, exec: nodeExec })).status).toBe("pushed");

    const b = await cloneRepo(bare);
    const p2 = await close(b, chain, 1); // B's store worktree starts from origin's store, holding p1
    const p3 = await close(a, chain, 2);
    expect((await publishPacket({ repoRoot: a, config: chain, path: p3.path, exec: nodeExec })).status).toBe("pushed");

    const published = await publishPacket({ repoRoot: b, config: chain, path: p2.path, exec: nodeExec });
    expect(published.status).toBe("pushed");
    expect(published.message).toContain("rebase");
    expect((await git(bare, "ls-tree", "--name-only", REF)).split("\n").sort()).toEqual(
      [p1, p2, p3].map((p) => basename(p.path)).sort(),
    );
  }, SLOW);

  test("without the chain, a HEAD a stored packet already claims is refused", async () => {
    const { root } = await makeRepo();
    await makeRemote(root);
    const snap = await close(root, config());
    await publishPacket({ repoRoot: root, config: config(), path: snap.path, exec: nodeExec });
    const again = await snapshotPacket({ repoRoot: root, config: config(), objective: "x", exec: nodeExec });
    expect(again.ok).toBe(false);
    if (!again.ok) expect(again.error).toContain(`already claimed by prior packet ${basename(snap.path)}`);

    // A stored packet is not its own prior.
    const listing = await listPackets({ repoRoot: root, config: config(), exec: nodeExec });
    const stored = listing.packets[0]!;
    const receipt = await validatePacket({ text: await stored.read(), packetPath: stored.source, mode: "produce", repoRoot: root, config: config(), exec: nodeExec, listing });
    expect(receipt.errors).toEqual([]);
  }, SLOW);

  test("git older than 2.42 is refused with the version requirement, and no worktree is made", async () => {
    const { root } = await makeRepo();
    const oldGit: Exec = (command, args, options) =>
      command === "git" && args[0] === "--version"
        ? Promise.resolve({ code: 0, stdout: "git version 2.30.1\n", stderr: "" })
        : nodeExec(command, args, options);
    const result = await snapshotPacket({ repoRoot: root, config: config(), objective: "x", exec: oldGit });
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain("the branch store needs git 2.42 or later (git worktree add --orphan); found 2.30.1");
    expect(existsSync(join(root, "var", "session-log-worktree"))).toBe(false);
  }, SLOW);

  test("a packet carrying an email address or a token is refused before the store commit; nothing is committed or pushed", async () => {
    const { root } = await makeRepo();
    const bare = await makeRemote(root);
    const snap = await close(root, config());
    const original = readFileSync(snap.path, "utf-8");
    for (const leak of ["Ask someone@example.org about it.", `token ghp_${"a".repeat(36)}`]) {
      writeFileSync(snap.path, `${original}\n${leak}\n`);
      const published = await publishPacket({ repoRoot: root, config: config(), path: snap.path, exec: nodeExec });
      expect(published.status).toBe("refused");
      expect(await refExists(root, `refs/heads/${REF}`)).toBe(false);
      expect(await refExists(bare, `refs/heads/${REF}`)).toBe(false);
    }
  }, SLOW);
});

describe("branch store: the bytes committed are the bytes validated", () => {
  test("produce validation with a branch store refuses an email address, so the agent gets a correction turn", async () => {
    const { root } = await makeRepo();
    await makeRemote(root);
    const snap = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: nodeExec });
    if (!snap.ok) throw new Error(snap.error);
    fillScaffold(snap.path);
    writeFileSync(snap.path, `${readFileSync(snap.path, "utf-8")}\nAsk someone@example.org about it.\n`);
    const receipt = await validateFilled({ snapshot: snap, repoRoot: root, config: config(), exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors).toContain("email address or contact string detected");
  }, SLOW);

  test("the dir store's produce validation is unchanged: an email address is not refused there", async () => {
    const { root } = await makeRepo();
    const dirConfig: PacketConfig = { dir: ".pi/session-packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [] };
    const snap = await snapshotPacket({ repoRoot: root, config: dirConfig, objective: "Ship it", exec: nodeExec });
    if (!snap.ok) throw new Error(snap.error);
    fillScaffold(snap.path);
    writeFileSync(snap.path, `${readFileSync(snap.path, "utf-8")}\nAsk someone@example.org about it.\n`);
    const receipt = await validateFilled({ snapshot: snap, repoRoot: root, config: dirConfig, exec: nodeExec });
    expect(receipt.verdict).toBe("ACCEPTED");
  });

  test("a packet file changed after validation is refused; nothing is committed or pushed", async () => {
    const { root } = await makeRepo();
    const bare = await makeRemote(root);
    const snap = await close(root, config());
    const validated = readFileSync(snap.path, "utf-8");
    writeFileSync(snap.path, `${validated}\nEdited after validation.\n`);
    const published = await publishPacket({ repoRoot: root, config: config(), path: snap.path, text: validated, exec: nodeExec });
    expect(published.status).toBe("refused");
    expect(published.message).toContain("changed since it was validated");
    expect(await refExists(root, `refs/heads/${REF}`)).toBe(false);
    expect(await refExists(bare, `refs/heads/${REF}`)).toBe(false);
  }, SLOW);

  test("a store commit is refused unless the staged set is exactly the packet file", async () => {
    const { root } = await makeRepo();
    const bare = await makeRemote(root);
    const snap = await close(root, config());
    const worktree = join(root, "var", "session-log-worktree");
    writeFileSync(join(worktree, "stray.md"), "never scanned");
    await git(worktree, "add", "stray.md");
    const published = await publishPacket({ repoRoot: root, config: config(), path: snap.path, text: readFileSync(snap.path, "utf-8"), exec: nodeExec });
    expect(published.status).toBe("refused");
    expect(published.message).toContain("stray.md");
    expect(await refExists(root, `refs/heads/${REF}`)).toBe(false);
    expect(await refExists(bare, `refs/heads/${REF}`)).toBe(false);
  }, SLOW);
});
