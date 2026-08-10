# Evidence

- **Status:** UNMEASURED.
- **Origin:** A production repository used a receiver ritual that loaded canonical state, emitted a hash-stamped read contract, and rejected false handoff claims.
- **Observed failure:** A prior session asserted a wrong file location, hook predicate, or sequence. The receiver caught the conflict against repository truth.
- **Validated against:** a personal production project's `resume` ritual skill, read in full on 2026-08-09 (private repo; commit pinned in the source tree).
- **Controlled result:** Not run.
- **Re-screen trigger:** Claude Code provides a native, project-configurable, repository-verified resume contract with typed claim probes.
- **Fixture classes:** RUN and passing on 2026-08-10 — nine classes, not the four this record first named (clean, stale, incomplete, failed-probe, placeholder, unfailable-check, command-probe, receive-mode-config, no-drift). Executed by CI on Linux and Windows from this date. This half of the blocker is discharged.
- **Promotion blocker:** One real producer-to-receiver cutover. Not yet run.
