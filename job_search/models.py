from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class CompanyOrigin(StrEnum):
    INTERNATIONAL = "INTERNATIONAL"
    PHILIPPINES = "PHILIPPINES"
    AMBIGUOUS = "AMBIGUOUS"


class Verdict(StrEnum):
    STRONG_APPLY = "STRONG APPLY"
    APPLY = "APPLY"
    REVIEW = "REVIEW"
    SKIP = "SKIP"


class RunMode(StrEnum):
    DRY_RUN = "DRY_RUN"
    AUTONOMOUS = "AUTONOMOUS"
    ASSISTED = "ASSISTED"
    DISCOVERY_ONLY = "DISCOVERY_ONLY"
    DISABLED = "DISABLED"


class ApplicationStatus(StrEnum):
    SHORTLISTED = "SHORTLISTED"
    PREPARED = "PREPARED"
    APPLIED = "APPLIED"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    OFFER = "OFFER"
    WITHDRAWN = "WITHDRAWN"
    CLOSED = "CLOSED"


class ResponseType(StrEnum):
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    RECRUITER_CONTACT = "RECRUITER CONTACT"
    REQUEST_FOR_INFORMATION = "REQUEST FOR INFORMATION"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    REJECTION = "REJECTION"
    OFFER = "OFFER"
    OTHER = "OTHER"


@dataclass(slots=True)
class Job:
    source: str
    role: str
    company: str
    description: str
    original_url: str
    company_origin: CompanyOrigin
    location: str = ""
    source_posting_id: str | None = None
    actual_employer: str | None = None
    destination_company: str | None = None
    company_domain: str | None = None
    destination_domain: str | None = None
    company_origin_evidence: str = ""
    remote_policy: str = ""
    remote_from_ph: bool | None = None
    employment_type: str = ""
    compensation: str = ""
    work_schedule: str = ""
    recurring_weekend_work: bool | None = None
    advertised_compensation_currency: str | None = None
    advertised_compensation_min: int | None = None
    advertised_compensation_max: int | None = None
    advertised_compensation_basis: str | None = None
    advertised_compensation_monthly_php_min: int | None = None
    advertised_compensation_monthly_php_max: int | None = None
    advertised_compensation_exchange_rate_to_php: float | None = None
    advertised_compensation_conversion_date: str | None = None
    strategically_exceptional: bool = False
    active: bool = True
    posted_at: str | None = None
    discovered_at: str = field(default_factory=utc_now)
    engineering_domain_eligible: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def employer(self) -> str:
        return self.destination_company or self.actual_employer or self.company

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["company_origin"] = self.company_origin.value
        return value


@dataclass(frozen=True, slots=True)
class FitRubric:
    actual_responsibilities: int
    architecture_match: int
    career_direction_fit: int
    technical_stack: int
    ai_product_platform_relevance: int
    seniority_scope: int
    remote_compatibility: int

    LIMITS = {
        "actual_responsibilities": 25,
        "architecture_match": 15,
        "career_direction_fit": 20,
        "technical_stack": 10,
        "ai_product_platform_relevance": 10,
        "seniority_scope": 10,
        "remote_compatibility": 10,
    }

    def __post_init__(self) -> None:
        for name, limit in self.LIMITS.items():
            value = getattr(self, name)
            if not 0 <= value <= limit:
                raise ValueError(f"{name} must be between 0 and {limit}; got {value}")

    @property
    def total(self) -> int:
        return sum(getattr(self, name) for name in self.LIMITS)

    @property
    def technical_fit_score(self) -> int:
        earned = (
            self.actual_responsibilities
            + self.architecture_match
            + self.technical_stack
            + self.seniority_scope
        )
        return round(earned / 60 * 100)

    @property
    def career_direction_fit_score(self) -> int:
        return round(self.career_direction_fit / self.LIMITS["career_direction_fit"] * 100)

    def to_dict(self) -> dict[str, int]:
        return {name: getattr(self, name) for name in self.LIMITS}


@dataclass(frozen=True, slots=True)
class EligibilityResult:
    can_score: bool
    verdict: Verdict | None = None
    reason_codes: tuple[str, ...] = ()
    explanation: str = ""


@dataclass(slots=True)
class Assessment:
    job_id: str
    fit_score: int | None
    base_fit_score: int | None
    technical_fit_score: int | None
    career_direction_fit_score: int | None
    eligibility_confidence: int | None
    application_readiness: int
    verdict: Verdict
    reason_codes: list[str]
    readiness_reason_codes: list[str]
    real_problem: str
    strongest_matches: list[str]
    relevant_projects: list[str]
    relevant_technologies: list[str]
    legitimate_gaps: list[str]
    dealbreakers: list[str]
    narrative: str
    cv_emphasis: str
    application_angle: str
    interview_risks: list[str]
    rubric: FitRubric | None = None
    scoring_version: str = "career-direction-v2"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["verdict"] = self.verdict.value
        value["rubric"] = self.rubric.to_dict() if self.rubric else None
        return value


@dataclass(slots=True)
class ApplicationPacket:
    application_id: str
    job_id: str
    company: str
    role: str
    narrative: str
    selected_evidence: list[str]
    letter: str
    screening_plan: dict[str, str]
    unresolved_questions: list[str]
    gaps: list[str]
    reasons: list[str]
    answer_metadata: dict[str, dict[str, Any]] = field(default_factory=dict)
    compensation_decision: dict[str, Any] | None = None
    screening_questions_verified: bool = False
    screening_questions_source: str = ""
    cv_version: str = "portfolio/public/jariel-balberona-cv.pdf"
    prepared_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])
