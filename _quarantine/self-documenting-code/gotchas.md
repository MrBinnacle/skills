# gotchas.md — self-documenting-code

Append-only log of observed and anticipated failure modes.

## [ANTICIPATED] 2026-09-06 — Description rewrite may lose retrieval surface

The original description was 285 characters. The published bar requires <= 200. The rewrite
shortened it to a router form ("Guide for writing self-documenting code through semantic
functions, pragmatic wrappers, and precise models"). If the card's retrieval depends on
specific terms that were in the longer description, the shorter version may not fire in the
same situations.

## [ANTICIPATED] 2026-09-06 — No EVIDENCE.md, no occurrences counted

The card carries zero counted occurrences. Against ADMISSION.md it fails criterion 1 (no
observed unaided failure), criterion 2 (no occasions counted), and criterion 4 (no
EVIDENCE.md). Three of four. The card is not admissible today.

## [ANTICIPATED] 2026-09-06 — No eval fixtures

The registry notes the current evals contain no fixture files. Without executable contrasting
fixtures the card cannot be screened. The ceiling is fixed regardless of treatment quality.

## [ANTICIPATED] 2026-09-06 — External registry validator does not accept gotchas.md

The registry's bundled `validate_package.py` does not list `gotchas.md` in its allowed
top-level file list. This file was added anyway because the repository's own
`validate_card_files.py` requires it for published cards. When the registry validator is
updated, this gotcha should be checked against the new allow-list.
