import { describe, expect } from "bun:test";
import { mkdtempSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "./testkit";

const FIXTURE = join(import.meta.dir, "fixtures", "temp-lifecycle.fixture.ts");

/** Run the fixture with its own temp root, and return what it left there. */
function runFixture(extraEnv: Record<string, string>): { code: number; left: string[]; stderr: string } {
  const temp = mkdtempSync(join(tmpdir(), "temp-lifecycle-"));
  try {
    const run = Bun.spawnSync([process.execPath, "test", FIXTURE], {
      env: { ...process.env, TEMP: temp, TMP: temp, TMPDIR: temp, ...extraEnv },
    });
    return { code: run.exitCode, left: readdirSync(temp), stderr: run.stderr.toString() };
  } finally {
    rmSync(temp, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  }
}

describe("session-packet temp directories", () => {
  test("a passing run leaves none behind, read-only git objects included", () => {
    const { code, left, stderr } = runFixture({});
    expect({ code, stderr: code === 0 ? "" : stderr }).toEqual({ code: 0, stderr: "" });
    expect(left).toEqual([]);
  }, 60_000);

  test("a failing run keeps them and names them", () => {
    const { code, left, stderr } = runFixture({ TEMP_LIFECYCLE_FAIL: "1" });
    expect(code).toBe(1);
    expect(left.some((name) => name.startsWith("session-packet-remote-"))).toBe(true);
    expect(stderr).toContain("kept 2 temp directories");
  }, 60_000);

  test("a body that outlives its timeout keeps its repository, and the next test leaves it alone", () => {
    const { code, left, stderr } = runFixture({ TEMP_LIFECYCLE_TIMEOUT: "1" });
    expect(code).toBe(1);
    expect(left.filter((name) => name.startsWith("session-packet-"))).toHaveLength(1);
    expect(stderr).toContain("kept 1 temp directories");
  }, 60_000);
});
