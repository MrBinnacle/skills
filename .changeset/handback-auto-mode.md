---
"mrbinnacle-skills": patch
---

Two orchestration cards no longer say a false thing about how a subagent's report reaches its caller. `subagent-handback` Check 0 said a subagent's final text is always the return. In Claude Code's auto mode (v2.1.271 and later) the report travels through a `SubagentHandback` call, and the result carries only a note about it. Check 0 now says the route differs by harness and mode, and a new sibling file, `platform-notes.md`, records each Claude Code route, checked 2026-11-12 against Claude Code 2.1.323. It also marks two points unverified: whether the classifier alone can withhold a report, and what arrives when an auto-mode subagent ends without the call. `disposition-schema`'s `PROVIDER-ENVELOPE.md` said a subagent answering in plain text emits nothing the caller receives. It now says the report normally arrives, handbacks have still arrived empty, and auto mode changes the route.
