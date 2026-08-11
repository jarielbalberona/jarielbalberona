---
name: manage-job-search
description: Orchestrate Jariel Balberona's selective job search from source discovery through employer eligibility, deduplication, fit assessment, application preparation, permitted submission, verification, local persistence, Google Sheet sync, and Gmail response reconciliation. Use for end-to-end job-search runs, calibration runs, or requests to find and process suitable opportunities.
---

# Manage job search

Treat the repository as the control plane. Read these sources before a run:

- `docs/job-search/candidate-context.md`
- `docs/job-search/target-roles.md`
- `docs/job-search/project-evidence.md`
- `docs/job-search/application-policy.md`
- `docs/job-search/application-workflow.md`
- `docs/job-search/source-registry.yaml`

Use the smaller skills for their stages. Do not restate their policy from memory.

## Run

1. Start a structured run in `.job-search/job-search.sqlite` with the requested source and mode. Default to `DRY_RUN`.
2. Invoke `$discover-jobs` and persist every normalized result, including skips.
3. Identify the actual destination employer. Run current-employer, company-origin, remote-from-Philippines, seniority, and engineering-domain gates in that order.
4. Deduplicate eligible jobs before fit scoring.
5. Invoke `$assess-job-fit` for viable jobs. Separate technical fit, career direction, eligibility confidence, and application readiness. Do not keyword-score without reading responsibilities.
6. Rank `STRONG APPLY`, `APPLY`, and `REVIEW` jobs. Keep hard-blocked roles out regardless of technical fit.
7. Invoke `$prepare-job-application` for the best real candidates. Select only relevant evidence.
8. Invoke `$apply-to-job` only when explicitly in scope. During calibration require individual review. In the eventual steady state, use the repository live-autonomy policy rather than assuming every strong score can submit.
9. Persist per-job outcome, evidence, errors, and every external action.
10. Invoke `$sync-job-application-tracker` only for meaningful lifecycle rows.
11. Invoke `$check-job-application-responses` narrowly and read-only when follow-up is requested.
12. Finish the run with counts, external writes, errors, and zero-submission confirmation when dry-running.

## Eligibility gate

Use this order without exception:

```text
actual employer
-> CURRENT_EMPLOYER_EXCLUDED
-> company origin
-> remote from Philippines
-> role and seniority
-> engineering domain
-> deduplication
-> fit assessment
```

Use `REVIEW / COMPANY_ORIGIN_UNVERIFIED` when origin is genuinely ambiguous. Never infer company origin from job location alone.

## Safety

- Never expose confidential client identities in public materials.
- Never fabricate unresolved applicant facts.
- Never mark `APPLIED` from a click or an unverified browser action.
- Never store credentials, cookies, tokens, or browser state in the repository.
- Report every external write explicitly.

Use `python3 -m job_search.cli init` to initialize private state and `python3 -m job_search.cli dry-run --input <json>` to persist a normalized calibration run.
