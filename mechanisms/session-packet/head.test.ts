import { describe, expect, test } from "bun:test";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { ghSquashMergeProbe, type SquashMergeProbe, type SquashMergeResult } from "./head";
import { extract, type Manifest } from "./packet";
import { type Exec, validateRepository } from "./repo";
import { fixture, git, makeRemote, makeRepo, nodeExec, renderPacket } from "./testkit";
import { validatePacket } from "./validate";

function packetAt(root: string, head: string, branch = "main"): Manifest {
  const m = extract(fixture("fixture-clean.md"));
  m.repository = { ...(m.repository as Record<string, unknown>), root, head, branch };
  return m;
}

const neverProbed: SquashMergeProbe = async () => {
  throw new Error("the squash-merge probe must not run here");
};

function answering(result: SquashMergeResult) {
  const asked: string[] = [];
  const probe: SquashMergeProbe = async (branch) => {
    asked.push(branch);
    return result;
  };
  return { asked, probe };
}

/** Tests that push to a bare origin run many git processes; Git on Windows is slow. */
const SLOW = 20_000;

const ancestor = (data: Manifest, root: string, squashMerged: SquashMergeProbe = neverProbed) =>
  validateRepository({ data, repoRoot: root, exec: nodeExec, headPolicy: "ancestor", squashMerged });

/** A repo with origin, where `feature` holds commit P and main has moved past the fork. */
async function featureFork() {
  const { root } = await makeRepo();
  await makeRemote(root);
  await git(root, "checkout", "-q", "-b", "feature");
  await git(root, "commit", "-q", "--allow-empty", "-m", "feature work");
  const p = await git(root, "rev-parse", "HEAD");
  await git(root, "push", "-q", "-u", "origin", "feature");
  await git(root, "checkout", "-q", "main");
  await git(root, "commit", "-q", "--allow-empty", "-m", "main moves on");
  await git(root, "push", "-q", "origin", "main");
  return { root, p };
}

describe("headPolicy exact (the default)", () => {
  test("a packet HEAD that is an ancestor of HEAD is still a stale HEAD", async () => {
    const { root, head } = await makeRepo();
    await git(root, "commit", "-q", "--allow-empty", "-m", "later");
    const result = await validateRepository({ data: packetAt(root, head), repoRoot: root, exec: nodeExec });
    expect(result.errors.some((e) => e.startsWith("stale HEAD"))).toBe(true);
  });
});

describe("headPolicy ancestor", () => {
  test("a packet HEAD reachable from HEAD is accepted, and status_porcelain is not compared once HEAD moved", async () => {
    const { root, head } = await makeRepo();
    await git(root, "commit", "-q", "--allow-empty", "-m", "later");
    writeFileSync(join(root, "README.md"), "dirty");
    const result = await ancestor(packetAt(root, head), root);
    expect(result.errors).toEqual([]);
    expect(result.notes.some((n) => n.includes("reachable from HEAD"))).toBe(true);
    expect(result.notes.some((n) => n.includes("status_porcelain not compared"))).toBe(true);
  });

  test("an unchanged HEAD still compares status_porcelain", async () => {
    const { root, head } = await makeRepo();
    writeFileSync(join(root, "README.md"), "dirty");
    const result = await ancestor(packetAt(root, head), root);
    expect(result.errors).toEqual(["status drift: packet='' current='M README.md'"]);
  });

  test("a packet HEAD reachable from origin's default branch is accepted; a branch change is a note", async () => {
    const { root } = await makeRepo();
    await makeRemote(root);
    await git(root, "commit", "-q", "--allow-empty", "-m", "on main");
    const p = await git(root, "rev-parse", "HEAD");
    await git(root, "push", "-q", "origin", "main");
    await git(root, "checkout", "-q", "-b", "side", "HEAD~1");
    await git(root, "commit", "-q", "--allow-empty", "-m", "side work");
    const result = await ancestor(packetAt(root, p, "main"), root);
    expect(result.errors).toEqual([]);
    expect(result.notes.some((n) => n.includes("reachable from origin/main"))).toBe(true);
    expect(result.notes).toContain("branch changed: packet=main current=side");
  }, SLOW);

  test("a packet HEAD whose branch still exists on origin is accepted", async () => {
    const { root, p } = await featureFork();
    const result = await ancestor(packetAt(root, p, "feature"), root);
    expect(result.errors).toEqual([]);
    expect(result.notes.some((n) => n.includes("branch feature still exists on origin"))).toBe(true);
  }, SLOW);

  test("a squash-merged packet branch (deleted on origin, PR merged) is accepted through the probe", async () => {
    const { root, p } = await featureFork();
    await git(root, "push", "-q", "origin", "--delete", "feature");
    const { asked, probe } = answering({ merged: true });
    const result = await ancestor(packetAt(root, p, "feature"), root, probe);
    expect(asked).toEqual(["feature"]);
    expect(result.errors).toEqual([]);
    expect(result.notes.some((n) => n.includes("feature") && n.includes("merged"))).toBe(true);
  }, SLOW);

  test("a diverged HEAD is drift, with the details of every route that failed", async () => {
    const { root, p } = await featureFork();
    await git(root, "push", "-q", "origin", "--delete", "feature");
    const result = await ancestor(packetAt(root, p, "feature"), root, answering({ merged: false }).probe);
    expect(result.errors).toHaveLength(1);
    const [drift] = result.errors;
    expect(drift).toStartWith(`HEAD drift: packet=${p} current=`);
    expect(drift).toContain("not reachable from HEAD or origin/main");
    expect(drift).toContain("branch feature is absent on origin");
    expect(drift).toContain("no merged PR for feature");
  }, SLOW);

  test("an unavailable squash-merge probe is a note; the drift stays an error", async () => {
    const { root, p } = await featureFork();
    await git(root, "push", "-q", "origin", "--delete", "feature");
    const result = await ancestor(packetAt(root, p, "feature"), root, answering({ unavailable: "gh: command not found" }).probe);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0]).toStartWith("HEAD drift:");
    expect(result.notes).toContain("squash-merge probe unavailable for feature: gh: command not found");
  }, SLOW);

  test("a vanished packet HEAD is drift naming its absence", async () => {
    const { root } = await makeRepo();
    const gone = "d".repeat(40);
    const result = await ancestor(packetAt(root, gone, ""), root);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0]).toStartWith(`HEAD drift: packet=${gone}`);
    expect(result.errors[0]).toContain("absent from this repository");
  });

  test("receive mode applies the configured headPolicy", async () => {
    const { root, head } = await makeRepo();
    await git(root, "commit", "-q", "--allow-empty", "-m", "later");
    mkdirSync(join(root, "packets"));
    const packetPath = join(root, "packets", "20260101T000000Z-aaaa.md");
    const m = packetAt(root, head);
    m.tests = [];
    const text = renderPacket(m);
    writeFileSync(packetPath, text);
    const config = { dir: "packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [], headPolicy: "ancestor" as const };
    const receipt = await validatePacket({ text, packetPath, mode: "receive", repoRoot: root, config, exec: nodeExec, squashMerged: neverProbed });
    expect(receipt.errors).toEqual([]);
    expect(receipt.verdict).toBe("ACCEPTED");
  });

  test("produce mode keeps an exact HEAD: a commit during the fill still makes the packet stale", async () => {
    const { root, head } = await makeRepo();
    await git(root, "commit", "-q", "--allow-empty", "-m", "committed during the fill");
    const m = packetAt(root, head);
    m.tests = [];
    const config = { dir: "packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [], headPolicy: "ancestor" as const };
    const receipt = await validatePacket({
      text: renderPacket(m), packetPath: join(root, "p.md"), mode: "produce", repoRoot: root, config, exec: nodeExec, squashMerged: neverProbed,
    });
    expect(receipt.errors.some((e) => e.startsWith("stale HEAD"))).toBe(true);
  });
});

describe("ghSquashMergeProbe (the default probe)", () => {
  const fake = (code: number, stdout: string, stderr = "") => {
    const calls: string[][] = [];
    const exec: Exec = async (command, args) => {
      calls.push([command, ...args]);
      return { code, stdout, stderr };
    };
    return { calls, exec };
  };

  test("asks gh for a merged PR whose head is the branch", async () => {
    const { calls, exec } = fake(0, '[{"number":7}]');
    expect(await ghSquashMergeProbe(exec)("feature", "/repo")).toEqual({ merged: true });
    expect(calls[0]).toEqual(["gh", "pr", "list", "--state", "merged", "--head", "feature", "--json", "number", "--limit", "1"]);
  });

  test("an empty list is not merged", async () => {
    expect(await ghSquashMergeProbe(fake(0, "[]").exec)("feature", "/repo")).toEqual({ merged: false });
  });

  test("a gh that cannot run is unavailable, not a failure", async () => {
    expect(await ghSquashMergeProbe(fake(127, "", "spawn gh ENOENT").exec)("feature", "/repo")).toEqual({ unavailable: "spawn gh ENOENT" });
  });
});
