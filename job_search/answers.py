from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
import re
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from .candidate import canonical_country, canonical_location, load_candidate_facts
from .compensation import (
    build_compensation_decision,
    engagement_category,
    select_expected_range_monthly_php,
)
from .models import Assessment, Job


class AnswerStatus(StrEnum):
    EXACT = "EXACT"
    BEST_SUPPORTED_ANSWER = "BEST_SUPPORTED_ANSWER"
    CONSERVATIVE_ESTIMATE = "CONSERVATIVE_ESTIMATE"
    MATERIAL_UNKNOWN = "MATERIAL_UNKNOWN"


@dataclass(frozen=True, slots=True)
class AnswerResolution:
    answer: str | None
    status: AnswerStatus
    confidence: float
    interpretation: str
    supporting_evidence: tuple[str, ...] = ()
    internal: dict[str, Any] = field(default_factory=dict)

    @property
    def blocks_readiness(self) -> bool:
        return self.status == AnswerStatus.MATERIAL_UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        value["supporting_evidence"] = list(self.supporting_evidence)
        return value


def _exact(answer: str, interpretation: str, *evidence: str) -> AnswerResolution:
    return AnswerResolution(answer, AnswerStatus.EXACT, 1.0, interpretation, evidence)


def _estimate(answer: str, interpretation: str, *evidence: str) -> AnswerResolution:
    return AnswerResolution(
        answer,
        AnswerStatus.CONSERVATIVE_ESTIMATE,
        0.8,
        interpretation,
        evidence,
    )


def _best_supported(
    answer: str,
    interpretation: str,
    *evidence: str,
    confidence: float = 0.9,
) -> AnswerResolution:
    return AnswerResolution(
        answer,
        AnswerStatus.BEST_SUPPORTED_ANSWER,
        confidence,
        interpretation,
        evidence,
    )


def _unknown(interpretation: str) -> AnswerResolution:
    return AnswerResolution(None, AnswerStatus.MATERIAL_UNKNOWN, 0.0, interpretation)


def _mentioned_technology_keys(text: str, facts: Mapping[str, Any]) -> list[str]:
    profiles = facts["technology_experience"].get("technology_profiles", {})
    mentioned: list[str] = []
    for key, profile in profiles.items():
        aliases = profile.get("aliases", ())
        if any(re.search(rf"\b{re.escape(str(alias).casefold())}\b", text) for alias in aliases):
            mentioned.append(str(key))
    return mentioned


def _technology_years_answer(
    text: str,
    facts: Mapping[str, Any],
) -> AnswerResolution | None:
    if "years" not in text:
        return None

    technology_experience = facts["technology_experience"]
    profiles = technology_experience.get("technology_profiles", {})
    mentioned = _mentioned_technology_keys(text, facts)
    if not mentioned:
        return None

    unsupported = [key for key in mentioned if not profiles[key].get("used", False)]
    if unsupported:
        return _unknown(
            "A listed technology has no supported professional-use evidence and cannot be hidden by a combined-stack estimate."
        )

    evidence = tuple(
        f"candidate_facts.technology_experience.technology_profiles.{key}"
        for key in mentioned
    )
    if len(mentioned) == 1:
        profile = profiles[mentioned[0]]
        answer = str(profile["numeric_years_floor"])
        interpretation = (
            f"Technology-specific floor for {mentioned[0]}; combined-stack majority evidence is not used."
        )
        status = AnswerStatus(profile["individual_answer_status"])
        if status == AnswerStatus.EXACT:
            return _exact(answer, interpretation, *evidence)
        if status == AnswerStatus.BEST_SUPPORTED_ANSWER:
            return _best_supported(answer, interpretation, *evidence)
        return _estimate(answer, interpretation, *evidence)

    explicit_weakest_link_terms = (
        "all of the following",
        "all the following",
        "each of the following",
        "each technology",
        "every technology",
        "all technologies",
        "used all",
    )
    if any(term in text for term in explicit_weakest_link_terms):
        weakest = min(int(profiles[key]["numeric_years_floor"]) for key in mentioned)
        return _estimate(
            str(weakest),
            "The wording explicitly requires experience across every listed technology, so weakest-depth semantics apply.",
            *evidence,
        )

    mentioned_set = set(mentioned)
    for combined in technology_experience.get("combined_stack_profiles", ()):
        if set(combined["technology_keys"]) == mentioned_set:
            return _best_supported(
                str(combined["dominant_stack_years"]),
                str(combined["interpretation"]),
                *evidence,
                confidence=float(combined.get("confidence", 0.9)),
            )

    return _unknown(
        "The question combines technologies, but no defensible dominant-stack profile exists for this exact combination."
    )


def _compensation_context(job: Job | None) -> tuple[bool, bool, bool, str | None]:
    if job is None:
        return False, False, False, None

    raw = job.raw if isinstance(job.raw, Mapping) else {}
    market_context = str(raw.get("compensation_market_context", "")).casefold()
    philippines_targeted = market_context == "philippines_targeted_international"
    if not philippines_targeted and job.company_origin.value == "INTERNATIONAL":
        targeting_text = f"{job.location} {job.remote_policy}".casefold()
        philippines_targeted = any(
            term in targeting_text
            for term in ("philippines", "national capital region", "metro manila")
        )

    direct_international_rate = (
        market_context == "direct_international_rate"
        or bool(raw.get("direct_international_rate"))
    )
    high_budget_evidence = bool(raw.get("high_budget_compensation_evidence"))
    employer_names = " ".join(
        value
        for value in (
            job.company,
            job.actual_employer,
            job.destination_company,
        )
        if value
    ).casefold()
    policy_override = (
        "omniflow"
        if "omniflow" in employer_names
        and not high_budget_evidence
        and not direct_international_rate
        else None
    )
    return (
        philippines_targeted,
        direct_international_rate,
        high_budget_evidence,
        policy_override,
    )


def resolve_question(
    key: str,
    question: str,
    *,
    supplied_answer: str = "",
    job: Job | None = None,
    assessment: Assessment | None = None,
    field_type: str = "",
) -> AnswerResolution:
    if supplied_answer.strip():
        return _exact(supplied_answer.strip(), "Explicit canonical or application-specific answer.")

    facts = load_candidate_facts()
    text = f"{key} {question}".casefold()

    if "current salary" in text or "current compensation" in text:
        if "prefer not to disclose" in text or "decline to disclose" in text:
            return _exact(
                "Prefer not to disclose",
                "The form provides a legitimate non-disclosure answer.",
            )
        return _unknown("Current compensation has no canonical value and must never be inferred.")

    legal_unknowns = (
        "work authorization",
        "authorised to work",
        "authorized to work",
        "citizenship",
        "visa status",
        "security clearance",
        "criminal",
        "disability",
        "medical declaration",
    )
    if any(term in text for term in legal_unknowns):
        return _unknown(
            "The question requires a personal legal or regulated fact not in canonical context."
        )

    availability = facts["availability"]
    if "notice period" in text or "rendering period" in text or "rendering time" in text:
        if "how many" in text or "days" in text or "numeric" in text:
            return _exact(
                str(availability["notice_period_days"]),
                "Canonical zero-day notice or rendering period.",
                "candidate_facts.availability",
            )
        return _exact(
            str(availability["notice_period"]),
            "Canonical notice and rendering period is none.",
            "candidate_facts.availability",
        )

    if "available to start immediately" in text or "can you start immediately" in text:
        return _exact(
            "Yes" if availability["available_immediately"] else "No",
            "Canonical immediate-start availability.",
            "candidate_facts.availability",
        )

    start_availability_terms = (
        "when can you start",
        "when are you available to start",
        "earliest start",
        "earliest available",
        "start date",
        "available to begin",
    )
    if any(term in text for term in start_availability_terms):
        if field_type.casefold() in {"date", "calendar"}:
            return _exact(
                datetime.now(ZoneInfo("Asia/Manila")).date().isoformat(),
                "Earliest reasonable immediate calendar date for a required date field.",
                "candidate_facts.availability",
            )
        return _exact(
            str(availability["earliest_start"]),
            "Canonical earliest start is immediate.",
            "candidate_facts.availability",
        )

    if "city" in text and ("state" in text or "country" in text):
        return _exact(
            canonical_location(),
            "Canonical city, state or region, and country of residence.",
            "candidate_facts.location",
        )
    if "country" in text and "based" not in text:
        return _exact(canonical_country(), "Canonical country of residence.", "candidate_facts.location")

    engagement_terms = (
        "independent contractor",
        "contractor",
        "freelance",
        "b2b",
        "consultant",
    )
    if any(term in text for term in engagement_terms):
        if "part-time" in text or (job and "part-time" in job.employment_type.casefold()):
            return _exact("No", "Part-time work is not the target engagement.")
        return _exact(
            "Yes",
            "Full-time employee and legitimate full-time non-employee structures are accepted.",
            "candidate_facts.employment_preferences",
        )

    weekend_terms = ("saturday", "sunday", "weekend")
    if any(term in text for term in weekend_terms) and any(
        term in text for term in ("regular", "recurring", "required", "shift")
    ):
        return _exact("No", "Recurring weekend work is outside the canonical schedule.")
    timezone_terms = (
        "pst",
        "pdt",
        "est",
        "edt",
        "cst",
        "mst",
        "uk hours",
        "european",
        "australian",
        "timezone",
    )
    if any(term in text for term in timezone_terms):
        return _exact(
            "Yes",
            "International weekday schedules and substantial timezone overlap are accepted.",
            "candidate_facts.schedule",
        )

    if "remote" in text and any(term in text for term in ("willing", "work", "remote_work")):
        return _exact("Yes", "Remote work is the canonical working model.")
    if "based" in text and "philipp" in text:
        return _exact("Yes", "Canonical country is the Philippines.")
    if "us client" in text or "u.s. client" in text or "american client" in text:
        return _exact("Yes", "Canonical context confirms experience handling US clients.")
    if "portfolio" in text:
        return _exact("https://jarielbalberona.dev", "Canonical portfolio URL.")

    expected_compensation_terms = (
        "expected monthly service pay",
        "expected salary",
        "desired salary",
        "salary expectation",
        "desired compensation",
        "annual compensation",
        "salary range",
        "contractor rate",
        "hourly rate",
    )
    if any(term in text for term in expected_compensation_terms):
        employment_type = job.employment_type if job else "Full-time employee"
        strong_ai = bool(
            assessment
            and assessment.career_direction_fit_score is not None
            and assessment.career_direction_fit_score >= 90
            and (
                "ai" in assessment.narrative.casefold()
                or "agent" in assessment.narrative.casefold()
            )
        )
        staff_scope = bool(job and "staff" in job.role.casefold())
        demanding_timezone = "pst" in text or "est" in text or bool(
            job and any(term in job.remote_policy.casefold() for term in ("pst", "est"))
        )
        (
            philippines_targeted,
            direct_international_rate,
            high_budget_evidence,
            policy_override,
        ) = _compensation_context(job)
        if "range" in text:
            low, high = select_expected_range_monthly_php(
                employment_type,
                strong_ai_alignment=strong_ai,
                staff_scope=staff_scope,
                direct_international_rate=direct_international_rate,
                high_budget_evidence=high_budget_evidence,
            )
            return AnswerResolution(
                f"PHP {low:,}-{high:,} per month",
                AnswerStatus.BEST_SUPPORTED_ANSWER,
                0.9,
                "Job-specific expected range selected from the canonical policy.",
                ("compensation_policy",),
                {
                    "compensation_decision": {
                        "engagement_category": engagement_category(employment_type).value,
                        "php_reference_monthly_min": low,
                        "php_reference_monthly_max": high,
                        "requested_currency": "PHP",
                        "requested_basis": "gross_monthly_range",
                        "submitted_currency": "PHP",
                        "submitted_min": low,
                        "submitted_max": high,
                    }
                },
            )
        if "annual" in text:
            requested_basis = "annual"
        elif "hourly" in text:
            requested_basis = "hourly"
        else:
            requested_basis = "gross_monthly"
        decision = build_compensation_decision(
            employment_type,
            strong_ai_alignment=strong_ai,
            staff_scope=staff_scope,
            demanding_timezone=demanding_timezone,
            philippines_targeted_international=philippines_targeted,
            direct_international_rate=direct_international_rate,
            high_budget_evidence=high_budget_evidence,
            policy_override=policy_override,
            requested_basis=requested_basis,
            advertised_currency=job.advertised_compensation_currency if job else None,
            advertised_min=job.advertised_compensation_min if job else None,
            advertised_max=job.advertised_compensation_max if job else None,
            advertised_basis=job.advertised_compensation_basis if job else None,
        )
        return AnswerResolution(
            str(decision.submitted_amount),
            AnswerStatus.BEST_SUPPORTED_ANSWER,
            0.95,
            "Job-specific expected compensation selected from the canonical policy.",
            ("compensation_policy",),
            {"compensation_decision": decision.to_dict()},
        )

    narrow_ai_terms = ("pytorch", "model training", "llm research", "mlops", "python ml")
    if any(term in text for term in narrow_ai_terms):
        return _unknown("Broad AI tenure cannot be reused for narrower unsupported specialization.")

    technology_years = _technology_years_answer(text, facts)
    if technology_years is not None:
        return technology_years

    broad_ai_terms = (
        "ai experience",
        "experience in ai",
        "years_ai",
        "ai development",
        "ai-assisted",
        "generative ai",
        "ai-enabled",
        "agentic ai",
    )
    if any(term in text for term in broad_ai_terms):
        ai = facts["ai_experience"]
        if "years" in text or key.startswith("years_"):
            return _exact(
                str(ai["numeric_years_when_required"]),
                "Canonical whole-number broad AI experience.",
                "candidate_facts.ai_experience",
            )
        return _exact(
            str(ai["broad_ai_experience"]),
            "Canonical free-text broad AI experience.",
            "candidate_facts.ai_experience",
        )

    rating_terms = ("rate your", "proficiency", "skill level", "self-rating", "self rating")
    if any(term in text for term in rating_terms):
        core_terms = ("typescript", "react", "next.js", "node.js", "postgresql", "aws", "terraform")
        secondary_terms = ("python", "fastapi")
        if any(term in text for term in core_terms):
            answer = "4" if "1-5" in text else "8" if "1-10" in text else "Advanced"
            return _estimate(
                answer,
                "Strong rating below the maximum for a core long-term technology.",
                "canonical CV and project evidence",
            )
        if any(term in text for term in secondary_terms):
            answer = "3" if "1-5" in text else "5" if "1-10" in text else "Intermediate"
            return _estimate(
                answer,
                "Middle rating for real but secondary technology experience.",
                "candidate_facts.technology_experience.python_fastapi",
            )
        return _unknown("No defensible evidence exists for the requested self-rating.")

    software_terms = ("software engineer", "software development", "swe")
    if "years" in text and any(term in text for term in software_terms):
        software = facts["technology_experience"]["professional_software_engineering"]
        return _exact(
            str(software["numeric_years_when_required"]),
            "Canonical conservative whole-number professional software-engineering experience.",
            "canonical CV",
        )

    supported_secondary = ("vite", "tanstack query", "zustand", "drizzle", "playwright")
    if "years" in text and any(term in text for term in supported_secondary):
        return _estimate(
            "1",
            "Lowest defensible whole-year estimate for a secondary technology with real project evidence.",
            "canonical CV and project evidence",
        )

    if "years" in text:
        return _unknown("No defensible professional-duration evidence exists for the named technology.")

    return _unknown("No exact fact or defensible conservative answer is available in canonical context.")


def resolve_questions(
    questions: Mapping[str, str],
    supplied_answers: Mapping[str, str],
    *,
    job: Job | None = None,
    assessment: Assessment | None = None,
    field_types: Mapping[str, str] | None = None,
) -> tuple[
    dict[str, str],
    list[str],
    dict[str, dict[str, Any]],
    dict[str, Any] | None,
]:
    resolved: dict[str, str] = {}
    unresolved: list[str] = []
    metadata: dict[str, dict[str, Any]] = {}
    compensation_decision: dict[str, Any] | None = None

    for key, question in questions.items():
        resolution = resolve_question(
            key,
            question,
            supplied_answer=supplied_answers.get(key, ""),
            job=job,
            assessment=assessment,
            field_type=(field_types or {}).get(key, ""),
        )
        metadata[key] = resolution.to_dict()
        if resolution.answer is not None:
            resolved[key] = resolution.answer
        if resolution.blocks_readiness:
            unresolved.append(question)
        decision = resolution.internal.get("compensation_decision")
        if decision:
            compensation_decision = dict(decision)

    return resolved, unresolved, metadata, compensation_decision
