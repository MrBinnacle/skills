# gotchas — pretooluse-prose (append-only)

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
  it. Both are on `pull-rebase`'s card as evidence.

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
  A private linter project's session state records: "CC Safety Net failed closed once on a long
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

- [OBSERVED 2026-08-24, recorded 2026-08-25] Three further blocks in one session of the
  private research repo (its S321), on three different guards, every one correct by its
  own rule and every one fired by prose rather than by the action the rule polices: a
  commit body describing a safe choice the session had made, a commit body containing
  the words "pull request", and a JSON payload containing a filename. All three recovered
  by this card's standing remedy — move the prose to a file and pass it by path. Recorded
  with a stated limit: the session's close packet preserved the prose classes that
  triggered each block but not the predicate names, so this entry counts the occasions
  without attributing them to specific rules. The recording itself was late: the session
  that observed the blocks closed without writing this entry, and the debt was carried in
  its close packet as an owed row. A card whose admission rests on counted recurrence is
  undercounted exactly when its author is busiest, which is when the guards fire most.

- [OBSERVED 2026-09-08] Five blocks in one working day across two repositories, all from a
  guard in **this collection's own preventive half** — `guard-git-pull-rebase.py`, the hook the
  `pull-rebase` card prescribes, and the same guard the 2026-08-23 entry above already counted
  twice. Three were observed first-hand by an agent whose entire task was to write about the
  trap that guard polices: it was authoring a findings document and a task fixture for a
  measurement of that very card, so every artifact it produced had to quote the hazard action.
  Two more were reported the same day by a peer agent in the same session, one on a
  pull-request body that merely mentioned an installer command; that pair is counted but its
  predicates were not preserved, and the limit is stated rather than smoothed over.

  The three first-hand blocks, in the order they fired:

  1. A `python -c` payload whose Python **string literal** carried the card's operative rule.
  2. The same payload with the token deliberately **split** as `'git ' + 'pull'` — which still
     blocked.
  3. A `git commit -F -` **heredoc body** quoting the card's own `description`.

  The third is this card's canonical shape and needs no elaboration. **The second is why this
  entry exists: the author's obvious workaround fails.** The predicate is

      PULL_INVOCATION = re.compile(r"(?<![\w-])git\s+[^|;&\n]*?(?<![\w-])pull(?![\w.-])")

  and its gap `[^|;&\n]*?` spans any run of characters short of a command separator, so
  `'git ' + 'pull'` reads as an invocation with `'+'` sitting in the middle. **Splitting a
  token defeats a literal scan; it does not defeat a gapped one.** Anyone who reaches for that
  trick after a false block concludes the guard is unpredictable rather than over-broad, which
  is a worse end state than the block itself.

  What makes this more than a sixth restatement: **the guard had already been narrowed for
  this exact family and still had the gap.** Its header records an earlier over-block — the
  bare identifier `git-pull-rebase-trap` inside a PATH, "Observed live twice" — fixed by
  anchoring both words so a hyphenated identifier no longer matches. It also documents
  `git log --grep="pull"` as a knowing, deliberate false positive, on the reasoning that "a
  false block costs one re-issue; a false PASS costs every local SHA". That trade is sound and
  this entry does not ask to loosen it. The point is narrower, and it is the same one the
  2026-08-24 entry made about a fix wired to one caller instead of the class:
  **command-position anchoring was added to this guard and heredoc stripping never was.** The
  commit-message block is a gap this card's standing remedy closes without touching anything
  the guard deliberately keeps.

  One correction to the cost model, offered because the guard's own comment states it. A false
  block does **not** cost one re-issue when the subject of the work *is* the trap. It recurs on
  every artifact the session produces — the script that checks the rule, the commit that
  explains the check, the record that reports it — because each must quote the hazard to say
  anything true about it. The 2026-08-23 entry already observed that the cost lands on whoever
  documents the trap; this occurrence measures how it scales, which is per artifact and not per
  incident.

  Recovered all three times by this card's standing remedy: write the payload to a file and
  pass it by path (`python script.py`, `git commit -F msg.txt`). Recorded the same day, by the
  session that was blocked — which is the debt the entry above says goes unpaid.

- [OBSERVED 2026-09-08] **The first occurrence that is not prose at all**, from the same guard
  as the entry above, found within the hour by a second agent trying to check out the pull
  request that carried that entry:

      git fetch origin pull/292/head:pr292

  blocked. Nothing here is text about the trap. `pull` is a path segment in
  `refs/pull/<n>/head`, GitHub's standard namespace for a pull-request ref, and the predicate's
  gap swallows `fetch origin ` on the way to it. Verified by importing the guard's own
  `targets_bare_pull` and running it over a case table: both `pull/292/head:pr292` and the
  fully-qualified `refs/pull/292/head` return True, while `git fetch origin main`,
  `git push origin main` and both explicit-intent pulls return False and a genuine bare pull
  still returns True. **So the guard blocks fetching any pull request by ref, in any repository
  whose effective config arms it, whatever the pull request contains.**

  Two things this changes.

  **The blast radius is not confined to authoring.** Every entry before this one says that
  writing about a trap is how you trip its guard, and that the cost lands on whoever documents
  it. This one costs a routine review workflow — fetching a PR to reproduce a failure — with no
  prose involved and nobody documenting anything.

  **The guard refuses a form of its own prescribed remedy.** The `pull-rebase` card's remedy is
  `git fetch` and then `git merge --no-ff`. Here a `git fetch` is blocked over its refspec. The
  2026-08-23 entry recorded the general version of this and acted on it — "a guard that refuses
  its own prescribed remedy trains you to route around it", which is why the `-L` remedy
  detector was loosened in that pass. The same reasoning applies and has not been applied here.

  **Scope, stated rather than assumed.** This is not an instance of the card's *prose* framing,
  and it is counted anyway. The card's general rule — a predicate that decides whether
  something will RUN must read command structure, not text — covers it exactly: `pull` is a
  path segment here, not a subcommand, and only a predicate that never looks at command
  position can confuse the two. Whether the card's headline framing should widen from "prose"
  to "anything that is not the command in command position" is a card-text question this record
  does not decide.

  **The fix is already built next door.** Anchoring the token to the start of a simple command
  fixes the prose cases and this one together, since `pull` sits in subcommand position in
  neither. The sibling measurement repository solved this same class on 2026-09-08 for its own
  hazard counter: segment a command string into simple commands on unquoted `&&`, `||`, `;`,
  `|` and newlines, normalise each through `shlex`, and match against that, so a `^` in a
  registered pattern means "this command IS the hazard" (`MrBinnacle/skill-harness#438`, merged
  as `1a5027a`). That is the remedy this card has prescribed since 2026-08-23, now with a
  worked implementation to copy. This guard has not adopted it.

  **Not a falsifier**, for the same reason as the entry above: command-position anchoring was
  never applied to this guard, so the remedy is absent rather than defeated.
