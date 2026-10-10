import { describe, expect, test } from "bun:test";
import { finalizeReview, newReviewId, renderReview, type Submission } from "./review";

const META = { model: "anthropic/claude-opus-5-5", base: "HEAD", head: "abc1234" };

function submission(n: number): Submission {
  return {
    status: "nominal",
    filesRead: ["src/a.ts"],
    findings: Array.from({ length: n }, (_, i) => ({
      severity: "major" as const,
      file: "src/a.ts",
      line: 10 + i,
      evidence: `line ${10 + i}: return x`,
      disposition: "fix-now" as const,
      reasoning: "Wrong value returned.",
      whatWouldChangeIt: "A caller that relies on it.",
    })),
  };
}

describe("finalizeReview", () => {
  test("finding ids are assigned by the extension and namespaced by review, so two reviews never collide", () => {
    const a = finalizeReview({ ...META, reviewId: newReviewId() }, submission(3));
    const b = finalizeReview({ ...META, reviewId: newReviewId() }, submission(3));
    const ids = [...a.findings, ...b.findings].map((f) => f.id);
    expect(new Set(ids).size).toBe(6);
    expect(a.findings[0].id.startsWith(a.reviewId)).toBe(true);
  });

  test("a reviewer that never submitted yields a blocked review with no findings, not an empty clean one", () => {
    const review = finalizeReview({ ...META, reviewId: "Rtest" }, undefined);
    expect(review.status).toBe("blocked");
    expect(review.statusReason).toContain("submit");
    expect(review.findings).toEqual([]);
  });

  test("a blocked review carries the diagnostics it was given, so the cause is visible", () => {
    const review = finalizeReview({ ...META, reviewId: "Rtest" }, undefined, "active tools: read, ls; last text: I cannot find the tool");
    expect(review.statusReason).toContain("active tools: read, ls");
  });
});

describe("renderReview", () => {
  test("the report shows every finding's id, severity, location and disposition, and the status line", () => {
    const review = finalizeReview({ ...META, reviewId: "Rtest" }, submission(2));
    const text = renderReview(review);
    for (const f of review.findings) expect(text).toContain(f.id);
    expect(text).toContain("src/a.ts:11");
    expect(text).toContain("fix-now");
    expect(text).toContain("status: nominal");
  });
});
