import { describe, expect, test } from "bun:test";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fillInstructions, type Snapshot, snapshotPacket, validateFilled } from "./close";
import { extract } from "./packet";
import type { PacketConfig } from "./settings";
import { fillScaffold, makeRepo, nodeExec } from "./testkit";
import { validatePacket } from "./validate";

const config = (over: Partial<PacketConfig> = {}): PacketConfig => ({
  dir: ".pi/session-packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [], ...over,
});
const CHAIN = config({ chain: true });

async function close(root: string, cfg: PacketConfig, second: number): Promise<Snapshot> {
  const now = new Date(Date.UTC(2026, 0, 1, 0, 0, second));
  const result = await snapshotPacket({ repoRoot: root, config: cfg, objective: "Ship it", exec: nodeExec, now });
  if (!result.ok) throw new Error(result.error);
  fillScaffold(result.path);
  return result;
}

describe("packet chain (opt-in)", () => {
  test("by default the scaffold carries no previous_packet_id and the fill instructions are unchanged", async () => {
    const { root } = await makeRepo();
    const snap = await close(root, config(), 0);
    expect("previous_packet_id" in extract(readFileSync(snap.path, "utf-8"))).toBe(false);
    const message = fillInstructions(snap);
    expect(message).toContain("Do not edit packet_id, created_at, repository or tests:");
    expect(message).not.toContain("parked");
  });

  test("the first packet of a chain has a null parent; a second close at the same HEAD is allowed and links to it", async () => {
    const { root } = await makeRepo();
    const first = await close(root, CHAIN, 0);
    expect(extract(readFileSync(first.path, "utf-8")).previous_packet_id).toBeNull();
    const second = await close(root, CHAIN, 1);
    expect(second.head).toBe(first.head);
    expect(extract(readFileSync(second.path, "utf-8")).previous_packet_id).toBe(first.packetId);
    const receipt = await validateFilled({ snapshot: second, repoRoot: root, config: CHAIN, exec: nodeExec });
    expect(receipt.errors).toEqual([]);
    expect(receipt.verdict).toBe("ACCEPTED");
  });

  test("previous_packet_id is a measured fact: a fill that edits it is refused", async () => {
    const { root } = await makeRepo();
    await close(root, CHAIN, 0);
    const second = await close(root, CHAIN, 1);
    const text = readFileSync(second.path, "utf-8").replace(/"previous_packet_id": "[^"]+"/, '"previous_packet_id": null');
    writeFileSync(second.path, text);
    const receipt = await validateFilled({ snapshot: second, repoRoot: root, config: CHAIN, exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors).toContain("measured facts edited: previous_packet_id differs from what /packet-close measured");
  });

  test("the chain's fill instructions name previous_packet_id and parked[]", async () => {
    const { root } = await makeRepo();
    const message = fillInstructions(await close(root, CHAIN, 0));
    expect(message).toContain("Do not edit packet_id, created_at, previous_packet_id, repository or tests:");
    expect(message).toContain("parked");
  });

  test("two packets with the same parent are reported as two heads, both kept, never refused", async () => {
    const { root } = await makeRepo();
    const parent = await close(root, CHAIN, 0);
    const left = await close(root, CHAIN, 1);
    // A concurrent close elsewhere: same parent, its own id, a later name.
    const rightId = "11111111-2222-4333-8444-555555555555";
    const rightPath = join(dirname(left.path), `20260101T000002Z-${rightId.slice(0, 8)}.md`);
    writeFileSync(rightPath, readFileSync(left.path, "utf-8").replace(left.packetId, rightId));

    const text = readFileSync(rightPath, "utf-8");
    const receipt = await validatePacket({ text, packetPath: rightPath, mode: "receive", repoRoot: root, config: CHAIN, exec: nodeExec });
    expect(receipt.verdict).toBe("ACCEPTED");
    const twoHeads = receipt.notes?.find((n) => n.startsWith("two heads:"));
    expect(twoHeads).toBeDefined();
    expect(twoHeads).toContain(left.packetId);
    expect(twoHeads).toContain(rightId);
    expect(twoHeads).toContain(parent.packetId);

    const produced = await validateFilled({ snapshot: left, repoRoot: root, config: CHAIN, exec: nodeExec });
    expect(produced.verdict).toBe("ACCEPTED");
    expect(produced.notes?.some((n) => n.startsWith("two heads:"))).toBe(true);
  });
});

describe("packet chain parent", () => {
  test("an abandoned, unfilled scaffold is never the parent: the newest filled packet is", async () => {
    const { root } = await makeRepo();
    const first = await close(root, CHAIN, 0);
    const abandoned = await snapshotPacket({ repoRoot: root, config: CHAIN, objective: "Abandoned", exec: nodeExec, now: new Date(Date.UTC(2026, 0, 1, 0, 0, 1)) });
    expect(abandoned.ok).toBe(true);
    const third = await close(root, CHAIN, 2);
    expect(extract(readFileSync(third.path, "utf-8")).previous_packet_id).toBe(first.packetId);
  });
});
