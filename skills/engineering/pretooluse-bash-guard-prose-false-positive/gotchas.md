# gotchas — pretooluse-bash-guard-prose-false-positive (append-only)

- [OBSERVED 2026-08-23] Four reproductions in a single rotation pass, on two different
  guards, none of them a defect in the guarded behaviour.

  **On a corpus-search guard.** A `PreToolUse` hook refuses a bare `find` over a
  symlinked skills corpus, because an unfollowed symlink silently undercounts it. The
  block fired on `gh pr create --body-file - <<EOF ...`, where the heredoc body was
  English prose containing the sentence fragment "The one find, and why it does not move
  a count". No filesystem search was being run. The guard scans the whole command string,
  the heredoc body is part of that string, and a common English verb is its trigger token.
  Worked around by rewording the prose to "The one hit".

  **The same guard again, forty minutes later.** A commit message describing the sweep
  contained "a signature that cannot find the occurrence we know happened". Worked around by
  writing the message to a file and passing `-F <path>`, which keeps the prose out of the
  command string entirely.

  **Correction, same day:** an earlier version of this entry claimed the predicate was a bare
  substring match and that every inflection tripped it — `find`, `finds`, `finding`,
  `findings`. **That was wrong, and it was asserted without testing.** The predicate was
  `\bfind\b`, which is word-bounded: "finding", "findings" and "finds" never matched. Both
  collisions were the bare verb `find`. Verified by running the pattern against all four
  spellings. The claim is corrected rather than deleted because a wrong correction to an
  evidence-first record is worse than the original error, and because the shape of the mistake
  is the card's own: a plausible mechanism asserted from a block message instead of read off
  the predicate.

  **On a rebase guard, twice, recorded the previous session** — once on a verification
  `grep` whose argument named the trap, and once on a commit message whose body explained
  it. Both are on `git-pull-rebase-trap`'s card as evidence.

  **The pattern across all three: writing ABOUT a trap is how you trip its guard.** The
  documents most likely to name a failure mode are the commit message, the pull-request
  body and the card that documents it, and those are exactly the artifacts a guard's
  substring match cannot distinguish from an attempt to commit the failure. A collection
  whose product is trap documentation will hit this more than most, and the cost lands on
  the person doing the recording.

  **The asymmetry that makes this worth living with.** A false positive costs one reword.
  A false negative costs the incident the guard exists to prevent. So the disposition is
  not "loosen the predicate" — it is to keep the block, and to make the message say which
  token matched, so the reword is obvious in one read rather than a guessing game. All
  three of these messages did name the trigger, which is why each cost seconds.

  **[RESOLVED 2026-08-23] The predicate was fixed rather than tolerated.** Two changes to the
  hook, both proven on the verbatim commands that were blocked:

  1. **Heredoc payloads are stripped before the predicate runs.** A heredoc body is data — a
     commit message, a PR body, a file being authored — and no rule about *running* a program
     should read it. The introducing line is kept, so rules that legitimately care about
     `<<'EOF' > notes.md` still see it.
  2. **The token must sit in command position**: start of string, after `;` `|` `&` `&&` `||`
     `(` `{` a newline or a command substitution, optionally after env assignments or a
     wrapper like `xargs` / `env` / `time`. Substring presence is the wrong test for any rule
     about execution, because the word appears in commit messages, PR bodies, documentation,
     and the guard's own block text.

  Verified as a before/after pair on the same two inputs: both previously-blocked commands now
  pass, while a bare `find` over the corpus, a `cd <corpus> && find .`, a `find` after a pipe,
  after an env assignment, and under `xargs` all still block. Eight fixtures added, including
  both prose bodies verbatim. Suite 97/97.

  The `-L` remedy detector was loosened in the same change, because it accepted only one
  spelling and a guard that refuses its own prescribed remedy trains you to route around it.

  **The general rule this leaves behind:** a predicate that decides whether something will
  RUN must read command structure, not text. Every guard in a rule set is worth auditing on
  that question, because the false positives land hardest on whoever is documenting the trap.

  **The mitigation is still worth preferring by default:** write long prose to a file and pass
  it by path (`git commit -F msg.txt`, `gh pr create --body-file body.md`). No guard sees the
  prose, and the artifact is reviewable before it ships.

- [OBSERVED on or about 2026-08-18, harvested 2026-08-24] Independent occurrence in a third
  project and on a third guard, found by a corpus sweep and verified by reading the source.
  `workspace_lint`'s session state records: "CC Safety Net failed closed once on a long
  `gh issue create` heredoc — write the body to the scratchpad and pass `--body-file`."
  Different project, different guard family (a rulebook plugin, not a hand-authored hook),
  same failure class — a PreToolUse Bash guard refusing a legitimate heredoc-carrying
  command — and the recorded workaround is this card's own prescribed remedy verbatim.
  Two hedges stated rather than smoothed over: the source line attributes the block to the
  heredoc's *length* and never names the predicate that fired, and the entry itself is
  undated inside a checkpoint band written on or about 2026-08-18/19. What is certain is
  the failed-closed block of a legitimate command and the `--body-file` recovery.

- [OBSERVED 2026-08-24] Two further reproductions during this collection's own maintenance
  passes (the private research repo's S312, fixed the same day in S313), both on the
  read-whole guard rule this card's 2026-08-23 entry did not cover: Python locals named `head` and `tail` inside a
  `python - <<'EOF'` script read as pager commands (a `.md` path in the segment supplied
  the operand), and then the commit describing that block was itself blocked because the
  prose contains the words. Fixed the same day at the class level: the rule now reads the
  heredoc-stripped command, proven by poison fixtures that reproduce both real incidents
  RED before the fix and pass after it, with the real pager invocation still blocking.
  The 2026-08-23 entry's own closing rule ("a predicate that decides whether something
  will RUN must read command structure, not text") predicted exactly this collision; the
  fix had been wired to one caller, not the class.
