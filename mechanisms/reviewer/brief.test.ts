import { describe, expect, test } from "bun:test";
import { buildBrief } from "./brief";

const BASE_INPUT = {
  task: "Make parseDate accept ISO week dates.",
  base: "HEAD",
  head: "abc1234",
  diff: "diff --git a/src/date.ts b/src/date.ts\n+export const x = 1;\n",
  untracked: [] as string[],
};

describe("buildBrief", () => {
  test("carries the task and the diff verbatim, with the revision", () => {
    const brief = buildBrief(BASE_INPUT);
    expect(brief).toContain(BASE_INPUT.task);
    expect(brief).toContain(BASE_INPUT.diff);
    expect(brief).toContain("abc1234");
  });

  test("states the reviewer's authority: recommend, not change scope or files", () => {
    const brief = buildBrief(BASE_INPUT);
    expect(brief).toMatch(/recommend/i);
    expect(brief).toMatch(/not (change|edit)/i);
  });

  test("lists untracked files, which a git diff omits, so the reviewer can read them", () => {
    const brief = buildBrief({ ...BASE_INPUT, untracked: ["src/new.ts"] });
    expect(brief).toContain("src/new.ts");
  });

  test("a diff over the cap is cut with an explicit notice naming the cut, never silently", () => {
    const diff = "x".repeat(500);
    const brief = buildBrief({ ...BASE_INPUT, diff, maxDiffChars: 100 });
    expect(brief).not.toContain(diff);
    expect(brief).toMatch(/truncated/i);
    expect(brief).toContain("400");
  });

  test("caller context is included verbatim when given, and absent otherwise", () => {
    expect(buildBrief({ ...BASE_INPUT, context: "Prior advice: keep the old signature." })).toContain(
      "Prior advice: keep the old signature.",
    );
    expect(buildBrief(BASE_INPUT)).not.toContain("Caller context");
  });
});
