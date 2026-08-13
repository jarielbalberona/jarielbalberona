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


class HybridExecutionPath(StrEnum):
    AUTO_SUBMIT = "AUTO_SUBMIT"
    HUMAN_FINAL_CLICK = "HUMAN_FINAL_CLICK"
    HUMAN_BROWSER_PREP = "HUMAN_BROWSER_PREP"
    BLOCKED = "BLOCKED"


class HumanSubmissionReconciliation(StrEnum):
    VERIFIED_SUBMITTED = "VERIFIED_SUBMITTED"
    SUBMISSION_UNVERIFIED = "SUBMISSION_UNVERIFIED"
    NOT_SUBMITTED = "NOT_SUBMITTED"
    FAILED = "FAILED"
    DUPLICATE_RISK = "DUPLICATE_RISK"


@dataclass(frozen=True, slots=True)
class SubmissionAuthorization:
    user_authorized_globally: bool = False
    individual_application_approval_required: bool = True
    policy_unclear_agent_submission_authorized: bool = False


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


@dataclass(frozen=True, slots=True)
class HybridExecutionDecision:
    path: HybridExecutionPath
    queue_status: str | None
    reason_codes: tuple[str, ...]


def _policy_unclear_override_allowed(
    source_policy: SourcePolicy,
    submission_authorization: SubmissionAuthorization,
) -> bool:
    """Allow the candidate's agent to act when current applicant terms are silent.

    This is deliberately narrower than treating the source as automation-permitted:
    the source must have a dated policy review, cannot be disabled, and an explicit
    restriction is never overridden.
    """
    return (
        source_policy.applicant_automation_policy == ApplicantAutomationPolicy.UNCLEAR
        and bool(source_policy.policy_verified_at)
        and source_policy.execution_mode != RunMode.DISABLED
        and submission_authorization.user_authorized_globally
        and not submission_authorization.individual_application_approval_required
        and submission_authorization.policy_unclear_agent_submission_authorized
    )


def reconcile_human_submission(
    *,
    human_click_reported: bool,
    confirmation_verified: bool,
    failure_observed: bool = False,
    duplicate_risk: bool = False,
) -> HumanSubmissionReconciliation:
    """Classify a reported human click without treating the report as submission proof."""
    if duplicate_risk:
        return HumanSubmissionReconciliation.DUPLICATE_RISK
    if confirmation_verified:
        return HumanSubmissionReconciliation.VERIFIED_SUBMITTED
    if failure_observed:
        return HumanSubmissionReconciliation.FAILED
    if human_click_reported:
        return HumanSubmissionReconciliation.SUBMISSION_UNVERIFIED
    return HumanSubmissionReconciliation.NOT_SUBMITTED


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
    policy_unclear_override = _policy_unclear_override_allowed(
        source_policy,
        submission_authorization,
    )

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
    elif (
        source_policy.applicant_automation_policy == ApplicantAutomationPolicy.UNCLEAR
        and not policy_unclear_override
    ):
        reasons.append("POLICY_UNCLEAR")
    if source_policy.execution_mode == RunMode.DISABLED:
        reasons.append("SOURCE_EXECUTION_FORBIDDEN")
    elif source_policy.execution_mode != RunMode.AUTONOMOUS and not policy_unclear_override:
        reasons.append("SOURCE_NOT_AUTONOMOUS")
    if (
        (not source_policy.live_submit or not source_policy.policy_verified_at)
        and not policy_unclear_override
    ):
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


def evaluate_hybrid_execution(
    *,
    assessment: Assessment,
    source_policy: SourcePolicy,
    unresolved_questions: list[str],
    calibration_stage: bool,
    submission_authorization: SubmissionAuthorization = SubmissionAuthorization(),
    policy: LiveAutonomyPolicy = LiveAutonomyPolicy(),
    required_video: bool = False,
    genuine_candidate_blocker: bool = False,
    form_accessible: bool = True,
    human_verification_required: bool = False,
    technical_final_click_restricted: bool = False,
    candidate_authored_prose_required: bool = False,
) -> HybridExecutionDecision:
    """Choose autonomous submission, human final click, or a genuine hold.

    Applicant-side policy uncertainty may forbid agent submission, but it does not
    forbid preparing an otherwise complete application for Jariel's final click.
    """
    if required_video:
        return HybridExecutionDecision(
            HybridExecutionPath.BLOCKED,
            "VIDEO_REQUIRED",
            ("REQUIRED_VIDEO_INTRO",),
        )
    if not form_accessible:
        return HybridExecutionDecision(
            HybridExecutionPath.BLOCKED,
            "FORM_INACCESSIBLE",
            ("FORM_INACCESSIBLE",),
        )
    if genuine_candidate_blocker:
        return HybridExecutionDecision(
            HybridExecutionPath.BLOCKED,
            "HOLD",
            ("GENUINE_CANDIDATE_BLOCKER",),
        )
    if candidate_authored_prose_required:
        return HybridExecutionDecision(
            HybridExecutionPath.HUMAN_BROWSER_PREP,
            "READY_FOR_BROWSER_PREP",
            ("SOURCE_REQUIRES_CANDIDATE_AUTHORED_PROSE",),
        )

    autonomy = evaluate_live_autonomy(
        assessment=assessment,
        source_policy=source_policy,
        unresolved_questions=unresolved_questions,
        calibration_stage=calibration_stage,
        submission_authorization=submission_authorization,
        policy=policy,
    )
    if autonomy.permitted and not human_verification_required and not technical_final_click_restricted:
        return HybridExecutionDecision(HybridExecutionPath.AUTO_SUBMIT, None, ())

    human_fallback_reasons = {
        "SOURCE_RESTRICTED",
        "POLICY_UNCLEAR",
        "SOURCE_NOT_AUTONOMOUS",
        "SOURCE_EXECUTION_FORBIDDEN",
    }
    reasons = list(autonomy.reason_codes)
    if human_verification_required:
        reasons.append("HUMAN_VERIFICATION_REQUIRED")
    if technical_final_click_restricted:
        reasons.append("TECHNICAL_FINAL_CLICK_RESTRICTED")
    unique_reasons = tuple(dict.fromkeys(reasons))
    non_fallback_reasons = set(unique_reasons) - human_fallback_reasons - {
        "HUMAN_VERIFICATION_REQUIRED",
        "TECHNICAL_FINAL_CLICK_RESTRICTED",
    }
    if not non_fallback_reasons:
        return HybridExecutionDecision(
            HybridExecutionPath.HUMAN_FINAL_CLICK,
            "HUMAN_SUBMIT_READY",
            unique_reasons,
        )
    return HybridExecutionDecision(
        HybridExecutionPath.BLOCKED,
        "HOLD",
        unique_reasons,
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
        policy_unclear_override = _policy_unclear_override_allowed(
            source_policy,
            submission_authorization,
        )
        if source_policy.applicant_automation_policy == ApplicantAutomationPolicy.RESTRICTED:
            raise SubmissionBlocked("applicant-side source policy explicitly restricts automation")
        if (
            source_policy.applicant_automation_policy == ApplicantAutomationPolicy.UNCLEAR
            and not policy_unclear_override
        ):
            raise SubmissionBlocked("applicant-side source policy is unclear")
        if source_policy.execution_mode == RunMode.DISABLED:
            raise SubmissionBlocked("source execution policy forbids submission")
        if source_policy.execution_mode == RunMode.DISCOVERY_ONLY and not policy_unclear_override:
            raise SubmissionBlocked("source execution policy forbids submission")
        if (
            (not source_policy.live_submit or not source_policy.policy_verified_at)
            and not policy_unclear_override
        ):
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
