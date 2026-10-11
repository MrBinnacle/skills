import { describe, expect, test } from "bun:test";
import { mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, join } from "node:path";
import { extract, validateStructure } from "./packet";
import { verifyParked } from "./parked";
import { fixture, git, makeRemote, makeRepo, nodeExec, renderPacket } from "./testkit";
import { validatePacket } from "./validate";

const parkedPacket = (parked: unknown) => {
  const m = extract(fixture("fixture-clean.md"));
  m.parked = parked;
  return m;
};
const structureErrors = (parked: unknown) => {
  const m = parkedPacket(parked);
  return validateStructure(m, renderPacket(m));
};
const entry = (kind: string, ref: string) => ({ kind, ref, reason: "parked for later" });

describe("parked[] structure", () => {
  test("a packet without parked has no parked errors (the default packet is unchanged)", () => {
    expect(validateStructure(extract(fixture("fixture-clean.md")), fixture("fixture-clean.md"))).toEqual([]);
  });

  test("well-formed entries of every kind pass", () => {
    expect(structureErrors([
      entry("branch-exists", "wip"), entry("remote-branch-exists", "wip"),
      entry("stash-exists", "0123abc"), entry("worktree-exists", "../wt"),
    ])).toEqual([]);
  });

  test.each([
    ["not an array", "wip", "parked must be an array"],
    ["an unknown kind", [entry("tag-exists", "v1")], "parked[0].kind must be one of branch-exists, remote-branch-exists, stash-exists, worktree-exists"],
    ["no ref or reason", [{ kind: "branch-exists", ref: "", reason: "" }], "parked[0] lacks ref or reason"],
    ["a short stash ref", [entry("stash-exists", "abc")], "parked[0] stash-exists ref must be a stash commit SHA of at least 7 hex characters"],
  ])("%s is rejected", (_name, parked, expected) => {
    expect(structureErrors(parked)).toContain(expected);
  });

  test("a stash@{n} ref is rejected with the command that records a stable SHA", () => {
    const errors = structureErrors([entry("stash-exists", "stash@{0}")]);
    expect(errors.some((e) => e.startsWith("parked[0] stash-exists ref stash@{0} renumbers") && e.includes("git rev-parse stash@{0}"))).toBe(true);
  });
});

describe("verifyParked (real git repo)", () => {
  test("branch-exists holds for a local branch and fails for a missing one", async () => {
    const { root } = await makeRepo();
    await git(root, "branch", "wip");
    const result = await verifyParked({ data: parkedPacket([entry("branch-exists", "wip"), entry("branch-exists", "missing")]), repoRoot: root, exec: nodeExec });
    expect(result.errors).toEqual(["parked[1] branch-exists probe failed: missing (parked for later)"]);
  });

  test("remote-branch-exists checks origin; an unreachable origin is a note", async () => {
    const { root } = await makeRepo();
    await makeRemote(root);
    await git(root, "push", "-q", "origin", "main:wip");
    const ok = await verifyParked({ data: parkedPacket([entry("remote-branch-exists", "wip"), entry("remote-branch-exists", "nope")]), repoRoot: root, exec: nodeExec });
    expect(ok.errors).toEqual(["parked[1] remote-branch-exists probe failed: nope (parked for later)"]);

    const offline = (await makeRepo()).root;
    await git(offline, "remote", "add", "origin", join(tmpdir(), "session-packet-no-such-remote.git"));
    const result = await verifyParked({ data: parkedPacket([entry("remote-branch-exists", "wip")]), repoRoot: offline, exec: nodeExec });
    expect(result.errors).toEqual([]);
    expect(result.notes.some((n) => n.startsWith("parked[0] remote-branch-exists not verified: could not reach origin"))).toBe(true);
  });

  test("stash-exists matches a stash commit SHA prefix", async () => {
    const { root } = await makeRepo();
    writeFileSync(join(root, "README.md"), "stashed edit");
    await git(root, "stash", "push", "-q", "-m", "parked edit");
    const sha = await git(root, "rev-parse", "stash@{0}");
    const result = await verifyParked({ data: parkedPacket([entry("stash-exists", sha.slice(0, 10)), entry("stash-exists", "0000000")]), repoRoot: root, exec: nodeExec });
    expect(result.errors).toEqual(["parked[1] stash-exists probe failed: 0000000 (parked for later)"]);
  });

  test("worktree-exists resolves its path against the repository root", async () => {
    const { root } = await makeRepo();
    const name = `${basename(root)}-wt`;
    await git(root, "worktree", "add", "-q", "-b", "wt-branch", join("..", name));
    const result = await verifyParked({ data: parkedPacket([entry("worktree-exists", `../${name}`), entry("worktree-exists", "../nowhere")]), repoRoot: root, exec: nodeExec });
    expect(result.errors).toEqual(["parked[1] worktree-exists probe failed: ../nowhere (parked for later)"]);
  });

  test("receive mode rejects a packet whose parked entry no longer holds", async () => {
    const { root, head } = await makeRepo();
    const m = parkedPacket([entry("branch-exists", "deleted-meanwhile")]);
    m.repository = { ...(m.repository as Record<string, unknown>), root, head, branch: "main" };
    m.tests = [];
    mkdirSync(join(root, "packets"));
    const packetPath = join(root, "packets", "20260101T000000Z-aaaa.md");
    const text = renderPacket(m);
    writeFileSync(packetPath, text);
    const config = { dir: "packets", receiverChecks: [], trustedProbeCommands: [], wakeConditions: [] };
    const receipt = await validatePacket({ text, packetPath, mode: "receive", repoRoot: root, config, exec: nodeExec });
    expect(receipt.verdict).toBe("REJECTED");
    expect(receipt.errors).toEqual(["parked[0] branch-exists probe failed: deleted-meanwhile (parked for later)"]);
    expect((receipt as { packet_assertions_held?: boolean }).packet_assertions_held).toBe(false);
  });
});
