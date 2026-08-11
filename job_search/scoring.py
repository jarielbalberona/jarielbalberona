from __future__ import annotations

from .models import Assessment, EligibilityResult, FitRubric, Verdict


def verdict_from_score(score: int) -> Verdict:
    if not 0 <= score <= 100:
        raise ValueError("fit score must be between 0 and 100")
    if score >= 85:
        return Verdict.STRONG_APPLY
    if score >= 75:
        return Verdict.APPLY
    if score >= 65:
        return Verdict.REVIEW
    return Verdict.SKIP


def build_assessment(
    *,
    job_id: str,
    eligibility: EligibilityResult,
    rubric: FitRubric | None,
    real_problem: str,
    strongest_matches: list[str],
    relevant_projects: list[str],
    relevant_technologies: list[str],
    legitimate_gaps: list[str],
    dealbreakers: list[str],
    narrative: str,
    cv_emphasis: str,
    application_angle: str,
    interview_risks: list[str],
) -> Assessment:
    if not eligibility.can_score:
        if eligibility.verdict is None:
            raise ValueError("a blocked eligibility result must provide a verdict")
        return Assessment(
            job_id=job_id,
            fit_score=None,
            verdict=eligibility.verdict,
            reason_codes=list(eligibility.reason_codes),
            real_problem=real_problem or eligibility.explanation,
            strongest_matches=[],
            relevant_projects=[],
            relevant_technologies=[],
            legitimate_gaps=legitimate_gaps,
            dealbreakers=list(eligibility.reason_codes),
            narrative="",
            cv_emphasis="",
            application_angle="Do not apply.",
            interview_risks=[],
        )

    if rubric is None:
        raise ValueError("eligible jobs require a completed fit rubric")
    score = rubric.total
    return Assessment(
        job_id=job_id,
        fit_score=score,
        verdict=verdict_from_score(score),
        reason_codes=[],
        real_problem=real_problem,
        strongest_matches=strongest_matches,
        relevant_projects=relevant_projects,
        relevant_technologies=relevant_technologies,
        legitimate_gaps=legitimate_gaps,
        dealbreakers=dealbreakers,
        narrative=narrative,
        cv_emphasis=cv_emphasis,
        application_angle=application_angle,
        interview_risks=interview_risks,
        rubric=rubric,
    )
