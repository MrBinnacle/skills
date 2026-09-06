# Evidence - 0.2.0 candidate

Sources: the 0.1.0 card and FIELD-REPORT-2026-08-17.
The field report covers one agent's session. It records no 0.2.0 run.

| Row | Record |
|---|---|
| Origin | ABSENT: the report shows the card working, not an observed clarity failure without it. The deciding words are: `Without that rule, both edits would have shipped as "cleanup"`. The edits were prevented. Nobody has yet recorded them happening without the card in this evidence base. The earlier shipped identity bug has no recorded conditions showing the card was absent. A directly observed unaided failure would fill this row. |
| Occasions counted | ABSENT: no supported count of unaided origin failures. The report's n = 1 counts an assisted session, not an unaided failure. A record of unaided events and their conditions would fill this row. |
| Dispatches recorded | One user-invoked clarity pass on 2026-08-17. Implementation, built-in code-review and codebase-design also ran. The narrative reports 8 findings: 7 applied, 1 recorded-not-corrected. The metrics instead say 8 (2 Required, 5 Recommended, 1 Optional) plus 1 Recorded-not-corrected. These totals conflict. The report also records 2 changes prevented and 2 frozen files kept out of scope. |
| Validated against | One private TypeScript repository: 16 files, 2,213 lines. The immediate harness swap had 52 + 73 assertions before and after, with zero failures. The full pass ended at 53 + 92, with zero failures. The report states 0 intended behavior changes and byte-identical live end-to-end output. Equal counts alone do not prove every case survived. These are 0.1.0 field results, not a controlled screen. |
| Screen result | ABSENT: no measured screen result. A recorded run against a frozen fixture and counterfixture would fill this row. |
| Paired verdict | ABSENT: no matched run with and without the card. Paired runs on the same frozen inputs would fill this row. |
| Standing cost | ABSENT: no measured token, time or upkeep cost. The baseline requires the assessment model on every pass. A dispatch cost log would fill the measured gap. |
| Re-screen trigger | ABSENT: no prior screen or agreed rerun condition. A recorded screen with its stated rerun condition would fill this row. |

## Limits

The clarity pass found two defects with live consequences in test machinery.
Built-in code-review found six defects, three introduced by the commit under review.
The report says these defect sets were disjoint.

Nothing has been replicated. The companion skills prevent a clean claim about
what this card alone caused. The report's proposed workflow changes were not
tested on another repository.
