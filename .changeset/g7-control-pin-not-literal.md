---
---

fix: the G7 poison-control test checks for a pinned checkout SHA, not one literal SHA.

`case_ci_control_refuses_a_mutable_workflow_ref` asserted that one exact `actions/checkout`
commit SHA appeared in the G7 control step, so every Dependabot bump of `actions/checkout`
turned the release gate red (#338). The case now requires the control to carry an
`actions/checkout@<40 lowercase hex>` ref, and requires that SHA to be one the workflow itself
checks out with elsewhere, read from the workflow file. It changes a test only. No card and no
package behaviour changes, so this changeset is empty and the release is not bumped by it.
