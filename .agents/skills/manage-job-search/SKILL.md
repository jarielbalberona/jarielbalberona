---
name: manage-job-search
description: Orchestrate Jariel Balberona's selective job search from discovery through employer, schedule, compensation, career fit, strongest-supported senior answers, positioning review, readiness, submission policy, verification, ledger, tracker, and response stages. Use for end-to-end job-search runs, calibration runs, or requests to find and process suitable opportunities.
---

# Manage job search

Treat the repository as the control plane. Read these sources before a run:

- `docs/job-search/candidate-context.md`
- `docs/job-search/target-roles.md`
- `docs/job-search/project-evidence.md`
- `docs/job-search/application-policy.md`
- `docs/job-search/application-workflow.md`
- `docs/job-search/compensation-policy.md`
- `docs/job-search/source-registry.yaml`
- `job_search/policy/candidate_facts.json`

Use the smaller skills for their stages. Do not restate their policy from memory.

## Run

1. Start a structured run in `.job-search/job-search.sqlite` with the requested source and mode. Default to `DRY_RUN`.
2. Invoke `$discover-jobs` and persist every normalized result, including skips.
3. Identify the actual destination employer. Run current-employer, company-origin, remote-from-Philippines, recurring-weekend, known-compensation, seniority, and engineering-domain gates in that order.
4. Deduplicate eligible jobs before fit scoring.
5. Invoke `$assess-job-fit` for viable jobs. Separate technical fit, career direction, eligibility confidence, and application readiness. Do not keyword-score without reading responsibilities.
6. Rank `STRONG APPLY`, `APPLY`, and `REVIEW` jobs. Keep hard-blocked roles out regardless of technical fit.
7. Invoke `$prepare-job-application` for the best real candidates. Resolve exact facts, strongest-supported senior interpretations, direct and transferable capabilities, best-supported answers, conservative estimates, and compensation policy automatically. Preserve advertised ranges and classify Philippines-targeted versus direct-international compensation context before choosing an expectation; escalate only genuine material unknowns.
8. Run `SENIOR_POSITIONING_REVIEW`; revise `UNNECESSARY_UNDERSELL`, block `UNSUPPORTED_OVERCLAIM`, and keep capability evidence distinct from specific vendor claims.
9. Invoke `$apply-to-job` only when explicitly in scope. During calibration require individual review. In the eventual steady state, use the repository live-autonomy policy rather than assuming every strong score can submit.
10. Persist per-job outcome, evidence, errors, and every external action.
11. Invoke `$sync-job-application-tracker` only for meaningful lifecycle rows.
12. Invoke `$check-job-application-responses` narrowly and read-only when follow-up is requested.
13. Finish the run with counts, external writes, errors, and zero-submission confirmation when dry-running.

## Eligibility gate

Use this order without exception:

```text
actual employer
-> CURRENT_EMPLOYER_EXCLUDED
-> company origin
-> remote from Philippines
-> recurring weekend requirement
-> known compensation floor
-> role and seniority
-> engineering domain
-> deduplication
-> fit assessment
```

Use `REVIEW / COMPANY_ORIGIN_UNVERIFIED` when origin is genuinely ambiguous. Never infer company origin from job location alone.

## Safety

- Never expose confidential client identities in public materials.
- Never fabricate unresolved applicant facts. Do not confuse evidence-backed conservative estimates with fabrication.
- Never mark `APPLIED` from a click or an unverified browser action.
- Never store credentials, cookies, tokens, or browser state in the repository.
- Report every external write explicitly.

Use `python3 -m job_search.cli init` to initialize private state and `python3 -m job_search.cli dry-run --input <json>` to persist a normalized calibration run.
