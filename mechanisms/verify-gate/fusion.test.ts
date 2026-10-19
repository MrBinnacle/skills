import { expect, test } from "bun:test";
import { createGate } from "./gate";
import { fusionReceipt } from "./fusion";

for (const status of ["succeeded", "failed", "not-run"] as const) {
  test(`fused ${status} follow-up settles only a successful check`, () => {
    const gate = createGate(["^bun test$"]);
    gate.runStarted();
    gate.toolFinished("bash", { command: "bun test" }, status !== "succeeded");
    gate.toolFinished("write", { path: "a.ts" }, status !== "succeeded", {
      solPiFusion: { version: 1, mutation: "succeeded", followUp: { command: "bun test", status } },
    });
    expect(gate.beforeSettle("completed") === undefined).toBe(status === "succeeded");
  });
}
test("unknown or malformed receipts do not establish mutation or check success", () => {
  for (const details of [null, {}, { solPiFusion: {} }, { solPiFusion: { version: 2 } },
    { solPiFusion: { version: 1, mutation: "succeeded", followUp: { command: "bun test", status: "unknown" } } }]) {
    expect(fusionReceipt(details)).toBeUndefined();
  }
});
