# Application policy

The system optimizes for qualified opportunities where Jariel's real experience gives an employer a credible reason to interview him. It does not optimize for application count.

## Eligibility

A job may proceed only when:

```text
fit meets threshold
AND no hard blocker exists
AND actual employer is identified sufficiently for exclusion and deduplication checks
AND role is legitimate and active
AND role is not a duplicate
AND answers are truthful
AND consequential unknowns are resolved
AND source execution policy permits the action
```

Run gates in this order: actual employer, current-employer exclusion, required recurring weekend work, known compensation floors, role/seniority, engineering domain, deduplication, then fit scoring. Record company origin and remote-from-Philippines status before scoring, but do not use either as an eligibility gate.

Confirmed current employers and clients always produce `SKIP / CURRENT_EMPLOYER_EXCLUDED`, including a recruiter listing that names a blocked destination company. Philippine-local employers, ambiguous employer origin, explicit remote-from-Philippines exclusions, and unverified remote geography may proceed to scoring and application. Preserve those facts, score remote/employment compatibility honestly, and never misstate Jariel's Philippine location or authorization.

## Reason codes

- `CURRENT_EMPLOYER_EXCLUDED`
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
- `NONCENTRAL_SKILL_GAP`
- `CAREER_DIRECTION_MISMATCH`
- `CALIBRATION_REVIEW_REQUIRED`
- `READINESS_BELOW_AUTONOMY_THRESHOLD`
- `VERDICT_REQUIRES_REVIEW`
- `VERDICT_SKIP`
- `SOURCE_NOT_AUTONOMOUS`
- `SOURCE_EXECUTION_FORBIDDEN`
- `SOURCE_RESTRICTED`
- `POLICY_UNCLEAR`
- `GLOBAL_USER_AUTHORIZATION_MISSING`
- `INDIVIDUAL_APPLICATION_APPROVAL_REQUIRED`
- `SUBMISSION_UNVERIFIED`
- `CAMPAIGN_MAXIMUM_REACHED`
- `POSTING_DATE_UNVERIFIED`
- `STALE_JOB`
- `HUMAN_ONLY_ACTION`
- `HUMAN_VERIFICATION_REQUIRED`
- `TECHNICAL_FINAL_CLICK_RESTRICTED`

Historical ledger rows may contain `PH_LOCAL_COMPANY`, `COMPANY_ORIGIN_UNVERIFIED`, `REMOTE_PH_INELIGIBLE`, or `REMOTE_PH_UNVERIFIED`. Those codes describe the policy in effect when the row was assessed; they are no longer live eligibility gates.

Current-employer identities are represented by normalized fingerprints in tracked policy. Do not log or publish the private relationship.

Timezone inconvenience and listing geography are not blockers. Full-time contractor, independent-contractor, consultant, freelance, B2B, and EOR structures are accepted. Required recurring weekend work is a hard incompatibility; ambiguous or rare on-call language requires evidence rather than an automatic skip.

Responsibilities override title shorthand. Explicitly junior roles remain deprioritized, while `Software Engineer`, `Engineer III`, `Mid-Senior`, hands-on solutions architecture, senior backend, software-heavy platform, developer infrastructure, developer productivity, integration or cloud product engineering, and technical-lead roles may proceed when actual scope is senior and hands-on. One learnable non-central stack or vendor gap is acceptable and uses `NONCENTRAL_SKILL_GAP`; a missing technology central to daily work remains `MATERIAL_REQUIREMENT_GAP`.

Uncertainty is not the same as unanswerable. Search the canonical application answer bank first, then candidate and project evidence, then derive the strongest-supported answer. Within that process use `EXACT`, `STRONGEST_SUPPORTED_ANSWER`, capability-depth classifications such as `DIRECT_DEEP`, `DIRECT_WORKING`, and `TRANSFERABLE_STRONG`, then `BEST_SUPPORTED_ANSWER`, `CONSERVATIVE_ESTIMATE`, and finally `MATERIAL_UNKNOWN`. All positive evidence-backed statuses are truthful resolved answers. Only a genuine `MATERIAL_UNKNOWN` remains consequential. Compensation evaluation follows `compensation-policy.md`; undisclosed compensation is not a blocker and ordinary expected-compensation answers are autonomous.

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
- `HUMAN_SUBMIT_READY`
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

SQLite owns lifecycle state. Canonical events distinguish preparation, human-ready, submit-clicked, submission-verified, submission-unverified, response stages, and tracker/queue projections. Normalize legacy aliases during maintenance. The Applications Sheet may contain only independently verified `APPLIED` or later records and cannot override SQLite status.

`HUMAN_SUBMIT_READY` means every live field and document has been prepared and verified and the only remaining action is Jariel's final submission control. It is not `APPLIED`, `HOLD`, `VIDEO_REQUIRED`, `POLICY_UNCLEAR`, or `SOURCE_RESTRICTED`. A later statement that Jariel clicked Submit must be reconciled as `VERIFIED_SUBMITTED`, `SUBMISSION_UNVERIFIED`, `NOT_SUBMITTED`, `FAILED`, or `DUPLICATE_RISK`; never assume success or click again blindly.

## Execution modes

- `DRY_RUN`: discovery, normalization, eligibility, assessment, drafting, local persistence, safe tracker schema work, and read-only Gmail checks only. Submission handlers must not execute.
- `DISCOVERY_ONLY`: discover and inspect; never submit.
- `ASSISTED`: process one candidate-directed application. Submission is allowed only when the source is `PERMITTED`, or when a dated `UNCLEAR` review is covered by standing candidate authorization. Never claim submission without evidence.
- `AUTONOMOUS`: allowed when current platform policy is `PERMITTED`, or through the narrower dated-`UNCLEAR` standing-authorization override, and every other source, readiness, and campaign gate passes.
- `AUTONOMOUS_CAMPAIGN`: apply the hybrid execution gate inside a persisted campaign with freshness priority, hold-and-continue behavior, separate autonomous and human-ready metrics, and a hard outcome cap.
- `DISABLED`: do not access the source.

Initial calibration is complete for the control plane, but source permission remains ATS-specific. A proven assisted submission does not promote that ATS to autonomous use. Indeed, LinkedIn, and Greenhouse remain non-autonomous under their verified current policies. Workable is the first autonomous source because its candidate terms permit applying and its current documentation explicitly recognizes AI-assisted and automated applications. Employer-specific declarations on each form still override source-level permission.

Jariel has granted standing candidate-side authorization for truthful job applications across all sources. Individual application approval is no longer required. When a dated review finds that applicant-side terms are silent or genuinely unclear, this standing authorization permits the agent to complete and submit the application without asking Jariel again. The source remains classified `UNCLEAR`; the candidate authorization does not turn it into verified platform permission.

This override never applies to an explicit source restriction, a disabled source, employer declarations, CAPTCHA, identity verification, security controls, paid application actions, truthfulness, duplicate, campaign-cap, or application-readiness gates. A source with no dated policy review remains blocked until reviewed.

Model applicant-side platform policy separately as `PERMITTED`, `RESTRICTED`, or `UNCLEAR`. Silence is `UNCLEAR`, not permission. An explicit restriction is `RESTRICTED` and cannot be overridden by candidate authorization. `PERMITTED` enables ordinary autonomous submission; a dated `UNCLEAR` classification may proceed only through the narrower standing-candidate-authorization override.

## Hybrid execution model

Standing candidate authorization applies globally, but source permission and technical capability still determine who performs the final click:

```text
eligible + complete + ready
-> source permits autonomous submission and no human-only control
   -> AUTO_SUBMIT -> verify -> APPLIED
-> source is explicitly restricted, policy is unclear without a dated review and standing override, CAPTCHA or human verification is required,
   or the final control cannot legitimately be automated
   -> fully populate and verify -> HUMAN_SUBMIT_READY
-> required video, inaccessible form, or genuine candidate fact/requirement gap
   -> VIDEO_REQUIRED, FORM_INACCESSIBLE, or HOLD
```

The human-final-click branch authorizes preparation only. It never authorizes the agent to bypass CAPTCHA, identity/security verification, source restrictions, or a technically protected final control. Keep at most 5-10 fully prepared browser tabs open; overflow becomes `READY_FOR_BROWSER_PREP`.

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

The higher `APPLY` threshold prevents a merely acceptable fit from becoming autonomous without unusually strong readiness evidence. The candidate-side authorization is now global:

```yaml
submission_authorization:
  user_authorized_globally: true
  individual_application_approval_required: false
  policy_unclear_agent_submission_authorized: true
```

Do not enable autonomy by changing run mode alone. An ordinarily permitted source must be explicitly verified for live submission and have `live_submit` enabled. The only exception is a dated `UNCLEAR` review covered by `policy_unclear_agent_submission_authorized`; it keeps the source classified `UNCLEAR` and still requires the current assessment, actual screening questions, readiness, truthfulness, duplicate, technical-control, and campaign gates to pass.

## Bounded hybrid campaigns

`AUTONOMOUS_CAMPAIGN` uses these repository-owned limits:

```text
minimum desired new outcomes:        8
normal target:                       10
absolute maximum:                    13
plausible raw/normalized inventory:  50 minimum, 100 target when available
human-final-click browser batch:      5-10 tabs
P0 freshness:                         0-7 days
P1 freshness:                         8-30 days
P2 extended strong-match inventory:  31-45 days
```

An outcome is either an autonomous submission backed by confirmation evidence or a fully verified `HUMAN_SUBMIT_READY` application. Keep those metrics separate: human-ready never increments `APPLIED` or verified-submission counts. Stop immediately at 13 combined outcomes. At 8 or more, stop when fresh high-quality inventory has been reasonably exhausted. Search P0 before P1, then consider P2 only for roles that score `STRONG APPLY`. Listings older than 45 days require a separately documented strategic exception. Below 8, stop rather than weakening the remaining eligibility, fit, readiness, truthfulness, source, schedule, or compensation policy.

One blocked job never blocks the campaign. Persist its exact application and queue outcomes, then continue. Required video, inaccessible forms, human-only actions, unsupported consequential declarations, source restrictions, unclear policies, failed verification, inactive listings, and source-policy failures are per-job outcomes.

Review Queue statuses are `HUMAN_SUBMIT_READY`, `READY_FOR_BROWSER_PREP`, `VIDEO_REQUIRED`, `HOLD`, `READY_TO_RETRY`, `SOURCE_RESTRICTED`, `POLICY_UNCLEAR`, `FORM_INACCESSIBLE`, `SUBMISSION_UNVERIFIED`, and `CLOSED`. `SOURCE_RESTRICTED` describes an explicit prohibition. `POLICY_UNCLEAR` applies when no dated review or standing override is available. Once a legitimate manual-only application is complete, its actionable status is `HUMAN_SUBMIT_READY` and source-policy detail remains in its dedicated column.

Every active queue record requires a concrete next action, computed re-review date, and expiry date. Expiry triggers live re-verification; it does not silently claim the listing is closed. Required media, assessment cost, declarations, CAPTCHA, and human verification must be discovered in preflight before application prose is generated.

Source diversity is a discovery control, not a scoring dimension. Prefer underrepresented reputable sources and target a maximum 40 percent single-source share while keeping the same employer, fit, freshness, truthfulness, compensation, and submission-policy gates. All campaign metrics are derived from persisted per-job outcomes.

Before every submission, query the SQLite ledger and Google Sheet for the canonical URL, employer, role, posting ID, description fingerprint, and previous events. Run `SENIOR_POSITIONING_REVIEW` on the complete live payload. Do not retry an unverified submission blindly.
