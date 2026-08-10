---
"mrbinnacle-skills": patch
---

Run the session-boundary validator suites in CI. Two skills in this collection ship
executable code and the collection had no job that executed it — only the link check and
the de-personalization gate.

The job invokes each suite through its real entrypoint rather than through `pytest`, and
that is the point of it. The cases run from `if __name__ == "__main__"` and the functions
carry no `test_` prefix, so `pytest` collects nothing from either file and reports
"no tests ran" — a green line that means the opposite of what it looks like. The job
asserts each suite's `PASS:` line so a suite that does not execute cannot report success,
and a poison control asserts the shipped validator still rejects a stale packet, because a
gate that cannot fail guards nothing. Both skills record the `pytest` false-green in their
gotchas. Runs on Linux and Windows, the platform the pair is actually used on.
