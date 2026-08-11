from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import Assessment, RunMode, Verdict


class SubmissionBlocked(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SourcePolicy:
    execution_mode: RunMode
    live_submit: bool
    policy_verified_at: str | None = None


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
    if calibration_stage:
        reasons.append("CALIBRATION_REVIEW_REQUIRED")
        requires_review = True
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
        autonomy_policy: LiveAutonomyPolicy = LiveAutonomyPolicy(),
        campaign_verified_submissions: int = 0,
        campaign_maximum_submissions: int = 13,
    ) -> SubmissionEvidence:
        if run_mode == RunMode.DRY_RUN:
            raise SubmissionBlocked("DRY_RUN blocks the submission handler")
        if run_mode in {RunMode.DISCOVERY_ONLY, RunMode.DISABLED}:
            raise SubmissionBlocked(f"{run_mode.value} does not permit submission")
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
