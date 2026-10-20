---
"mrbinnacle-skills": patch
---

Conformance gains obligation O9, "no watch past its close", and the edition moves from `conformance v5` to `conformance v6`. The scheduled run now reads the `## On watch` table in `RETIRED.md` and fails a row whose `Watch closes` date is past, is not a `YYYY-MM-DD` date, or sits beside a `Removed` cell with no 40-hex install SHA. It also fails a row whose card name is still under `skills/`, in a plugin manifest or in the Retired table. An empty table passes. `validate_conformance.py` takes `--today YYYY-MM-DD` so tests do not read the wall clock. No card changes and no watch is opened.
