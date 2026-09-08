# gotchas — uniform-eol

Append-only. Never rewrite or delete an entry; add a new one naming the earlier.

## [OBSERVED 2026-09-06] The commit succeeded, every assertion passed, and the diff was still wrong

A script applied six exact-string replacements to a 788-line `AGENTS.md`. Each replacement asserted its pattern occurred exactly once, and each assertion passed. The script printed `OK: 6 amendments applied`. The pre-commit hooks passed. The commit succeeded.

The diffstat read `810 insertions(+), 788 deletions(-)`.

Everything that could report success did report success. The only signal that anything was wrong was a number in the diffstat that did not match the size of the intended edit. Nothing prompted a look at it; noticing was discretionary.

## [OBSERVED 2026-09-06] The installed mixed-EOL guard passed this, for two independent reasons

A `PostToolUse` guard on `Write|Edit|Bash` was installed and wired, with a self-test in the session's own receiver checks. It did not fire.

Reason one, and the general one: its predicate was `crlf > 0 and lone_lf > 0`. After a whole-file conversion the counts were `crlf = 789, lone_lf = 0`. Not mixed. The guard is built to catch a stray separator landing in a file, and a uniform conversion is not that.

Reason two, and the local one: the guard's root was `Path(__file__).resolve().parent.parent.parent` — the session's own project directory. The write went into a sibling repository by absolute path, so `relative_to_repo()` returned `None` and the file was never a candidate.

Either reason alone would have been enough. Both were true at once, which is why nothing in the environment noticed.

## [OBSERVED 2026-09-06] `read_text` then `write_text` is the round trip that does it

The conversion is not caused by anything exotic. `read_text()` opens with `newline=None`, which gives universal newlines, so the string in memory holds `\n` regardless of what the file held. `write_text()` also defaults to `newline=None`, which translates every `\n` to `os.linesep` on write. On Windows that is `\r\n`.

So the most ordinary read-modify-write in Python converts a whole LF file on Windows, silently, with no error and no warning, and it does so *correctly* by the documented contract. There is no bug to report.

## [ANTICIPATED] `newline=""` and `write_bytes` are not equivalent in every case

`write_bytes(t.encode("utf-8"))` writes exactly the bytes you encoded. `write_text(t, encoding="utf-8", newline="")` disables translation but still goes through text mode. They agree for this purpose. They diverge if the string already contains `\r\n` — neither will normalise it, so a string assembled from mixed sources stays mixed either way. Normalising the string is a separate step and this skill does not do it.

## [ANTICIPATED] A repository without `.gitattributes` will keep producing this

Commit-time normalisation via `* text=auto eol=lf` stops the converted bytes reaching git. Without it, every scripted edit on Windows is a candidate. Adding it is worth doing and does not retire the diffstat check: it fixes what git stores while leaving the working tree converted, and it does nothing for a repository you do not control.

## [ANTICIPATED] The repair is `--amend`, and that is only safe before a push

The fix rewrites the commit. If the branch has already been pushed and anyone has fetched it, amending forces a divergence. Check whether the branch is pushed before reaching for `--amend`; after a push, a follow-up commit that restores the endings is the honest repair even though the history keeps the noisy commit.

## [OBSERVED 2026-09-07] The same conversion, with no diff to notice it in

A session auditing evidence pointers extracted 19 URLs, wrote them one per line with
`open(path, "w")`, then read the file back in a shell loop and fetched each with `curl`.

Every fetch returned `000`. Not 404, not 403 — no connection at all, on all 19, including
`https://arxiv.org/abs/2410.06992`, which is not a plausible outage.

The write had converted each LF to CRLF. The shell's `read` strips the newline and leaves the
carriage return, so every URL carried a trailing CR and `curl` tried to resolve a hostname that
did not exist. The character is invisible in terminal output, and the failure presented exactly
like a network outage or a repository that had gone private.

**What this adds to the 2026-09-06 record.** That one establishes the conversion corrupts a
commit, and its stated diagnostic is to read `git diff --numstat` before committing what a script
wrote. This one had no commit and no diff: the file was scratch, never staged, so no diffstat
existed and no EOL guard had a write to inspect. The only symptom was a downstream tool failing
for a reason it could not report.

So the card's diagnostic is necessary and not sufficient. It catches the conversion when the file
reaches git. It cannot catch the conversion in data in flight, where a trailing CR on a URL, a
hostname, a token or a path fails silently at whatever consumes it.

**The general rule is the write, not the diff.** On Windows, use `write_bytes`, or pass an explicit
`newline` to `open`, for any file whose bytes another program will parse. Reading the diffstat is
the backstop for the case where you forgot.

**The diagnostic that resolved it** was a control, not a theory: fetch one of the same URLs typed
directly into the command, outside the loop. It returned 200, which separated the apparatus from
the subject in a single call. A zero-cost failure across every item of a batch is an apparatus
fault until a control says otherwise. The repair was to strip the carriage returns and re-run.

**While writing this entry the same class of bug recurred, and it is worth stating because it
shows how narrow the safe path is.** The first attempt at this append passed the entry through a
shell heredoc; the escaping collapsed one level and wrote four real CR bytes into the prose that
describes CR bytes. The diffstat did not show it — the append was a clean 36 insertions, 0
deletions — because a stray CR inside a line is not a line-ending change. A byte count found it.
The fix was to stop passing prose through shell escaping layers and write the text as a file.
That third instance is a symptom of this same occasion, not a separate one, and is not counted
as one.
