import { describe, expect, test } from "bun:test";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { DEFAULT_CHECK_COMMANDS, loadConfig } from "./config";

function project(configText?: string): string {
  const root = mkdtempSync(join(tmpdir(), "pi-env-config-"));
  if (configText !== undefined) {
    mkdirSync(join(root, ".pi"));
    writeFileSync(join(root, ".pi", "engineering-env.json"), configText);
  }
  return root;
}

describe("loadConfig", () => {
  test("a project without the file gets the default check commands", () => {
    const result = loadConfig(project());
    expect(result).toEqual({ ok: true, config: { checkCommands: DEFAULT_CHECK_COMMANDS } });
  });

  test("a project's checkCommands replace the defaults and sessionPacket passes through", () => {
    const result = loadConfig(project(JSON.stringify({
      checkCommands: ["\\bmake verify\\b"],
      sessionPacket: { dir: "packets" },
    })));
    expect(result).toEqual({
      ok: true,
      config: { checkCommands: ["\\bmake verify\\b"], sessionPacket: { dir: "packets" } },
    });
  });

  test("malformed JSON is an error naming the file, not a silent default", () => {
    const result = loadConfig(project("{ not json"));
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain("engineering-env.json");
  });

  test("a checkCommands entry that is not a valid regex is an error naming its index", () => {
    const result = loadConfig(project(JSON.stringify({ checkCommands: ["ok", "(unclosed"] })));
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error).toContain("checkCommands[1]");
  });

  test("checkCommands of the wrong type is an error", () => {
    expect(loadConfig(project(JSON.stringify({ checkCommands: "pytest" }))).ok).toBe(false);
    expect(loadConfig(project(JSON.stringify([1, 2]))).ok).toBe(false);
  });
});
