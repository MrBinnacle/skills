import { describe, expect, test } from "bun:test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { extract } from "./packet";
import type { PacketConfig } from "./settings";
import { fixture, git, makeRepo, nodeExec, renderPacket } from "./testkit";
import { validatePacket } from "./validate";

const config = (over: Partial<PacketConfig> = {}): PacketConfig => ({
  dir: "packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [], ...over,
});
const RED = config({ receiverChecks: [{ name: "under-test", command: "echo boom >&2; exit 1" }] });
const GREEN = config({ receiverChecks: [{ name: "under-test", command: "git rev-parse HEAD" }] });

/** A repo whose HEAD carries the close marker, plus a sound packet text matching it. */
async function soundPacket(fixtureName = "fixture-clean.md") {
  const { root, head } = await makeRepo("chore(state): close\n\nRITUAL: 1");
  const m = extract(fixture(fixtureName));
  m.repository = { ...m.repository, root, head, branch: "main" };
  m.tests = [];
  mkdirSync(join(root, "packets"));
  const packetPath = join(root, "packets", "20260101T000000Z-sound.md");
  const text = renderPacket(m);
  writeFileSync(packetPath, text);
  return { root, head, packetPath, text };
}

describe("validatePacket receipts", () => {
  test("receive mode without a sessionPacket config refuses instead of skipping its checks", async () => {
    const { root, packetPath, text } = await soundPacket();
    const receipt = await validatePacket({ text, packetPath, mode: "receive", repoRoot: root, config: undefined, exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors).toContain("receive mode requires a sessionPacket config");
  });

  test("a sound packet under passing checks is ACCEPTED with exactly the five receipt keys", async () => {
    const { root, packetPath, text } = await soundPacket();
    const receipt = await validatePacket({ text, packetPath, mode: "receive", repoRoot: root, config: GREEN, exec: nodeExec });
    expect(Object.keys(receipt)).toEqual(["verdict", "packet_id", "errors", "notes", "checks"]);
    expect(receipt.verdict).toBe("ACCEPTED");
    expect(receipt.packet_id).toBe("clean-1");
    expect(receipt.checks).toHaveLength(1);
    expect(receipt.checks[0]).toMatchObject({
      name: "under-test", exit_code: 0, status: "passed", output: "omitted: check passed, exit code is the verdict",
    });
    expect(typeof receipt.checks[0]!.duration_ms).toBe("number");
  });

  test("a sound packet under a defective receiver check: REJECTED, assertions held, summary last", async () => {
    const { root, packetPath, text } = await soundPacket();
    const receipt = await validatePacket({ text, packetPath, mode: "receive", repoRoot: root, config: RED, exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors).toEqual(["receiver check failed: under-test"]);
    expect(receipt.packet_assertions_held).toBe(true);
    expect(receipt.failed_receiver_checks).toEqual(["under-test"]);
    expect(Object.keys(receipt).at(-1)).toBe("summary");
    expect(receipt.summary).toContain("receiver checks alone: under-test.");
    expect(receipt.checks[0]).toMatchObject({ status: "failed", exit_code: 1 });
    expect(receipt.checks[0]!.stderr).toContain("boom");
  });

  test("a failing claim probe under the same check: assertions did not hold", async () => {
    const { root, packetPath, text } = await soundPacket("fixture-failed-probe.md");
    const receipt = await validatePacket({ text, packetPath, mode: "receive", repoRoot: root, config: RED, exec: nodeExec });
    expect(receipt.packet_assertions_held).toBe(false);
    expect(receipt.errors).toContain("claim C001 path probe failed: does-not-exist");
    expect(receipt.summary).toContain("not attributable to the receiver checks alone");
  });

  test("an always-zero receiver check is reported as a note", async () => {
    const { root, packetPath, text } = await soundPacket();
    const cfg = config({ receiverChecks: [{ name: "git-status", command: "git status --porcelain" }] });
    const receipt = await validatePacket({ text, packetPath, mode: "receive", repoRoot: root, config: cfg, exec: nodeExec });
    expect(receipt.notes.some((n) => n.includes("'git-status' always exits zero"))).toBe(true);
  });

  test("produce mode refuses a manifest whose tests[] records a red check", async () => {
    const { root } = await makeRepo();
    const text = fixture("fixture-red-check.md");
    const receipt = await validatePacket({ text, packetPath: join(root, "x.md"), mode: "produce", repoRoot: root, config: config(), exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors.some((e) => e.startsWith("recorded receiver check failed: tests[1]"))).toBe(true);
    expect("packet_assertions_held" in receipt).toBe(false);
  });

  test("produce mode runs both the close-commit and the claimed-HEAD refusals", async () => {
    const { root, packetPath, text } = await soundPacket();
    await git(root, "commit", "--allow-empty", "-m", "later work, no ritual line");
    const head = await git(root, "rev-parse", "HEAD");
    writeFileSync(join(root, "packets", "20260106T000000Z-ffff.md"), `<!-- SESSION-PACKET-V1\n{"repository":{"head":"${head}"}}\nSESSION-PACKET-V1 -->`);
    const cfg = config({ closeCommit: { contains: "RITUAL:" } });
    const receipt = await validatePacket({ text, packetPath, mode: "produce", repoRoot: root, config: cfg, exec: nodeExec });
    expect(receipt.errors.some((e) => e.includes("is not the close commit"))).toBe(true);
    expect(receipt.errors.some((e) => e.includes("already claimed"))).toBe(true);
  });

  test("an unreadable packet yields a REJECTED receipt, not a throw", async () => {
    const { root } = await makeRepo();
    const receipt = await validatePacket({ text: "no markers", packetPath: join(root, "x.md"), mode: "receive", repoRoot: root, config: GREEN, exec: nodeExec });
    expect(receipt).toEqual({ verdict: "REJECTED", errors: ["packet markers are absent or out of order"] });
  });
});
