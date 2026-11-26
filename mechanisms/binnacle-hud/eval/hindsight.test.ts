import { describe, expect, test } from "bun:test";
import { agentWorth, verdict } from "./hindsight";

const shown = "<before>\n[Agent]: I merged PR #696 without running the full suite.\n</before>\n\n<note>\nThe suite never ran before the merge.\n</note>\n\n<after>\n[Tool result]: 3 failed on main after the merge\n</after>";
const reply = (t: string, n: string, c: string) => JSON.stringify({ true: { answer: true, quote: t }, new: { answer: true, quote: n }, consequential: { answer: true, quote: c } });

describe("verdict", () => {
  test("worth it when all three answers hold and every quote is in the record", () => {
    expect(verdict(reply("merged PR #696 without running", "merged PR #696 without running", "3 failed on main after the merge"), shown)?.worth).toBe(true);
  });
  test("a quote that is not in the record voids that answer", () => {
    expect(verdict(reply("merged PR #696 without running", "merged PR #696 without running", "the person reverted the merge"), shown)).toMatchObject({ worth: false, consequential: false });
  });
  test("the note itself is not the record", () => {
    expect(verdict(reply("suite never ran before the merge", "merged PR #696 without running", "3 failed on main after the merge"), shown)).toMatchObject({ worth: false, true: false });
  });
  test("a false answer or an unreadable reply is not worth it", () => {
    const o = JSON.parse(reply("merged PR #696 without running", "merged PR #696 without running", "3 failed on main after the merge"));
    o.new.answer = false;
    expect(verdict(JSON.stringify(o), shown)?.worth).toBe(false);
    expect(verdict("no json", shown)).toBeUndefined();
  });
});

test("agentWorth reads the main agent's verdict, with or without a suffix", () => {
  expect(agentWorth("right, new to the agent (acted)")).toBe(true);
  expect(agentWorth("right, the agent already had it")).toBe(false);
  expect(agentWorth("partly wrong")).toBe(false);
});
