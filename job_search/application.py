from __future__ import annotations

import re
from typing import Mapping

from .evidence import EvidenceSelection, select_evidence
from .models import ApplicationPacket, Assessment, Job, Verdict
from .normalization import application_id
from .policy import EmployerExclusionMatcher


class ConfidentialityError(ValueError):
    pass


CONSEQUENTIAL_FIELDS = frozenset(
    {
        "salary_expectation",
        "current_salary",
        "notice_period",
        "start_date",
        "work_authorization",
        "visa_status",
        "relocation",
        "team_size",
        "management_scope",
        "years_specific_technology",
        "degree",
        "certification",
    }
)


def assert_public_safe(text: str, matcher: EmployerExclusionMatcher | None = None) -> None:
    matcher = matcher or EmployerExclusionMatcher.load()
    if matcher.contains_in_text(text):
        raise ConfidentialityError("public application text contains a confidential employer identity")
    if "—" in text or "–" in text:
        raise ValueError("application text must use ordinary ASCII punctuation")


def resolve_application_answers(
    questions: Mapping[str, str], canonical_answers: Mapping[str, str]
) -> tuple[dict[str, str], list[str]]:
    resolved: dict[str, str] = {}
    unresolved: list[str] = []
    for key, question in questions.items():
        answer = canonical_answers.get(key, "").strip()
        if answer:
            resolved[key] = answer
        elif key in CONSEQUENTIAL_FIELDS:
            unresolved.append(question)
        else:
            unresolved.append(question)
    return resolved, unresolved


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
    matcher: EmployerExclusionMatcher | None = None,
) -> ApplicationPacket:
    if assessment.verdict not in {Verdict.STRONG_APPLY, Verdict.APPLY, Verdict.REVIEW}:
        raise ValueError("application packets may not be prepared for skipped jobs")
    if assessment.reason_codes:
        raise ValueError("application packets require an assessment without hard blockers")

    selected = select_evidence(job, assessment.narrative)
    final_letter = (letter or _default_letter(job, assessment, selected)).strip()
    assert_public_safe(final_letter, matcher)
    if re.search(r"\b(i am|i'm) (thrilled|incredibly excited)\b", final_letter, re.IGNORECASE):
        raise ValueError("application text uses prohibited generic enthusiasm")

    resolved, unresolved = resolve_application_answers(
        screening_questions or {}, canonical_answers or {}
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
        screening_questions_verified=screening_questions_verified,
        screening_questions_source=screening_questions_source,
    )
