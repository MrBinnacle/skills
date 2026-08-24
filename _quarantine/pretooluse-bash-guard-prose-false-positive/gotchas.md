# gotchas — pretooluse-bash-guard-prose-false-positive (append-only)

- [OBSERVED 2026-08-23] Three reproductions in a single rotation pass, on two different
  guards, none of them a defect in the guarded behaviour.

  **On a corpus-search guard.** A `PreToolUse` hook refuses a bare `find` over a
  symlinked skills corpus, because an unfollowed symlink silently undercounts it. The
  block fired on `gh pr create --body-file - <<EOF ...`, where the heredoc body was
  English prose containing the sentence fragment "The one find, and why it does not move
  a count". No filesystem search was being run. The guard scans the whole command string,
  the heredoc body is part of that string, and a common English verb is its trigger token.
  Worked around by rewording the prose to "The one hit".

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

  **What would change the disposition:** a guard whose trigger token is common enough that
  prose hits it repeatedly in one session. `find` is at that boundary. The narrower fix is
  to anchor the predicate to command position rather than to substring presence, so a token
  inside a quoted heredoc body cannot match. That is a real change to the hook, not to the
  card, and it is not made here.
