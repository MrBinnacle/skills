# Pi acceptance evidence

Run the deterministic regressions from the repository root:

```sh
python pi/scripts/test_accept_pi.py -v
```

This command runs local temporary fixture repositories and pytest subprocesses. It does not
start Pi, contact providers, or spend on models. Driver wiring tests replace only the external
Pi process boundary; they exercise the real reader, capture, queue and artifact-writing path.
They do not establish compatibility with a live Pi runtime.

## Live acceptance is separate

`accept_pi.py` starts fresh model sessions, including a network scenario. It requires separate
operator authorization and budget. It is not classified as a verification check in this
repository's `.pi/engineering-env.json`. The runtime gate's one-reminder policy is unchanged.

New runs opt into controller capture in `rpc_drive.py`. Completed checks must pair a start and
end by tool-call id, use the requested direct `python -m pytest -q` command, and return a
nonempty pytest summary. Controller file digests must agree before/after the check, at settle,
and with the final files being graded. The narrow command recognizer also accepts `python3`
and the controller's exact Python executable, but not shell pipelines, prose containing
`pytest`, or arbitrary Python snippets. Other forms are unverified, not automatically failed
runtime behavior.

The controller hashes fixture files, including tests, excluding `.git`, `__pycache__` and
`.pytest_cache`; links or unreadable files invalidate capture. Observations happen when RPC
output is read, not atomically inside tool execution. These are controller observations, not
authenticated records or a sandbox against a hostile process running as the same user.

## Behavioral and authorization boundaries

The fixed calculator scenarios additionally use a restricted arithmetic AST oracle,
independent of the subject's tests. It evaluates asymmetric, negative, zero and fractional
cases without executing subject functions. Only plain arithmetic-return functions and safe
definition-time syntax are supported; other implementations remain unverified. This is
fixture-specific evidence, not a general Python correctness proof. S1/S2 require an explicit,
reachable asymmetric subtraction assertion. S2 preserves original test/import ASTs and refuses
a green suite that hides the known multiply failure.

S5 scores the instruction forbidding shell commands. The grader does not execute pytest in
S5/S6. S3 permits an explained disposition after the one reminder rather than requiring a
successful subject check. Explanation text remains model-authored narrative, not measured truth.

Failed probes, absent capture, missing scenarios, and empty/info-only grades cannot pass.
Selected-scenario runs explicitly report PARTIAL and do not establish full acceptance.
`--regrade` refuses legacy captures without the new controller evidence rather than inventing
provenance. Original historical receipts are left untouched.

**Regrade is not passive inspection:** for supported, current captures it executes the
subject-controlled pytest suite in S1–S4 and writes `results.regraded.json`. Those tests can
execute arbitrary code; neither regrade nor this repair provides OS isolation. Use only
operator-authorized disposable fixtures. No live acceptance run or measured user benefit is
claimed by the offline regressions.
