import { describe, expect, test } from "bun:test";
import { DEFAULT_DIR, parseSessionPacketConfig } from "./settings";

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
