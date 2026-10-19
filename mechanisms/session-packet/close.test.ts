import { describe, expect, test } from "bun:test";
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join } from "node:path";
import { fillInstructions, snapshotPacket, validateFilled } from "./close";
import { extract } from "./packet";
import type { PacketConfig } from "./settings";
import { git, makeRepo, nodeExec } from "./testkit";
import { validatePacket } from "./validate";

const config = (over: Partial<PacketConfig> = {}): PacketConfig => ({
  dir: ".pi/session-packets", receiverChecks: [{ name: "head", command: "git rev-parse HEAD" }],
  trustedProbeCommands: [], wakeConditions: ["A claim fails."], ...over,
});

/** What the agent is asked to do: replace every marker with real content. */
function fill(path: string) {
  const text = readFileSync(path, "utf-8")
    .replace('"task": "__REQUIRED__"', '"task": "Run the suite"')
    .replace('"purpose": "__REQUIRED__"', '"purpose": "Confirm green"')
    .replaceAll("__REQUIRED__", "Filled in.");
  writeFileSync(path, text);
}

describe("snapshotPacket", () => {
  test("a red receiver check refuses the packet and writes no file", async () => {
    const { root } = await makeRepo();
    const cfg = config({ receiverChecks: [{ name: "under-test", command: "echo nope; exit 1" }] });
    const result = await snapshotPacket({ repoRoot: root, config: cfg, objective: "x", exec: nodeExec });
    expect(result.ok).toBe(false);
    if (result.ok) return;
    expect(result.error).toBe("refusing to write a packet: a receiver check is red");
    expect(result.failed_receiver_checks).toEqual([{ name: "under-test", command: "echo nope; exit 1", exit_code: 1, output: "nope\n" }]);
    expect(existsSync(join(root, ".pi", "session-packets"))).toBe(false);
  });

  test("an empty objective is refused", async () => {
    const { root } = await makeRepo();
    const result = await snapshotPacket({ repoRoot: root, config: config(), objective: "  ", exec: nodeExec });
    expect(result).toEqual({ ok: false, error: "refusing to write a packet: the objective is empty" });
  });

  test("HEAD without the close marker is refused before any file is written", async () => {
    const { root } = await makeRepo("ordinary work");
    const result = await snapshotPacket({ repoRoot: root, config: config({ closeCommit: { contains: "RITUAL:" } }), objective: "x", exec: nodeExec });
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain("HEAD is not the close commit");
    expect(existsSync(join(root, ".pi", "session-packets"))).toBe(false);
  });

  test("a HEAD an earlier packet already claimed is refused", async () => {
    const { root } = await makeRepo();
    const first = await snapshotPacket({ repoRoot: root, config: config(), objective: "x", exec: nodeExec });
    expect(first.ok).toBe(true);
    const second = await snapshotPacket({ repoRoot: root, config: config(), objective: "x", exec: nodeExec });
    expect(second.ok).toBe(false);
    if (!second.ok) expect(second.error).toContain("already claimed");
  });

  test("the scaffold records the measured git facts and checks, and is unfinished until filled", async () => {
    const { root, head } = await makeRepo();
    const result = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: nodeExec });
    if (!result.ok) throw new Error(result.error);
    expect(readdirSync(join(root, ".pi", "session-packets"))).toEqual([basename(result.path)]);
    expect(result.path).toMatch(/\d{8}T\d{6}Z-[0-9a-f]{8}\.md$/);
    const m = extract(readFileSync(result.path, "utf-8"));
    expect(m.repository).toMatchObject({ head, branch: "main", status_porcelain: "" });
    expect(m.tests).toEqual([expect.objectContaining({ command: "git rev-parse HEAD", exit_code: 0, status: "passed", head })]);
    expect(m.objective).toBe("Ship it");
    expect(m.wake_conditions).toEqual(["A claim fails."]);
    const receipt = await validateFilled({ snapshot: result, repoRoot: root, config: config(), exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors).toContain("unfinished marker present: __REQUIRED__");
  });

  test("a filled scaffold is ACCEPTED in produce mode and then by the receiver", async () => {
    const { root } = await makeRepo();
    const result = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: nodeExec });
    if (!result.ok) throw new Error(result.error);
    fill(result.path);
    const produced = await validateFilled({ snapshot: result, repoRoot: root, config: config(), exec: nodeExec });
    expect(produced.errors).toEqual([]);
    expect(produced.verdict).toBe("ACCEPTED");
    const text = readFileSync(result.path, "utf-8");
    const received = await validatePacket({ text, packetPath: result.path, mode: "receive", repoRoot: root, config: config(), exec: nodeExec });
    expect(received.verdict).toBe("ACCEPTED");
  });

  test("a fill that edits the measured facts is refused", async () => {
    const { root } = await makeRepo();
    const result = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: nodeExec });
    if (!result.ok) throw new Error(result.error);
    fill(result.path);
    const text = readFileSync(result.path, "utf-8").replace(/"tests": \[[\s\S]*?\],\n  "skills_dispatched"/, '"tests": [],\n  "skills_dispatched"');
    writeFileSync(result.path, text);
    const receipt = await validateFilled({ snapshot: result, repoRoot: root, config: config(), exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors).toContain("measured facts edited: tests differs from what /packet-close measured");
  });

  test("the fill instructions name the file and forbid touching the measured facts", async () => {
    const { root } = await makeRepo();
    const result = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: nodeExec });
    if (!result.ok) throw new Error(result.error);
    const message = fillInstructions(result);
    expect(message).toContain(result.path);
    expect(message).toContain("__REQUIRED__");
    expect(message).toContain("Do not edit");
  });

  test("committing after the snapshot makes the produced packet stale", async () => {
    const { root } = await makeRepo();
    const result = await snapshotPacket({ repoRoot: root, config: config(), objective: "Ship it", exec: nodeExec });
    if (!result.ok) throw new Error(result.error);
    fill(result.path);
    await git(root, "commit", "--allow-empty", "-m", "late commit");
    const receipt = await validateFilled({ snapshot: result, repoRoot: root, config: config(), exec: nodeExec });
    expect(receipt.errors.some((e) => e.startsWith("stale HEAD"))).toBe(true);
  });
});
