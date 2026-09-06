# Assessment model

Use this model to separate code clarity defects from missing external context.

## The seven code dimensions

| Dimension | Reader question | Strong code evidence | Typical defect |
|---|---|---|---|
| Vocabulary | What domain concept is this? | Stable domain names across code, tests, and interfaces | Vague, conflicting, or implementation-only names |
| Contract | What enters, exits, and remains true? | Types, schemas, signatures, invariants, validation | Ambiguous inputs, outputs, nullability, or ownership |
| Control flow | What sequence and decision structure applies? | Small branches, guard clauses, named conditions | Deep nesting, mixed levels of abstraction, hidden order |
| State and units | What state or measurement does this value represent? | Enums, value objects, units, lifecycle types | Boolean blindness, magic values, unit ambiguity |
| Side effects | What does this operation change? | Command verbs, explicit dependencies, transaction boundaries | A query-like name that writes, hidden network or file work |
| Failure behavior | How can this fail and who handles it? | Result types, explicit exceptions, validation boundaries | Swallowed errors, generic exceptions, surprise retries |
| Executable examples | Which behavior is promised? | Focused tests with condition-and-result names | Tests that mirror implementation or hide expected behavior |

## Facts code can carry

Code can usually state:

- Domain names and relationships.
- Data shape, units, ownership, nullability, and valid states.
- Control flow and operation sequence.
- Side effects and transaction boundaries.
- Failure modes that belong to the interface.
- Behavioral examples through focused tests.

## Facts code cannot carry safely

Keep these facts in comments, ADRs, issues, or user documentation:

- Why this design won against credible alternatives.
- The external authority for a business, legal, or regulatory rule.
- Historical incidents and compatibility obligations.
- Performance evidence and the workload that produced it.
- Security assumptions that depend on another system.
- Deprecation dates, migration ownership, and release commitments.
- Counterintuitive behavior that an external dependency requires.

A longer identifier is not a substitute for rationale.

## Finding test

A finding is actionable only when all five statements hold:

1. A specific reader question has no reliable answer.
2. The code contains exact evidence of the gap.
3. The gap can cause misunderstanding, defects, or unsafe change.
4. A smaller correction cannot solve the same problem.
5. Verification can show that behavior remained stable.

If statement 3 or 5 fails, report the item as optional or unverified. Do not edit by default.

## Priority

### Required

Use this priority when the code can mislead a reader about behavior or safety.

Examples include hidden writes, ambiguous units, misleading names, stale comments, invalid states, and accidental public API changes.

### Recommended

Use this priority when the defect creates a clear maintenance cost inside the task scope.

Examples include repeated terminology drift, unnecessary nesting, and a function with two separable responsibilities.

### Optional

Use this priority for taste, local style, or alternative designs with no demonstrated benefit.

Do not make optional changes unless the user requests broad cleanup.

## Reader-question method

Write the question before the correction.

Weak finding:

> This function is too complex.

Strong finding:

> A reader cannot tell whether `load_account` reads local state or refreshes remote state. The function performs an HTTP write on line 42. Rename or split the refresh operation, then verify call sites.

## False positives

Do not flag these by default:

- Framework idioms that the repository uses consistently.
- Short local names in a small and obvious scope.
- Generated code.
- Mathematical notation where the domain uses that notation.
- A long function that represents one linear algorithm clearly.
- Repetition that prevents a premature abstraction.
- Comments that cite authority, rationale, units, hazards, or compatibility.
