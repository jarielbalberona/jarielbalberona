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
2. Load due or expired, non-closed Review Queue records from SQLite before fresh discovery. Re-verify each due item against the live listing, current form, current source policy, and newly resolved candidate facts. Every active item requires a concrete next action, automatic re-review date, and expiry date; it must not disappear silently.
3. Invoke `$discover-jobs` and persist every normalized result, including skips. Use canonical source IDs and the diversity rotation so one board does not dominate inventory. Diversity affects crawl order only, never fit. For `AUTONOMOUS_CAMPAIGN`, record posting age and freshness, exhaust P0 (0-7 days) before P1 (8-30 days), then consider P2 (31-45 days) only for roles that score `STRONG APPLY`.
4. Identify the actual destination employer. Run current-employer, recurring-weekend, known-compensation, seniority, and engineering-domain gates in that order. Record company origin and remote-from-Philippines evidence, but do not use either as a gate.
5. Deduplicate eligible jobs before fit scoring.
6. Invoke `$assess-job-fit` for viable jobs. Separate technical fit, career direction, eligibility confidence, and application readiness. Do not keyword-score without reading responsibilities.
7. Rank `STRONG APPLY`, `APPLY`, and `REVIEW` jobs. Keep hard-blocked roles out regardless of technical fit.
8. Inspect the complete live form and run application preflight before writing a letter or filling ordinary fields. Detect required photo/video, assessments, CAPTCHA/human verification, ownership/confidentiality declarations, work authorization, and other expensive blockers early. Then invoke `$prepare-job-application` for candidates that can proceed.
9. Run `SENIOR_POSITIONING_REVIEW`; revise `UNNECESSARY_UNDERSELL`, block `UNSUPPORTED_OVERCLAIM`, and keep capability evidence distinct from specific vendor claims.
10. Invoke `$apply-to-job` only when explicitly in scope. In `AUTONOMOUS_CAMPAIGN`, use the hybrid `AUTO_SUBMIT` / `HUMAN_FINAL_CLICK` decision, source-specific live policy, the 8/10/13 combined-outcome targets, separate metrics, and hard cap. A held or failed job must not stop the campaign.
11. Fully populate and verify legitimate human-final-click applications, stop before the final control, and record `HUMAN_SUBMIT_READY`. Keep only 5-10 such tabs open; overflow is `READY_FOR_BROWSER_PREP`. Persist genuine holds and review-only jobs with exact reason, prepared answers, role-specific cover letter, media state, source policy, next action, and re-review date. Never queue hard `SKIP` jobs.
12. Persist each canonical per-job outcome and application event in SQLite. All campaign counts must be derived from `run_outcomes`; never type or estimate summary counts manually.
13. Invoke `$sync-job-application-tracker` only for meaningful lifecycle rows and Review Queue transitions.
14. Run the configured daily `$check-job-application-responses` monitor narrowly and read-only. It may search, read, classify, reconcile SQLite, and sync tracker state; it may not send, reply, archive, delete, or label mail.
15. Finish the run with discovered, eligible, assessed, verdict, prepared, auto-submitted, auto-verified-submitted, human-submit-ready, ready-for-browser-prep, human-clicked, human-verified-submitted, submission-unverified, video-required, held, and skipped counts; external writes; errors; and zero-submission confirmation when dry-running.

## Eligibility gate

Use this order without exception:

```text
actual employer
-> CURRENT_EMPLOYER_EXCLUDED
-> record company origin and remote geography
-> recurring weekend requirement
-> known compensation floor
-> role and seniority
-> engineering domain
-> deduplication
-> fit assessment
```

Employer origin and remote-from-Philippines status do not block scoring or application. Never infer company origin from job location alone, and never alter Jariel's canonical location or authorization answers to fit a listing.

## Safety

- Never expose confidential client identities in public materials.
- Never fabricate unresolved applicant facts. Do not confuse evidence-backed conservative estimates with fabrication.
- Never mark `APPLIED` from a click or an unverified browser action.
- Transition application state through the SQLite lifecycle authority only. `APPLIED` requires typed confirmation evidence; the Google Sheet is a projection and may not override lifecycle status.
- Never store credentials, cookies, tokens, or browser state in the repository.
- Report every external write explicitly.

Use `python3 -m job_search.cli init` to initialize private state and `python3 -m job_search.cli dry-run --input <json>` to persist a normalized calibration run.
