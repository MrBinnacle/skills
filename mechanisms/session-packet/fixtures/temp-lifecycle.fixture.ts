// Run only by temp-lifecycle.test.ts, in its own bun process.
import { expect } from "bun:test";
import { makeRemote, makeRepo, test } from "../testkit";

test("makes temp repositories, then passes or fails on request", async () => {
  const { root } = await makeRepo();
  await makeRemote(root);
  expect(process.env.TEMP_LIFECYCLE_FAIL).toBeUndefined();
}, 30_000);

test.each(["each"])("cleans up after an each-test as well: %s", async () => {
  await makeRepo();
}, 30_000);
