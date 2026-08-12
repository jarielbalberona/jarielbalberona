from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Callable

from .models import Assessment, RunMode, Verdict


class SubmissionBlocked(RuntimeError):
    pass


class ApplicantAutomationPolicy(StrEnum):
    PERMITTED = "PERMITTED"
    RESTRICTED = "RESTRICTED"
    UNCLEAR = "UNCLEAR"


@dataclass(frozen=True, slots=True)
class SubmissionAuthorization:
    user_authorized_globally: bool = False
    individual_application_approval_required: bool = True


@dataclass(frozen=True, slots=True)
class SourcePolicy:
    execution_mode: RunMode
    live_submit: bool
    policy_verified_at: str | None = None
    applicant_automation_policy: ApplicantAutomationPolicy = ApplicantAutomationPolicy.UNCLEAR


@dataclass(frozen=True, slots=True)
class SubmissionEvidence:
    verified: bool
    evidence_type: str
    detail: str = ""


@dataclass(frozen=True, slots=True)
class LiveAutonomyPolicy:
    strong_apply_readiness_threshold: int = 85
    apply_readiness_threshold: int = 92


@dataclass(frozen=True, slots=True)
class AutonomyDecision:
    permitted: bool
    requires_review: bool
    reason_codes: tuple[str, ...]


def evaluate_live_autonomy(
    *,
    assessment: Assessment,
    source_policy: SourcePolicy,
    unresolved_questions: list[str],
    calibration_stage: bool,
    submission_authorization: SubmissionAuthorization = SubmissionAuthorization(),
    policy: LiveAutonomyPolicy = LiveAutonomyPolicy(),
) -> AutonomyDecision:
    reasons: list[str] = []
    requires_review = False

    if assessment.reason_codes:
        reasons.extend(assessment.reason_codes)
    if assessment.verdict == Verdict.SKIP:
        reasons.append("VERDICT_SKIP")
    elif assessment.verdict == Verdict.REVIEW:
        reasons.append("VERDICT_REQUIRES_REVIEW")
        requires_review = True
    if unresolved_questions:
        reasons.append("UNRESOLVED_CONSEQUENTIAL_FACT")
        requires_review = True
    if not submission_authorization.user_authorized_globally:
        reasons.append("GLOBAL_USER_AUTHORIZATION_MISSING")
        requires_review = True
    if submission_authorization.individual_application_approval_required:
        reasons.append("INDIVIDUAL_APPLICATION_APPROVAL_REQUIRED")
        requires_review = True
    if calibration_stage and submission_authorization.individual_application_approval_required:
        reasons.append("CALIBRATION_REVIEW_REQUIRED")
        requires_review = True
    if source_policy.applicant_automation_policy == ApplicantAutomationPolicy.RESTRICTED:
        reasons.append("SOURCE_RESTRICTED")
    elif source_policy.applicant_automation_policy == ApplicantAutomationPolicy.UNCLEAR:
        reasons.append("POLICY_UNCLEAR")
    if source_policy.execution_mode != RunMode.AUTONOMOUS:
        reasons.append("SOURCE_NOT_AUTONOMOUS")
    if not source_policy.live_submit or not source_policy.policy_verified_at:
        reasons.append("SOURCE_EXECUTION_FORBIDDEN")

    threshold = (
        policy.strong_apply_readiness_threshold
        if assessment.verdict == Verdict.STRONG_APPLY
        else policy.apply_readiness_threshold
    )
    if assessment.verdict in {Verdict.STRONG_APPLY, Verdict.APPLY}:
        if assessment.application_readiness < threshold:
            reasons.append("READINESS_BELOW_AUTONOMY_THRESHOLD")
            requires_review = True

    unique_reasons = tuple(dict.fromkeys(reasons))
    return AutonomyDecision(
        permitted=not unique_reasons,
        requires_review=requires_review,
        reason_codes=unique_reasons,
    )


class SubmissionController:
    def submit(
        self,
        *,
        run_mode: RunMode,
        source_policy: SourcePolicy,
        unresolved_questions: list[str],
        handler: Callable[[], SubmissionEvidence],
        assessment: Assessment | None = None,
        calibration_stage: bool = True,
        submission_authorization: SubmissionAuthorization = SubmissionAuthorization(),
        autonomy_policy: LiveAutonomyPolicy = LiveAutonomyPolicy(),
        campaign_verified_submissions: int = 0,
        campaign_maximum_submissions: int = 13,
    ) -> SubmissionEvidence:
        if run_mode == RunMode.DRY_RUN:
            raise SubmissionBlocked("DRY_RUN blocks the submission handler")
        if run_mode in {RunMode.DISCOVERY_ONLY, RunMode.DISABLED}:
            raise SubmissionBlocked(f"{run_mode.value} does not permit submission")
        if not submission_authorization.user_authorized_globally:
            raise SubmissionBlocked("global candidate submission authorization is not enabled")
        if submission_authorization.individual_application_approval_required:
            raise SubmissionBlocked("individual application approval is required")
        if source_policy.applicant_automation_policy == ApplicantAutomationPolicy.RESTRICTED:
            raise SubmissionBlocked("applicant-side source policy explicitly restricts automation")
        if source_policy.applicant_automation_policy == ApplicantAutomationPolicy.UNCLEAR:
            raise SubmissionBlocked("applicant-side source policy is unclear")
        if source_policy.execution_mode in {RunMode.DISCOVERY_ONLY, RunMode.DISABLED}:
            raise SubmissionBlocked("source execution policy forbids submission")
        if not source_policy.live_submit or not source_policy.policy_verified_at:
            raise SubmissionBlocked("live submission is not verified and enabled for this source")
        if unresolved_questions:
            raise SubmissionBlocked("consequential application questions remain unresolved")
        if run_mode == RunMode.AUTONOMOUS_CAMPAIGN:
            if campaign_verified_submissions >= campaign_maximum_submissions:
                raise SubmissionBlocked("campaign maximum verified submissions reached")
        if run_mode in {RunMode.AUTONOMOUS, RunMode.AUTONOMOUS_CAMPAIGN}:
            if assessment is None:
                raise SubmissionBlocked("autonomous submission requires a current assessment")
            decision = evaluate_live_autonomy(
                assessment=assessment,
                source_policy=source_policy,
                unresolved_questions=unresolved_questions,
                calibration_stage=calibration_stage,
                submission_authorization=submission_authorization,
                policy=autonomy_policy,
            )
            if not decision.permitted:
                raise SubmissionBlocked(
                    "autonomous submission blocked: " + ", ".join(decision.reason_codes)
                )

        evidence = handler()
        if not evidence.verified:
            return SubmissionEvidence(
                verified=False,
                evidence_type="SUBMISSION_UNVERIFIED",
                detail=evidence.detail,
            )
        return evidence
