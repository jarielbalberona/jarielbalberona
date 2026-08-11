from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import RunMode


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


class SubmissionController:
    def submit(
        self,
        *,
        run_mode: RunMode,
        source_policy: SourcePolicy,
        unresolved_questions: list[str],
        handler: Callable[[], SubmissionEvidence],
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

        evidence = handler()
        if not evidence.verified:
            return SubmissionEvidence(
                verified=False,
                evidence_type="SUBMISSION_UNVERIFIED",
                detail=evidence.detail,
            )
        return evidence
