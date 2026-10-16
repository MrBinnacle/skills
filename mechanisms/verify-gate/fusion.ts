/** SoL-Pi local receipt v1. Unknown/malformed receipts never grant check credit. */
export interface FusionReceipt {
  version: 1;
  mutation: "succeeded";
  followUp: { command: string; status: "succeeded" | "failed" | "not-run" };
}
export function fusionReceipt(details: unknown): FusionReceipt | undefined {
  const r = (details as { solPiFusion?: FusionReceipt } | undefined)?.solPiFusion;
  return r?.version === 1 && r.mutation === "succeeded" &&
    typeof r.followUp?.command === "string" &&
    ["succeeded", "failed", "not-run"].includes(r.followUp.status) ? r : undefined;
}
