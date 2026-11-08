import { describe, expect, test } from "bun:test";
// @ts-expect-error plain ESM script with no type declarations
import { parse, render } from "./render-demo.mjs";

const OUTPUT = [
  "verify-gate demo: Pi 1.5.0's real agent loop, edit and bash tools, scripted model replies.",
  "",
  "Run 1: verify-gate not loaded",
  "  user  | Give every order a 10% discount.",
  "  agent | Done. Every order now gets a 10% discount.",
  "  The run settled after 2 model calls and 0 checks.",
  "  The demo now runs the project's tests itself: FAIL. The bug would have shipped.",
  "",
  "Run 2: verify-gate loaded from mechanisms/verify-gate/, same script",
  "  gate  | Verification gate: these files changed after the last check command in this run: price.mjs.",
  "  tool  | bash FAILED",
  "  agent | I ran npm test and it failed, so the discount is not done:",
  "        |   actual: 10,",
  "  The run settled after 4 model calls. The gate sent the agent back to check.",
  "",
  "Real: Pi's agent loop, its edit and bash tools, npm test, and the verify-gate extension as shipped.",
  "Scripted: the model's replies. The last one reads the real test output from the transcript.",
  "Guard: mechanisms/verify-gate/ (gate.ts holds the rule). Took 2.5s.",
].join("\n");

describe("render-demo", () => {
  test("parses both runs, keeps continuation lines, drops the timing line", () => {
    const { runs, tail } = parse(OUTPUT);
    expect(runs.map((r: { rows: unknown[] }) => r.rows.length)).toEqual([2, 3]);
    expect(runs[1].rows[2].lines).toEqual(["I ran npm test and it failed, so the discount is not done:", "  actual: 10,"]);
    expect(tail).toHaveLength(2);
    expect(render(OUTPUT)).not.toContain("Took");
  });

  test("the picture changes when the demo's output changes", () => {
    expect(render(OUTPUT.replace("bash FAILED", "bash ok"))).not.toBe(render(OUTPUT));
  });

  test("refuses output that is missing a run", () => {
    expect(() => parse(OUTPUT.replace(/Run 2:[\s\S]*?(?=Real:)/, ""))).toThrow("expected shape");
  });

  test("escapes XML in demo text", () => {
    expect(render(OUTPUT.replace("10% discount.", "a < b & c"))).toContain("a &lt; b &amp; c");
  });

  test("the picture is well-formed XML: every tag parses and every open tag closes", () => {
    expect(xmlProblem(render(OUTPUT))).toBe("");
    expect(xmlProblem('<svg><filter id="a"x="0"/></svg>')).not.toBe("");
    expect(xmlProblem("<svg><g></svg>")).not.toBe("");
    expect(xmlProblem("<svg>a & b</svg>")).not.toBe("");
  });
});

// A strict scan of the subset of XML the renderer writes: tags with quoted attributes, escaped
// text, and one <style> block. Returns "" when the document is well-formed.
function xmlProblem(svg: string): string {
  const open: string[] = [];
  const body = svg.replace(/<style>[\s\S]*?<\/style>/g, "<style/>");
  for (const [, tag, text] of body.matchAll(/(<[^>]*>)|([^<]+)/g)) {
    if (text !== undefined) {
      if (/&(?!(amp|lt|gt|quot|apos);)/.test(text) || text.includes(">")) return `bad text: ${text.slice(0, 40)}`;
      continue;
    }
    const close = tag.match(/^<\/([\w:-]+)>$/);
    if (close) {
      if (open.pop() !== close[1]) return `mismatched </${close[1]}>`;
      continue;
    }
    const m = tag.match(/^<([\w:-]+)((?:\s+[\w:-]+="[^"<]*")*)\s*(\/?)>$/);
    if (!m) return `bad tag: ${tag.slice(0, 60)}`;
    if (!m[3]) open.push(m[1]);
  }
  return open.length ? `unclosed <${open.at(-1)}>` : "";
}
