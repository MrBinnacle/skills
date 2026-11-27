import { expect, test } from "bun:test";
import { type Kit, Panel } from "./panel";
import { fold, type State } from "./state";

const kit: Kit = {
  truncateToWidth: (t, w, _e, pad) => (t.length > w ? t.slice(0, w) : pad ? t.padEnd(w) : t),
  wrapTextWithAnsi: (t, w) => t.match(new RegExp(`.{1,${w}}`, "g")) ?? [""],
};
const theme = { fg: (_: string, t: string) => t, bold: (t: string) => t };
const note = { key: "n1", tag: "heads-up" as const, line: "Skipped test " + "z".repeat(200), details: "**Why**", agentKnows: false, at: 1, how: "for you only" as const };
const panel = (state: Partial<State>) => new Panel(kit, theme, () => ({ ...fold([], []), ...state }));

test("every rendered line fits the width", () => {
  const p = panel({ draft: ["x".repeat(300)], notes: [note], log: [{ text: "y".repeat(300), at: 1 }] });
  for (const w of [30, 60, 120]) for (const l of p.render(w)) expect(l.length).toBe(w);
});
test("a long heads-up wraps inside the panel instead of being cut", () => {
  const text = panel({ notes: [note] }).render(40).join("").replace(/\s+/g, "");
  expect(text).toContain("z".repeat(200));
});
test("a closed heads-up leaves the panel", () => {
  const text = panel({ notes: [{ ...note, mark: "useful" }] }).render(60).join("");
  expect(text).not.toContain("Skipped test");
});
test("the panel takes no keys: it has no input handler", () => {
  expect("handleInput" in panel({})).toBe(false);
});
