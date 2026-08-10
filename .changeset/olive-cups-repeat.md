---
"mrbinnacle-skills": patch
---

Remove a predictive alternative that had been added to the first admission question.

`ADMISSION.md` question 1 shipped as "still fails **(or should plausibly still fail)** the job the skill claims to fix". The parenthetical was not part of the settled question and changes what the policy admits: "fails" is an observation, "should plausibly fail" is a prediction, so the disjunct allowed admission with no unaided run ever performed.

It also contradicted two things already in the repository:

- the gate card's Gate 1, which says "**Don't predict — measure**" and "Count occasions, not artifacts", and Gate 2, which says "Measure, don't argue" and asks for a with-skill vs without-skill run;
- question 2 of this same policy file, which requires occasions be "counted, not predicted".

Question 1 now reads "still fails the job the skill claims to fix. Observed, not predicted: run it unaided first."

The declared version stays `admission-policy v1`. This is errata, not an amendment: the four questions as specified never contained the disjunct, and no machine-readable consumer of the policy exists yet, so no digest of the defective text is in circulation. Questions 2, 3 and 4 were re-checked against Gates 0-2 and are faithful.
