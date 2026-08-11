---
name: apply-to-job
description: Process one job through employer, schedule, compensation, fit, strongest-supported senior answers, capability-versus-vendor calibration, positioning review, source policy, submission authority, verification, persistence, and tracker sync. Use only for a specific application; dry-run and disallowed sources must never submit.
---

# Apply to job

Read `docs/job-search/application-policy.md`, `docs/job-search/compensation-policy.md`, and the source entry in `docs/job-search/source-registry.yaml`. Invoke `$assess-job-fit` and `$prepare-job-application`; do not duplicate their logic.

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

Never submit when the employer is excluded, company origin is Philippine-local or ambiguous, remote-from-Philippines eligibility is unresolved, recurring weekend work is required, known compensation violates policy, a `MATERIAL_UNKNOWN` remains, the listing is inactive or duplicate, source policy forbids it, or run mode is `DRY_RUN`.

Before finalizing form answers, verify that forced-choice selections are fully supported and that source-of-discovery answers come from ledger provenance rather than the ATS host. A higher option containing an unsupported scale or specialization claim fails truthfulness even when part of the option matches.

`BEST_SUPPORTED_ANSWER` and `CONSERVATIVE_ESTIMATE` are resolved, truthful answers and do not block submission. Resolve expected compensation autonomously; current salary remains separate and may be material unknown.

`STRONGEST_SUPPORTED_ANSWER`, `DIRECT_DEEP`, `DIRECT_WORKING`, and `TRANSFERABLE_STRONG` are also resolved when their evidence is recorded. Before the submission boundary, require a passing `SENIOR_POSITIONING_REVIEW`. Revise `UNNECESSARY_UNDERSELL`; never submit `UNSUPPORTED_OVERCLAIM`. A missing vendor keyword must not erase an underlying senior capability, and transferable capability must not become a fabricated vendor claim.

Expected compensation must follow the current job-specific policy decision. Advertised ranges take priority over generic anchors. Philippines-targeted international roles default to the localized-context anchor unless direct international-rate or other high-budget evidence supports more. Compensation above a target-range maximum is never itself a blocker.

`DRY_RUN` must block the submission handler itself, not rely on operator restraint.

## Live autonomy

During calibration, require Jariel review for every real submission. After calibration, permit autonomy only when repository policy allows it:

- `STRONG APPLY`: readiness at least 85, no blocker or consequential unknown, autonomous source permitted.
- `APPLY`: readiness at least 92 with the same gates.
- `REVIEW`: Jariel review required.
- `SKIP`: never apply.

Do not enable live submission in this skill. Source policy and the calibration flag remain authoritative.

## Verification

Do not equate clicking Apply with success. Require a confirmation page, ATS success state, employer confirmation, or appropriate acknowledgement. Record evidence type and time. Without evidence, use `SUBMISSION_UNVERIFIED` and do not mark `APPLIED`.

Never send recruiter messages unless separately authorized. Never store browser or authentication state in Git.
