---
name: manage-job-search
description: Orchestrate Jariel Balberona's selective job search from discovery through employer, schedule, compensation, career fit, strongest-supported senior answers, positioning review, readiness, submission policy, verification, ledger, tracker, and response stages. Use for end-to-end job-search runs, calibration runs, or requests to find and process suitable opportunities.
---

# Manage job search

Treat the repository as the control plane. Read these sources before a run:

- `docs/job-search/candidate-context.md`
- `docs/job-search/application-answer-bank.md`
- `docs/job-search/target-roles.md`
- `docs/job-search/project-evidence.md`
- `docs/job-search/application-policy.md`
- `docs/job-search/application-workflow.md`
- `docs/job-search/compensation-policy.md`
- `docs/job-search/source-registry.yaml`
- `job_search/policy/candidate_facts.json`
- `job_search/policy/application_answer_bank.json`

Use the smaller skills for their stages. Do not restate their policy from memory.

## Run

1. Start a structured run in `.job-search/job-search.sqlite` with the requested source and mode. Default to the source registry; never infer campaign authority from a browser session.
2. Load due, non-closed Review Queue records from SQLite before fresh discovery. Re-verify each due item against the live listing, current form, current source policy, and newly resolved candidate facts. A held item may become ready, remain held with a new date, or close; it must not disappear silently.
3. Invoke `$discover-jobs` and persist every normalized result, including skips. For `AUTONOMOUS_CAMPAIGN`, record posting age and freshness, exhaust P0 before P1, and normally reject older-than-14-day inventory.
4. Identify the actual destination employer. Run current-employer, company-origin, remote-from-Philippines, recurring-weekend, known-compensation, seniority, and engineering-domain gates in that order.
5. Deduplicate eligible jobs before fit scoring.
6. Invoke `$assess-job-fit` for viable jobs. Separate technical fit, career direction, eligibility confidence, and application readiness. Do not keyword-score without reading responsibilities.
7. Rank `STRONG APPLY`, `APPLY`, and `REVIEW` jobs. Keep hard-blocked roles out regardless of technical fit.
8. Invoke `$prepare-job-application` for the best real candidates. Search the canonical answer bank first, then use candidate and project evidence, strongest-supported senior interpretations, direct and transferable capabilities, best-supported answers, conservative estimates, and compensation policy automatically. Preserve advertised ranges and classify Philippines-targeted versus direct-international compensation context before choosing an expectation; escalate only genuine material unknowns.
9. Run `SENIOR_POSITIONING_REVIEW`; revise `UNNECESSARY_UNDERSELL`, block `UNSUPPORTED_OVERCLAIM`, and keep capability evidence distinct from specific vendor claims.
10. Invoke `$apply-to-job` only when explicitly in scope. In `AUTONOMOUS_CAMPAIGN`, use the hybrid `AUTO_SUBMIT` / `HUMAN_FINAL_CLICK` decision, source-specific live policy, the 8/10/13 combined-outcome targets, separate metrics, and hard cap. A held or failed job must not stop the campaign.
11. Fully populate and verify legitimate human-final-click applications, stop before the final control, and record `HUMAN_SUBMIT_READY`. Keep only 5-10 such tabs open; overflow is `READY_FOR_BROWSER_PREP`. Persist genuine holds and review-only jobs with exact reason, prepared answers, role-specific cover letter, media state, source policy, next action, and re-review date. Never queue hard `SKIP` jobs.
12. Persist per-job outcome, evidence, errors, and every external action.
13. Invoke `$sync-job-application-tracker` only for meaningful lifecycle rows and Review Queue transitions.
14. Invoke `$check-job-application-responses` narrowly and read-only when follow-up is requested.
15. Finish the run with discovered, eligible, assessed, verdict, prepared, auto-submitted, auto-verified-submitted, human-submit-ready, ready-for-browser-prep, human-clicked, human-verified-submitted, submission-unverified, video-required, held, and skipped counts; external writes; errors; and zero-submission confirmation when dry-running.

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
