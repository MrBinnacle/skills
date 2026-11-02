// Run only by temp-lifecycle.test.ts, in its own bun process.
import { expect } from "bun:test";
import { makeRemote, makeRepo, test } from "../testkit";

if (process.env.TEMP_LIFECYCLE_TIMEOUT) {
  test("times out, then makes a repository and returns", async () => {
    await Bun.sleep(300);
    await makeRepo();
  }, 100);

  test("passes while the timed-out body finishes", async () => {
    await Bun.sleep(6_000);
  }, 30_000);
} else {
  test("makes temp repositories, then passes or fails on request", async () => {
    const { root } = await makeRepo();
    await makeRemote(root);
    expect(process.env.TEMP_LIFECYCLE_FAIL).toBeUndefined();
  }, 30_000);

  test.each(["each"])("cleans up after an each-test as well: %s", async () => {
    await makeRepo();
  }, 30_000);

  test.skip("keeps bun's other test members", () => {});
}
