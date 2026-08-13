from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from .models import ApplicationStatus, utc_now
from .time_utils import normalize_utc_timestamp


class ApplicationEventType(StrEnum):
    PREPARED = "PREPARED"
    HUMAN_SUBMIT_READY = "HUMAN_SUBMIT_READY"
    SUBMIT_CLICKED = "SUBMIT_CLICKED"
    SUBMISSION_VERIFIED = "SUBMISSION_VERIFIED"
    SUBMISSION_UNVERIFIED = "SUBMISSION_UNVERIFIED"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    RECRUITER_CONTACT = "RECRUITER_CONTACT"
    REQUEST_FOR_INFORMATION = "REQUEST_FOR_INFORMATION"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    REJECTION = "REJECTION"
    OFFER = "OFFER"
    WITHDRAWN = "WITHDRAWN"
    CLOSED = "CLOSED"
    TRACKER_SYNCED = "TRACKER_SYNCED"
    REVIEW_QUEUE_SYNCED = "REVIEW_QUEUE_SYNCED"
    REVIEW_QUEUE_CLOSED = "REVIEW_QUEUE_CLOSED"
    QUEUE_CLOSED_INACTIVE = "QUEUE_CLOSED_INACTIVE"
    USER_DEFERRED = "USER_DEFERRED"
    MEDIA_ATTACHED_AND_HELD = "MEDIA_ATTACHED_AND_HELD"


EVENT_ALIASES = {
    "APPLICATION_PREPARED_AT_FINAL_BOUNDARY": ApplicationEventType.PREPARED,
    "FORM_PREPARED": ApplicationEventType.PREPARED,
    "SUBMITTED": ApplicationEventType.SUBMIT_CLICKED,
    "HUMAN_CLICK_REPORTED": ApplicationEventType.SUBMIT_CLICKED,
    "SUBMISSION_CONFIRMED": ApplicationEventType.SUBMISSION_VERIFIED,
    "VERIFIED_SUBMITTED": ApplicationEventType.SUBMISSION_VERIFIED,
    "ACKNOWLEDGEMENT_RECEIVED": ApplicationEventType.ACKNOWLEDGEMENT,
}

VERIFIED_SUBMISSION_EVIDENCE_TYPES = frozenset(
    {"ATS_CONFIRMATION_PAGE", "ATS_SUCCESS_STATE", "EMPLOYER_ACKNOWLEDGEMENT_EMAIL"}
)

STATUS_RANK = {
    ApplicationStatus.SHORTLISTED: 0,
    ApplicationStatus.PREPARED: 1,
    ApplicationStatus.HELD: 1,
    ApplicationStatus.HUMAN_SUBMIT_READY: 2,
    ApplicationStatus.SUBMISSION_UNVERIFIED: 3,
    ApplicationStatus.APPLIED: 4,
    ApplicationStatus.ASSESSMENT: 5,
    ApplicationStatus.INTERVIEW: 6,
    ApplicationStatus.REJECTED: 7,
    ApplicationStatus.OFFER: 7,
    ApplicationStatus.WITHDRAWN: 8,
    ApplicationStatus.CLOSED: 8,
}


def canonical_event_type(value: str | ApplicationEventType) -> ApplicationEventType:
    normalized = str(value).strip().upper().replace(" ", "_")
    alias = EVENT_ALIASES.get(normalized)
    return alias if alias is not None else ApplicationEventType(normalized)


def assert_transition(current: ApplicationStatus | None, target: ApplicationStatus) -> None:
    if current is None or current == target:
        return
    if STATUS_RANK[target] < STATUS_RANK[current]:
        raise ValueError(f"application lifecycle may not regress from {current.value} to {target.value}")
    if current in {ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN, ApplicationStatus.CLOSED}:
        raise ValueError(f"terminal application status {current.value} may not transition")


@dataclass(frozen=True, slots=True)
class SubmissionEvidence:
    evidence_type: str
    detail: str
    external_key: str
    occurred_at: str = ""

    def __post_init__(self) -> None:
        if self.evidence_type not in VERIFIED_SUBMISSION_EVIDENCE_TYPES:
            raise ValueError(f"unsupported verified submission evidence: {self.evidence_type}")
        if not self.detail.strip() or not self.external_key.strip():
            raise ValueError("verified submission evidence requires detail and an external key")

    def to_dict(self) -> dict[str, Any]:
        return {
            "verified": True,
            "evidence_type": self.evidence_type,
            "detail": self.detail.strip(),
            "external_key": self.external_key.strip(),
            "occurred_at": normalize_utc_timestamp(self.occurred_at or utc_now()),
        }


def require_applied_evidence(
    target: ApplicationStatus,
    evidence: SubmissionEvidence | Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if target != ApplicationStatus.APPLIED:
        return dict(evidence) if isinstance(evidence, Mapping) else None
    if isinstance(evidence, SubmissionEvidence):
        return evidence.to_dict()
    if not evidence or evidence.get("verified") is not True:
        raise ValueError("APPLIED requires independently verified submission evidence")
    evidence_type = str(evidence.get("evidence_type", ""))
    if evidence_type not in VERIFIED_SUBMISSION_EVIDENCE_TYPES:
        raise ValueError("APPLIED evidence type is not independently verifiable")
    if not str(evidence.get("external_key", "")).strip() or not str(evidence.get("detail", "")).strip():
        raise ValueError("APPLIED evidence requires detail and an external key")
    result = dict(evidence)
    result["occurred_at"] = normalize_utc_timestamp(str(result.get("occurred_at") or utc_now()))
    return result
