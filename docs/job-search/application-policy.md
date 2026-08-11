# Application policy

The system optimizes for qualified opportunities where Jariel's real experience gives an employer a credible reason to interview him. It does not optimize for application count.

## Eligibility

A job may proceed only when:

```text
fit meets threshold
AND no hard blocker exists
AND actual employer is eligible
AND role is legitimate and active
AND role is not a duplicate
AND answers are truthful
AND consequential unknowns are resolved
AND source execution policy permits the action
```

Run gates in this order: actual employer, current-employer exclusion, company origin, remote-from-Philippines compatibility, required recurring weekend work, known compensation floors, role/seniority, engineering domain, deduplication, then fit scoring.

Confirmed current employers and clients always produce `SKIP / CURRENT_EMPLOYER_EXCLUDED`, including a recruiter listing that names a blocked destination company. Confirmed Philippine-local employers produce `SKIP / PH_LOCAL_COMPANY`. Ambiguous company origin produces `REVIEW / COMPANY_ORIGIN_UNVERIFIED` and cannot proceed to submission.

## Reason codes

- `CURRENT_EMPLOYER_EXCLUDED`
- `PH_LOCAL_COMPANY`
- `COMPANY_ORIGIN_UNVERIFIED`
- `REMOTE_PH_INELIGIBLE`
- `SENIORITY_MISMATCH`
- `ENGINEERING_DOMAIN_MISMATCH`
- `ROLE_DEPRIORITIZED`
- `INACTIVE_JOB`
- `DUPLICATE_JOB`
- `SUSPECT_LISTING`
- `UNRESOLVED_CONSEQUENTIAL_FACT`
- `MATERIAL_UNKNOWN`
- `REQUIRED_CANDIDATE_PHOTO`
- `REQUIRED_VIDEO_INTRO`
- `BEST_SUPPORTED_ANSWER`
- `CONSERVATIVE_ESTIMATE`
- `APPLICATION_ENTRY_UNAVAILABLE`
- `SCREENING_ANSWERS_UNRESOLVED`
- `SCREENING_QUESTIONS_UNVERIFIED`
- `REQUIRED_WEEKEND_WORK`
- `WEEKEND_WORK_UNVERIFIED`
- `COMPENSATION_BELOW_MINIMUM`
- `COMPENSATION_REVIEW`
- `COMPENSATION_TARGET_MATCH`
- `COMPENSATION_ACCEPTABLE`
- `COMPENSATION_UNDISCLOSED`
- `COMPENSATION_CONVERSION_REQUIRED`
- `MATERIAL_REQUIREMENT_GAP`
- `CAREER_DIRECTION_MISMATCH`
- `CALIBRATION_REVIEW_REQUIRED`
- `READINESS_BELOW_AUTONOMY_THRESHOLD`
- `VERDICT_REQUIRES_REVIEW`
- `VERDICT_SKIP`
- `SOURCE_NOT_AUTONOMOUS`
- `SOURCE_EXECUTION_FORBIDDEN`
- `SUBMISSION_UNVERIFIED`

Current-employer identities are represented by normalized fingerprints in tracked policy. Do not log or publish the private relationship.

Timezone inconvenience is not a blocker. Full-time contractor, independent-contractor, consultant, freelance, B2B, and EOR structures are accepted. Required recurring weekend work is a hard incompatibility; ambiguous or rare on-call language requires evidence rather than an automatic skip.

Uncertainty is not the same as unanswerable. `EXACT`, `BEST_SUPPORTED_ANSWER`, and `CONSERVATIVE_ESTIMATE` answers are truthful resolved answers. Only a genuine `MATERIAL_UNKNOWN` remains consequential. Compensation evaluation follows `compensation-policy.md`; undisclosed compensation is not a blocker and ordinary expected-compensation answers are autonomous.

## Candidate media

The canonical candidate photo is a reusable private asset under the gitignored `.job-search/assets/` directory. Attach it automatically only when a legitimate application requires a photo, or when an optional photo is clearly beneficial under the source policy. Never commit the image to the public repository.

No canonical introduction video currently exists, and the system must not generate, fabricate, substitute, or reuse unrelated footage. A live form that proves an introduction video is required produces `REQUIRED_VIDEO_INTRO` and action `HOLD`. This is an application-readiness constraint, not a permanent global eligibility blocker, and it must not reduce Technical Fit or Career Direction Fit.

## Lifecycle

Local jobs may be `DISCOVERED`, `SKIPPED`, `REVIEW`, or `CANDIDATE`. Human-facing application states are:

- `SHORTLISTED`
- `PREPARED`
- `APPLIED`
- `ASSESSMENT`
- `INTERVIEW`
- `REJECTED`
- `OFFER`
- `WITHDRAWN`
- `CLOSED`

An automated receipt remains `APPLIED`; it is not recruiter interest.

## Submission evidence

Clicking an Apply control is not success. Mark `APPLIED` only after a confirmation page, ATS success state, employer confirmation, or appropriate acknowledgement proves submission. Persist the evidence type and timestamp.

## Execution modes

- `DRY_RUN`: discovery, normalization, eligibility, assessment, drafting, local persistence, safe tracker schema work, and read-only Gmail checks only. Submission handlers must not execute.
- `DISCOVERY_ONLY`: discover and inspect; never submit.
- `ASSISTED`: prepare and navigate only to the documented human boundary; do not claim submission without evidence.
- `AUTONOMOUS`: allowed only after current platform policy is verified and `source-registry.yaml` explicitly permits live submission.
- `DISABLED`: do not access the source.

V1 is `DRY_RUN`. Real applications submitted during initial calibration must be zero.

## Live-autonomy policy

Live submission remains disabled during calibration. The intended steady state is:

```text
STRONG APPLY
+ no hard blocker
+ no consequential unresolved question
+ source permits autonomous submission
+ application readiness >= 85
-> autonomous application permitted

APPLY
+ the same gates
+ application readiness >= 92
-> autonomous application permitted

REVIEW
-> Jariel review required

SKIP
-> never apply
```

The higher `APPLY` threshold prevents a merely acceptable fit from becoming autonomous without unusually strong readiness evidence. Individual approval for every strong application is a calibration-stage rule, not the intended permanent operating model.

Do not enable autonomy by changing run mode alone. The source must be explicitly verified for live submission, `live_submit` must be enabled, the calibration flag must be cleared, and the current assessment plus actual screening questions must pass the policy.
