---
name: apply-to-job
description: Process one job through activity, employer eligibility, deduplication, fit, evidence, application questions, source policy, submission authority, verification, persistence, and tracker sync. Use only when preparing or performing an application for a specific job; dry-run and disallowed sources must never submit.
---

# Apply to job

Read `docs/job-search/application-policy.md` and the source entry in `docs/job-search/source-registry.yaml`. Invoke `$assess-job-fit` and `$prepare-job-application`; do not duplicate their logic.

## Pipeline

```text
load job
-> verify active
-> identify actual employer
-> hard eligibility gate
-> deduplicate
-> assess fit
-> select narrative and evidence
-> prepare application
-> resolve questions
-> verify source policy and run mode
-> submit only if permitted
-> verify submission
-> persist application and event
-> sync tracker
```

## Hard stops

Never submit when the employer is excluded, company origin is Philippine-local or ambiguous, remote-from-Philippines eligibility is unresolved, a consequential answer is unknown, the listing is inactive or duplicate, source policy forbids it, or run mode is `DRY_RUN`.

`DRY_RUN` must block the submission handler itself, not rely on operator restraint.

## Verification

Do not equate clicking Apply with success. Require a confirmation page, ATS success state, employer confirmation, or appropriate acknowledgement. Record evidence type and time. Without evidence, use `SUBMISSION_UNVERIFIED` and do not mark `APPLIED`.

Never send recruiter messages unless separately authorized. Never store browser or authentication state in Git.
