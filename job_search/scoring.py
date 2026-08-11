from __future__ import annotations

from .models import Assessment, EligibilityResult, FitRubric, Verdict


ELIGIBILITY_CONFIDENCE_CAPS = {
    "APPLICATION_ENTRY_UNAVAILABLE": 92,
    "MATERIAL_REQUIREMENT_GAP": 92,
    "SCREENING_QUESTIONS_UNVERIFIED": 92,
    "TIMEZONE_REQUIREMENT_UNRESOLVED": 92,
    "WORK_AUTHORIZATION_UNRESOLVED": 85,
}

APPLICATION_READINESS_CAPS = {
    "APPLICATION_ENTRY_UNAVAILABLE": 55,
    "CAREER_DIRECTION_MISMATCH": 55,
    "MATERIAL_REQUIREMENT_GAP": 55,
    "SCREENING_ANSWERS_UNRESOLVED": 60,
    "SCREENING_QUESTIONS_UNVERIFIED": 55,
    "TIMEZONE_REQUIREMENT_UNRESOLVED": 60,
    "WORK_AUTHORIZATION_UNRESOLVED": 60,
}


def _capped_signal(proposed: int, reason_codes: list[str], caps: dict[str, int]) -> int:
    if not 0 <= proposed <= 100:
        raise ValueError("confidence and readiness signals must be between 0 and 100")
    applicable_caps = [caps[code] for code in reason_codes if code in caps]
    return min([proposed, *applicable_caps])


def calibrate_eligibility_confidence(proposed: int, reason_codes: list[str]) -> int:
    return _capped_signal(proposed, reason_codes, ELIGIBILITY_CONFIDENCE_CAPS)


def calibrate_application_readiness(proposed: int, reason_codes: list[str]) -> int:
    return _capped_signal(proposed, reason_codes, APPLICATION_READINESS_CAPS)


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


def uncertainty_adjusted_score(base_score: int, eligibility_confidence: int) -> int:
    if not 0 <= base_score <= 100:
        raise ValueError("base score must be between 0 and 100")
    if not 0 <= eligibility_confidence <= 100:
        raise ValueError("eligibility confidence must be between 0 and 100")
    return round(base_score * eligibility_confidence / 100)


def build_assessment(
    *,
    job_id: str,
    eligibility: EligibilityResult,
    rubric: FitRubric | None,
    eligibility_confidence: int,
    application_readiness: int,
    readiness_reason_codes: list[str],
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
    confidence = calibrate_eligibility_confidence(
        eligibility_confidence, readiness_reason_codes
    )
    readiness = calibrate_application_readiness(
        application_readiness, readiness_reason_codes
    )
    if not eligibility.can_score:
        if eligibility.verdict is None:
            raise ValueError("a blocked eligibility result must provide a verdict")
        return Assessment(
            job_id=job_id,
            fit_score=None,
            base_fit_score=None,
            technical_fit_score=None,
            career_direction_fit_score=None,
            eligibility_confidence=None,
            application_readiness=0,
            verdict=eligibility.verdict,
            reason_codes=list(eligibility.reason_codes),
            readiness_reason_codes=list(eligibility.reason_codes),
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
    score = uncertainty_adjusted_score(rubric.total, confidence)
    return Assessment(
        job_id=job_id,
        fit_score=score,
        base_fit_score=rubric.total,
        technical_fit_score=rubric.technical_fit_score,
        career_direction_fit_score=rubric.career_direction_fit_score,
        eligibility_confidence=confidence,
        application_readiness=readiness,
        verdict=verdict_from_score(score),
        reason_codes=[],
        readiness_reason_codes=readiness_reason_codes,
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
