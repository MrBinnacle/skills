const L = { none: "Watching", looking: "Observer reading", rechecking: "Rereading later turns", shown: "Note on the panel", read: "Note opened", sent: "Sent to the agent", closed: "Marked and closed", dropped: "Dropped: already fixed" };
export const title = "A Binnacle heads-up, from look to close";
export const state = (v) => ({ Problem: v.fact === "open" ? "Problem open" : "Agent fixed it", Note: L[v.note] });
export const step = (a) => ({ AgentSettles: "the agent fixes it", AgentWorks: "the agent works on", ObserverLooks: "the observer looks", ReplyQuiet: "the reply arrives", ReplyMoved: "the agent moved on [read the new turns]", RecheckSettled: "the new turns fixed it", RecheckHolds: "it still holds", PersonOpens: "you open it", PersonSends: "you send it", PersonMarks: "you mark it", Done: null })[a] ?? a;
export const group = (v) => (["sent", "closed", "dropped"].includes(v.note) ? "end" : v.note === "none" ? "idle" : "live");
export const colors = { end: "teal", idle: "tan", live: "yellow" };
