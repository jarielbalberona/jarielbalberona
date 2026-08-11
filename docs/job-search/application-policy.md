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
- `STRONGEST_SUPPORTED_ANSWER`
- `DIRECT_DEEP`
- `DIRECT_WORKING`
- `TRANSFERABLE_STRONG`
- `CONSERVATIVE_ESTIMATE`
- `UNNECESSARY_UNDERSELL`
- `UNSUPPORTED_OVERCLAIM`
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
- `CAMPAIGN_MAXIMUM_REACHED`
- `POSTING_DATE_UNVERIFIED`
- `STALE_JOB`
- `HUMAN_ONLY_ACTION`

Current-employer identities are represented by normalized fingerprints in tracked policy. Do not log or publish the private relationship.

Timezone inconvenience is not a blocker. Full-time contractor, independent-contractor, consultant, freelance, B2B, and EOR structures are accepted. Required recurring weekend work is a hard incompatibility; ambiguous or rare on-call language requires evidence rather than an automatic skip.

Uncertainty is not the same as unanswerable. Resolve in this order: `EXACT`, `STRONGEST_SUPPORTED_ANSWER`, capability-depth classifications such as `DIRECT_DEEP`, `DIRECT_WORKING`, and `TRANSFERABLE_STRONG`, then `BEST_SUPPORTED_ANSWER`, `CONSERVATIVE_ESTIMATE`, and finally `MATERIAL_UNKNOWN`. All positive evidence-backed statuses are truthful resolved answers. Only a genuine `MATERIAL_UNKNOWN` remains consequential. Compensation evaluation follows `compensation-policy.md`; undisclosed compensation is not a blocker and ordinary expected-compensation answers are autonomous.

## Senior candidate positioning

Application answers must present Jariel as a 10+ year senior engineer with documented full-stack, product, platform, cloud, architecture, consulting, CMS, AI-product, and agentic-development depth. Use the strongest truthful interpretation supported by career and project history. Do not optimize for the most cautious wording when that wording materially understates direct experience.

Distinguish the underlying engineering capability from experience with a specific vendor. Custom CMS architecture, WordPress, Shopify, admin systems, and content workflows establish substantial CMS engineering even without AEM or Sitecore specialization. Apply the same distinction to cloud, observability, APIs, databases, and AI engineering.

Run `SENIOR_POSITIONING_REVIEW` before the submission boundary. Revise answers or writing flagged `UNNECESSARY_UNDERSELL`; do not submit content flagged `UNSUPPORTED_OVERCLAIM`. Boolean answers remain concise when `Yes` or `No` is supported. Free text should lead with what Jariel built, owned, designed, architected, delivered, or improved instead of junior-style eager-to-learn language.

For forced-choice questions, `strongest supported` applies to the complete semantics of an option, not one attractive phrase inside it. Every material scale, environment, vendor, migration, traffic, certification, or scope claim must be evidenced. If a higher option mixes supported capability with an unsupported enterprise-scale claim, select the strongest fully supported lower option and use available free text to preserve accurate depth.

Discovery provenance and application infrastructure are separate facts. Record the channel that originally surfaced the job, the destination employer page, and the ATS host independently. Never answer a source-of-discovery question with an ATS name solely because the ATS hosts the form.

## Candidate media

The canonical candidate photo is a reusable private asset under the gitignored `.job-search/assets/` directory. Attach it automatically only when a legitimate application requires a photo, or when an optional photo is clearly beneficial under the source policy. Never commit the image to the public repository.

No canonical introduction video currently exists, and the system must not generate, fabricate, substitute, or reuse unrelated footage. A live form that proves an introduction video is required produces `REQUIRED_VIDEO_INTRO` and action `HOLD`. This is an application-readiness constraint, not a permanent global eligibility blocker, and it must not reduce Technical Fit or Career Direction Fit.

## Lifecycle

Local jobs may be `DISCOVERED`, `SKIPPED`, `REVIEW`, or `CANDIDATE`. Human-facing application states are:

- `SHORTLISTED`
- `PREPARED`
- `HELD`
- `APPLIED`
- `SUBMISSION_UNVERIFIED`
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
- `AUTONOMOUS_CAMPAIGN`: apply the same per-application autonomy gate inside a persisted campaign with freshness priority, hold-and-continue behavior, separate verified-submission counting, and a hard submission cap.
- `DISABLED`: do not access the source.

Initial calibration is complete for the control plane, but source permission remains ATS-specific. A proven assisted submission does not promote that ATS to autonomous use. Indeed, LinkedIn, and Greenhouse remain non-autonomous under their verified current policies. Workable is the first autonomous source because its candidate terms permit applying and its current documentation explicitly recognizes AI-assisted and automated applications. Employer-specific declarations on each form still override source-level permission.

## Live-autonomy policy

The bounded live policy is:

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

## Bounded autonomous campaigns

`AUTONOMOUS_CAMPAIGN` uses these repository-owned limits:

```text
minimum desired new verified submissions: 8
normal target:                            10
absolute maximum:                        13
P0 freshness:                            0-7 days
P1 freshness:                            8-14 days
```

Only a submission backed by confirmation evidence increments `verified_submitted`. Prepared, held, failed, duplicate, and unverified attempts do not count. Stop immediately at 13 verified submissions. At 8 or more, stop when fresh high-quality inventory has been reasonably exhausted. Below 8, stop rather than weakening eligibility, fit, readiness, truthfulness, source, schedule, or compensation policy.

One blocked job never blocks the campaign. Persist its exact outcome as `HELD`, `SKIP`, or `PREPARED`, then continue. Required video, inaccessible forms, human-only actions, unsupported consequential declarations, non-autonomous sources, failed verification, inactive listings, and source-policy failures are per-job outcomes.

Before every submission, query the SQLite ledger and Google Sheet for the canonical URL, employer, role, posting ID, description fingerprint, and previous events. Run `SENIOR_POSITIONING_REVIEW` on the complete live payload. Do not retry an unverified submission blindly.
