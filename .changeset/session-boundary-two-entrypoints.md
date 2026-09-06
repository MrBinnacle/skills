---
"mrbinnacle-skills": patch
---

`im-down` and `im-up`: one public entrypoint each, so the close and open sequences cannot be reordered by the caller.

The close previously took two commands the agent had to sequence: write durable state, then snapshot the packet. Reversed, the packet records a pre-commit `HEAD` and the next open rejects it as stale. `close_session.py` now performs all three stages in one process — write state, commit with the `close_commit` marker, snapshot at the post-commit `HEAD` — and fails if `HEAD` moves between the commit and the snapshot. `open_session.py` is the matching receive action: validate the packet, load the declared `state_file`, and emit one receipt carrying `state_read` evidence. A packet whose state file is missing is rejected rather than accepted without doctrine.

`snapshot_state.py` remains published and is now named in `im-down/SKILL.md`. It writes the packet scaffold alone, for a project whose close commits a caller-authored message or decides by judgement what enters the commit. That caller owns the ordering assertion `close_session.py` makes internally.

Band rotation is stated as out of scope on the close card. No surface in this repository enforces it.
