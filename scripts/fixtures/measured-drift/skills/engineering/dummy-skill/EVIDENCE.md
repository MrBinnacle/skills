# EVIDENCE — dummy-skill (fixture)

Fixture record, and the poison in this tree. Its Screen result states a controlled outcome, so
the derived measured count is 1 while every scoreboard site in this tree still says `0 measured`.

That is the failure the control exists to catch: the day a card is finally screened, the front
page's `0 measured` becomes false, and it has to go red rather than stay quietly wrong. Nothing
else in this tree disagrees with the repository — the other three numbers are correct and the
policy version matches — so the only thing this fixture can fail on is the assertion under test.

| Field | Value |
|---|---|
| **Screen result** | KEEP. Fixture: a controlled result, deliberately not UNMEASURED. |
| **Paired verdict** | UNMEASURED. Fixture. |
