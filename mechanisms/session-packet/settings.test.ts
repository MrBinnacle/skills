import { describe, expect, test } from "bun:test";
import { DEFAULT_DIR, DEFAULT_STORE_WORKTREE, parseSessionPacketConfig } from "./settings";

describe("parseSessionPacketConfig", () => {
  test("an absent section yields the defaults", () => {
    expect(parseSessionPacketConfig(undefined)).toEqual({
      ok: true,
      config: { dir: DEFAULT_DIR, receiverChecks: [], trustedProbeCommands: [], wakeConditions: [] },
    });
  });

  test("a full section parses, and an unnamed check is named by its command", () => {
    const result = parseSessionPacketConfig({
      dir: "packets",
      receiverChecks: [{ name: "clean-tree", command: "git diff --quiet" }, { command: "true" }],
      trustedProbeCommands: ["bun test"],
      closeCommit: { contains: "RITUAL:" },
      wakeConditions: ["A claim fails."],
    });
    expect(result).toEqual({
      ok: true,
      config: {
        dir: "packets",
        receiverChecks: [{ name: "clean-tree", command: "git diff --quiet" }, { name: "true", command: "true" }],
        trustedProbeCommands: ["bun test"],
        closeCommit: { contains: "RITUAL:" },
        wakeConditions: ["A claim fails."],
      },
    });
  });

  test.each([
    [{ dir: 3 }, "sessionPacket.dir"],
    [{ receiverChecks: [{ name: "x" }] }, "sessionPacket.receiverChecks[0].command"],
    [{ trustedProbeCommands: "bun test" }, "sessionPacket.trustedProbeCommands"],
    [{ closeCommit: { contains: "" } }, "sessionPacket.closeCommit.contains"],
    [{ wakeConditions: [1] }, "sessionPacket.wakeConditions"],
  ])("malformed %j is an error naming the key", (raw, key) => {
    const result = parseSessionPacketConfig(raw);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain(key);
  });
});

describe("parseSessionPacketConfig opt-in keys", () => {
  test("headPolicy, chain and a branch store parse; the store worktree defaults", () => {
    const result = parseSessionPacketConfig({ headPolicy: "ancestor", chain: true, store: { kind: "branch", ref: "session-log" } });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.config.headPolicy).toBe("ancestor");
    expect(result.config.chain).toBe(true);
    expect(result.config.store).toEqual({ kind: "branch", ref: "session-log", worktree: DEFAULT_STORE_WORKTREE });
    expect(DEFAULT_STORE_WORKTREE).toBe("var/session-log-worktree");
  });

  test("an explicit dir store and an explicit worktree parse as written", () => {
    const dir = parseSessionPacketConfig({ headPolicy: "exact", store: { kind: "dir" } });
    expect(dir.ok && dir.config.store).toEqual({ kind: "dir" });
    const branch = parseSessionPacketConfig({ store: { kind: "branch", ref: "log", worktree: "../log-wt" } });
    expect(branch.ok && branch.config.store).toEqual({ kind: "branch", ref: "log", worktree: "../log-wt" });
  });

  test.each([
    [{ headPolicy: "loose" }, "sessionPacket.headPolicy"],
    [{ chain: "yes" }, "sessionPacket.chain"],
    [{ store: "branch" }, "sessionPacket.store"],
    [{ store: { kind: "git" } }, "sessionPacket.store.kind"],
    [{ store: { kind: "branch" } }, "sessionPacket.store.ref"],
    [{ store: { kind: "branch", ref: "x", worktree: "" } }, "sessionPacket.store.worktree"],
  ])("malformed %j is an error naming the key", (raw, key) => {
    const result = parseSessionPacketConfig(raw);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain(key);
  });
});
