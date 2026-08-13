from __future__ import annotations

import re
from typing import Mapping

from .answers import resolve_questions
from .evidence import EvidenceSelection, select_evidence
from .models import ApplicationPacket, Assessment, Job, Verdict
from .normalization import application_id
from .policy import EmployerExclusionMatcher
from .positioning import assert_senior_positioning, strengthen_supported_positioning
from .preflight import ApplicationPreflight


class ConfidentialityError(ValueError):
    pass


def assert_public_safe(text: str, matcher: EmployerExclusionMatcher | None = None) -> None:
    matcher = matcher or EmployerExclusionMatcher.load()
    if matcher.contains_in_text(text):
        raise ConfidentialityError("public application text contains a confidential employer identity")
    if "—" in text or "–" in text:
        raise ValueError("application text must use ordinary ASCII punctuation")


def resolve_application_answers(
    questions: Mapping[str, str],
    canonical_answers: Mapping[str, str],
    *,
    job: Job | None = None,
    assessment: Assessment | None = None,
    field_types: Mapping[str, str] | None = None,
) -> tuple[dict[str, str], list[str]]:
    resolved, unresolved, _, _ = resolve_questions(
        questions,
        canonical_answers,
        job=job,
        assessment=assessment,
        field_types=field_types,
    )
    return resolved, unresolved


def resolve_application_answers_with_metadata(
    questions: Mapping[str, str],
    canonical_answers: Mapping[str, str],
    *,
    job: Job | None = None,
    assessment: Assessment | None = None,
    field_types: Mapping[str, str] | None = None,
) -> tuple[dict[str, str], list[str], dict[str, dict[str, object]], dict[str, object] | None]:
    return resolve_questions(
        questions,
        canonical_answers,
        job=job,
        assessment=assessment,
        field_types=field_types,
    )


def _default_letter(job: Job, assessment: Assessment, evidence: EvidenceSelection) -> str:
    problem = assessment.real_problem.rstrip(".")
    first = evidence.summaries[0].rstrip(".")
    second = evidence.summaries[1].rstrip(".") if len(evidence.summaries) > 1 else ""
    evidence_sentence = f"My relevant work includes {first}."
    if second:
        evidence_sentence += f" I have also handled {second}."
    return (
        f"Hi,\n\nI'm applying for the {job.role} position at {job.employer}. "
        f"The role's focus on {problem} closely matches the production engineering work I have been doing.\n\n"
        f"{evidence_sentence} I bring 10+ years across TypeScript, React, Node.js, PostgreSQL, cloud delivery, "
        "and end-to-end technical ownership, with AI-assisted work bounded by deterministic and runtime verification.\n\n"
        "I'd be interested in discussing how this experience could contribute to the work your team is doing.\n\n"
        "Regards,\nJariel Balberona"
    )


def prepare_application_packet(
    job: Job,
    assessment: Assessment,
    *,
    letter: str | None = None,
    screening_questions: Mapping[str, str] | None = None,
    canonical_answers: Mapping[str, str] | None = None,
    screening_questions_verified: bool = False,
    screening_questions_source: str = "",
    screening_field_types: Mapping[str, str] | None = None,
    matcher: EmployerExclusionMatcher | None = None,
    preflight: ApplicationPreflight | None = None,
) -> ApplicationPacket:
    if preflight is not None and not preflight.can_prepare:
        raise ValueError(f"application preflight blocked preparation: {', '.join(preflight.blockers)}")
    if assessment.verdict not in {Verdict.STRONG_APPLY, Verdict.APPLY, Verdict.REVIEW}:
        raise ValueError("application packets may not be prepared for skipped jobs")
    if assessment.reason_codes:
        raise ValueError("application packets require an assessment without hard blockers")

    selected = select_evidence(job, assessment.narrative)
    final_letter = strengthen_supported_positioning(
        (letter or _default_letter(job, assessment, selected)).strip()
    )
    assert_public_safe(final_letter, matcher)
    positioning_review = assert_senior_positioning(final_letter)
    if re.search(r"\b(i am|i'm) (thrilled|incredibly excited)\b", final_letter, re.IGNORECASE):
        raise ValueError("application text uses prohibited generic enthusiasm")

    resolved, unresolved, answer_metadata, compensation_decision = resolve_application_answers_with_metadata(
        screening_questions or {},
        canonical_answers or {},
        job=job,
        assessment=assessment,
        field_types=screening_field_types,
    )
    return ApplicationPacket(
        application_id=application_id(job),
        job_id=application_id(job),
        company=job.employer,
        role=job.role,
        narrative=selected.narrative,
        selected_evidence=list(selected.projects),
        letter=final_letter,
        screening_plan=resolved,
        unresolved_questions=unresolved,
        gaps=list(assessment.legitimate_gaps),
        reasons=[assessment.real_problem, assessment.application_angle],
        answer_metadata=answer_metadata,
        compensation_decision=compensation_decision,
        screening_questions_verified=screening_questions_verified,
        screening_questions_source=screening_questions_source,
        senior_positioning_review=positioning_review.to_dict(),
    )
