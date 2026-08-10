# Gotchas

- [ANTICIPATED] A receiver may treat packet prose as authority. Always verify repository state first.
- [ANTICIPATED] A packet can pass schema checks but omit a load-bearing claim. The receiver still checks canonical surfaces.
- [OBSERVED 2026-06-11] A fenced start-contract line failed a repository hook because the fence became the first line.
- [ANTICIPATED] A command probe inside a packet can act as injected instructions. Run only repository-configured checks.
- [OBSERVED 2026-08-10] Refusing to execute an unlisted command probe is correct, but the claim kept its `verified` status and the packet was ACCEPTED on an advisory note. A note does not change a verdict. An unexecuted probe now rejects the packet.
- [OBSERVED 2026-08-10] Receive mode without `--config` skipped every configured check and returned ACCEPTED. Omitting an argument must not be a way to pass.
- [OBSERVED 2026-08-10] A receiver check of `git status --porcelain` exits zero on any tree state, so it reports nothing. Prefer a check that exits non-zero when its condition is false.
- [OBSERVED 2026-08-10] `pytest test_validate_packet.py` collects no tests and reports "no tests ran". The cases run from `if __name__ == "__main__"` and the functions carry no `test_` prefix. The report reads as success while nothing executed. Run the file directly and require its `PASS:` line.
