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
from .media import MediaRequirement, resolve_candidate_media
from .models import Assessment, Job
from .positioning import review_senior_positioning, strengthen_supported_positioning


class AnswerStatus(StrEnum):
    EXACT = "EXACT"
    STRONGEST_SUPPORTED_ANSWER = "STRONGEST_SUPPORTED_ANSWER"
    DIRECT_DEEP = "DIRECT_DEEP"
    DIRECT_WORKING = "DIRECT_WORKING"
    TRANSFERABLE_STRONG = "TRANSFERABLE_STRONG"
    BEST_SUPPORTED_ANSWER = "BEST_SUPPORTED_ANSWER"
    CONSERVATIVE_ESTIMATE = "CONSERVATIVE_ESTIMATE"
    MATERIAL_UNKNOWN = "MATERIAL_UNKNOWN"
    REQUIRED_VIDEO_INTRO = "REQUIRED_VIDEO_INTRO"


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
        return self.status in {
            AnswerStatus.MATERIAL_UNKNOWN,
            AnswerStatus.REQUIRED_VIDEO_INTRO,
        }

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


def _strongest_supported(
    answer: str,
    interpretation: str,
    *evidence: str,
    confidence: float = 0.95,
) -> AnswerResolution:
    return AnswerResolution(
        answer,
        AnswerStatus.STRONGEST_SUPPORTED_ANSWER,
        confidence,
        interpretation,
        evidence,
    )


def _capability_answer(
    answer: str,
    status: AnswerStatus,
    interpretation: str,
    *evidence: str,
    confidence: float = 0.95,
) -> AnswerResolution:
    return AnswerResolution(answer, status, confidence, interpretation, evidence)


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


def _legal_work_answer(
    text: str,
    facts: Mapping[str, Any],
    job: Job | None,
) -> AnswerResolution | None:
    citizenship = facts["citizenship"]
    authorization = facts["work_authorization"]
    philippines = authorization["philippines"]
    united_states = authorization["united_states"]

    philippines_terms = ("philippines", "philippine", "filipino")
    united_states_terms = ("united states", "u.s.", "us work", "usa")
    job_context = " ".join(
        value for value in ((job.location if job else ""), (job.remote_policy if job else "")) if value
    ).casefold()
    is_philippines = any(term in text for term in philippines_terms) or (
        "philipp" in job_context
        and any(term in text for term in ("work visa", "sponsorship", "sponsor"))
    )
    is_united_states = any(term in text for term in united_states_terms)

    if any(term in text for term in ("citizenship country", "country of citizenship")):
        return _exact(
            str(citizenship["country"]),
            "Canonical country of citizenship.",
            "candidate_facts.citizenship.country",
        )

    if "nationality" in text and not is_united_states:
        return _exact(
            str(citizenship["country"]),
            "Canonical nationality for application purposes is Filipino / Philippines.",
            "candidate_facts.citizenship",
        )

    if is_philippines and any(term in text for term in ("citizen", "citizenship", "nationality")):
        return _exact(
            "Yes" if citizenship["filipino_citizen"] else "No",
            "Canonical Filipino citizenship status.",
            "candidate_facts.citizenship.filipino_citizen",
        )

    legal_work_terms = (
        "legally work",
        "legal right to work",
        "work authorization",
        "authorised to work",
        "authorized to work",
        "eligible to work",
    )
    if is_philippines and any(term in text for term in legal_work_terms):
        return _exact(
            "Yes" if philippines["legally_authorized_to_work"] else "No",
            "Canonical legal authorization to work in the Philippines.",
            "candidate_facts.work_authorization.philippines.legally_authorized_to_work",
        )

    sponsorship_terms = ("sponsorship", "sponsor", "work visa")
    if is_philippines and any(term in text for term in sponsorship_terms):
        return _exact(
            "Yes" if philippines["sponsorship_required"] else "No",
            "Canonical Philippines employment-sponsorship requirement.",
            "candidate_facts.work_authorization.philippines.sponsorship_required",
        )

    if is_united_states and any(term in text for term in legal_work_terms):
        boolean_form = any(
            term in text
            for term in ("are you", "do you", "can you", "yes/no", "yes or no")
        )
        answer = "No" if boolean_form else "Not Applicable / located outside the US"
        return _exact(
            answer,
            "Canonical United States work authorization is not applicable because the candidate is located outside the US and is not authorized to work there.",
            "candidate_facts.work_authorization.united_states",
            "candidate_facts.residence.country",
        )

    return None


def _is_boolean_question(text: str) -> bool:
    return any(
        term in text
        for term in (
            "do you have",
            "have you",
            "are you experienced",
            "are you familiar",
            "experience with",
            "experience in",
        )
    ) and not any(term in text for term in ("describe", "how would you", "years"))


def _cms_answer(text: str, facts: Mapping[str, Any]) -> AnswerResolution | None:
    cms_terms = (
        "cms",
        "content management",
        "wordpress",
        "shopify",
        "contentful",
        "sanity",
        "payload",
        "storyblok",
        "strapi",
        "aem",
        "sitecore",
    )
    if not any(term in text for term in cms_terms):
        return None

    cms = facts["cms"]
    for vendor, label in (("aem", "Adobe AEM"), ("sitecore", "Sitecore")):
        if vendor in text:
            if "years" in text:
                return _unknown(
                    f"No defensible professional-duration claim exists for vendor-specific {label} experience."
                )
            return _exact(
                "No",
                f"Canonical CMS policy does not claim meaningful vendor-specific {label} experience.",
                f"candidate_facts.cms.{vendor if vendor == 'sitecore' else 'adobe_aem'}",
            )

    if "wordpress" in text:
        return _capability_answer(
            "Yes" if _is_boolean_question(text) else cms["wordpress"]["summary"],
            AnswerStatus.DIRECT_WORKING,
            "Direct professional WordPress development and integration experience.",
            "candidate_facts.cms.wordpress",
        )

    if "shopify" in text:
        return _capability_answer(
            "Yes" if _is_boolean_question(text) else cms["shopify"]["summary"],
            AnswerStatus.DIRECT_WORKING,
            "Direct professional Shopify and commerce content-management experience.",
            "candidate_facts.cms.shopify",
        )

    named_headless_vendors = ("contentful", "sanity", "payload", "storyblok", "strapi")
    if any(vendor in text for vendor in named_headless_vendors):
        return _unknown(
            "Strong headless CMS architecture does not prove experience with this specific vendor."
        )

    if "headless" in text:
        return _capability_answer(
            "Yes" if _is_boolean_question(text) else cms["headless_cms_architecture"]["summary"],
            AnswerStatus.TRANSFERABLE_STRONG,
            "Strongly transferable headless CMS architecture from custom CMS, API, database, React, Next.js, and admin-interface work; no unsupported vendor specialization is implied.",
            "candidate_facts.cms.headless_cms_architecture",
        )

    if "custom" in text:
        return _capability_answer(
            "Yes" if _is_boolean_question(text) else cms["custom_cms_development"]["summary"],
            AnswerStatus.DIRECT_DEEP,
            "Direct deep custom CMS architecture and implementation experience.",
            "candidate_facts.cms.custom_cms_development",
        )

    if "enterprise" in text:
        answer = "Yes" if _is_boolean_question(text) else (
            "Substantial hands-on CMS engineering experience across custom CMS architecture, "
            "content models, administration and publishing workflows, WordPress, Shopify, APIs, "
            "and database-backed content platforms."
        )
        return _strongest_supported(
            answer,
            "Direct CMS engineering plus strongly transferable enterprise content-platform architecture, without claiming AEM or Sitecore specialization.",
            "candidate_facts.cms.general_cms",
            "candidate_facts.cms.enterprise_cms_concepts",
            confidence=0.97,
        )

    return _capability_answer(
        "Yes" if _is_boolean_question(text) else cms["general_cms"]["summary"],
        AnswerStatus.DIRECT_DEEP,
        "Substantial direct CMS engineering experience, including custom CMS development.",
        "candidate_facts.cms.general_cms",
        "candidate_facts.cms.custom_cms_development",
        confidence=0.99,
    )


def _senior_capability_answer(text: str) -> AnswerResolution | None:
    if "years" in text:
        return None
    capabilities = (
        (
            ("api design", "api architecture", "rest api"),
            "Substantial API design, integration, and production backend experience.",
            "canonical full-stack, REST, Node.js, tRPC, and production API evidence",
        ),
        (
            ("database design", "data modeling", "relational database"),
            "Substantial relational database design and data-modeling experience.",
            "canonical PostgreSQL, MySQL, multi-tenant SaaS, and data-modeling evidence",
        ),
        (
            ("system architecture", "software architecture", "solution architecture"),
            "Substantial hands-on system and product architecture experience.",
            "canonical multi-tenant SaaS, offline-first, cloud, and product-ownership evidence",
        ),
        (
            ("technical leadership", "tech lead", "engineering leadership"),
            "Substantial hands-on technical leadership and architecture ownership.",
            "canonical frontend-lead, founder and CTO, modernization, and architecture evidence",
        ),
        (
            ("client-facing", "client facing", "consulting experience"),
            "Substantial client-facing consulting and international distributed-team experience.",
            "canonical consulting and international client-delivery evidence",
        ),
        (
            ("ci/cd", "continuous integration", "continuous delivery"),
            "Substantial CI/CD, infrastructure automation, and production-delivery experience.",
            "canonical GitHub Actions, Terraform, Docker, cloud, and release evidence",
        ),
        (
            ("agentic ai", "coding agents", "agentic engineering"),
            "Substantial practical AI-native and agentic software-engineering experience.",
            "canonical repository-grounded agent execution and verification-loop evidence",
        ),
    )
    for terms, description, evidence in capabilities:
        if any(term in text for term in terms):
            return _strongest_supported(
                "Yes" if _is_boolean_question(text) else description,
                "Senior capability inferred from documented underlying implementation and ownership evidence.",
                evidence,
            )
    return None


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
        supplied = supplied_answer.strip()
        strengthened = strengthen_supported_positioning(supplied)
        if strengthened != supplied:
            return _strongest_supported(
                strengthened,
                "An evidence-backed weak CMS answer was strengthened before submission.",
                "candidate_facts.cms",
            )
        return _exact(supplied, "Explicit canonical or application-specific answer.")

    facts = load_candidate_facts()
    text = f"{key} {question}".casefold()

    cms_answer = _cms_answer(text, facts)
    if cms_answer is not None:
        return cms_answer

    normalized_field_type = field_type.casefold().replace("-", "_").replace(" ", "_")
    if normalized_field_type in {
        "required_photo",
        "optional_photo",
        "optional_photo_approved",
    }:
        requirement = (
            MediaRequirement.REQUIRED
            if normalized_field_type == "required_photo"
            else MediaRequirement.OPTIONAL
        )
        media = resolve_candidate_media(
            "photo",
            requirement,
            optional_use_approved=normalized_field_type == "optional_photo_approved",
        )
        if media.action == "ATTACH" and media.asset_path:
            return _exact(
                str(media.asset_path),
                "Canonical private candidate photo approved for legitimate job applications.",
                "candidate_facts.candidate_media.photo",
            )
        if requirement == MediaRequirement.OPTIONAL:
            return _exact(
                "",
                "Optional candidate photo omitted because application-specific benefit was not approved.",
                "candidate_facts.candidate_media.photo",
            )
        return _unknown("A required candidate photo is not available in canonical assets.")

    if normalized_field_type == "required_introduction_video":
        media = resolve_candidate_media("introduction_video", MediaRequirement.REQUIRED)
        if media.blocks_readiness:
            return AnswerResolution(
                None,
                AnswerStatus.REQUIRED_VIDEO_INTRO,
                1.0,
                "A candidate-authored introduction video is required, but canonical policy holds the application until that asset exists.",
                ("candidate_facts.candidate_media.required_video_behavior",),
                {"action": media.action, "reason_code": media.reason_code},
            )

    if "current salary" in text or "current compensation" in text:
        if "prefer not to disclose" in text or "decline to disclose" in text:
            return _exact(
                "Prefer not to disclose",
                "The form provides a legitimate non-disclosure answer.",
            )
        return _unknown("Current compensation has no canonical value and must never be inferred.")

    legal_work_answer = _legal_work_answer(text, facts, job)
    if legal_work_answer is not None:
        return legal_work_answer

    legal_unknowns = (
        "work authorization",
        "authorised to work",
        "authorized to work",
        "legally work",
        "eligible to work",
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
    commitments_terms = (
        "upcoming commitments",
        "planned leave",
        "upcoming travel",
        "commitments that would prevent",
        "commitments affecting",
        "scheduling restrictions",
        "anything affecting availability",
    )
    if any(term in text for term in commitments_terms):
        no_commitments = not availability["upcoming_commitments_affecting_work_next_3_months"]
        free_text_types = {"text", "textbox", "textarea", "free_text", "long_text"}
        answer = (
            "No, I don't have any upcoming commitments that would affect my work schedule or availability."
            if normalized_field_type in free_text_types and no_commitments
            else "No" if no_commitments else "Yes"
        )
        return _exact(
            answer,
            "Canonical next-three-month work availability has no affecting commitments.",
            "candidate_facts.availability.upcoming_commitments_affecting_work_next_3_months",
        )

    if "fully available" in text and "schedule" in text:
        return _exact(
            "Yes",
            "Canonical weekday and international-timezone availability supports the required schedule.",
            "candidate_facts.schedule",
            "candidate_facts.availability",
        )
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

    capability_answer = _senior_capability_answer(text)
    if capability_answer is not None:
        return capability_answer

    rating_terms = ("rate your", "proficiency", "skill level", "self-rating", "self rating")
    if any(term in text for term in rating_terms):
        core_terms = ("typescript", "react", "next.js", "node.js", "postgresql", "aws", "terraform")
        secondary_terms = ("python", "fastapi")
        if any(term in text for term in core_terms):
            answer = "4" if "1-5" in text else "8" if "1-10" in text else "Advanced"
            return _strongest_supported(
                answer,
                "Strong senior rating for a core long-term technology without automatically claiming the maximum.",
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
        positioning_review = review_senior_positioning(resolution.answer or "")
        metadata[key]["senior_positioning_review"] = positioning_review.to_dict()
        if resolution.answer is not None:
            resolved[key] = resolution.answer
        if resolution.blocks_readiness:
            unresolved.append(question)
        if not positioning_review.passes:
            unresolved.append(question)
        decision = resolution.internal.get("compensation_decision")
        if decision:
            compensation_decision = dict(decision)

    return resolved, unresolved, metadata, compensation_decision
