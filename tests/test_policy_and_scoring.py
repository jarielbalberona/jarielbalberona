from __future__ import annotations

import json
import unittest
from pathlib import Path

from job_search.models import CompanyOrigin, EligibilityResult, FitRubric, Job, Verdict
from job_search.normalization import fingerprint
from job_search.policy import EmployerExclusionMatcher, ExclusionIdentity, evaluate_eligibility
from job_search.scoring import (
    build_assessment,
    calibrate_application_readiness,
    calibrate_eligibility_confidence,
    uncertainty_adjusted_score,
    verdict_from_score,
)


def job(**overrides: object) -> Job:
    values: dict[str, object] = {
        "source": "fixture",
        "role": "Senior Software Engineer",
        "company": "International Product Company",
        "description": "Own product architecture, TypeScript services, React applications, PostgreSQL and delivery.",
        "original_url": "https://jobs.example.com/roles/123",
        "company_origin": CompanyOrigin.INTERNATIONAL,
        "remote_from_ph": True,
        "engineering_domain_eligible": True,
    }
    values.update(overrides)
    return Job(**values)  # type: ignore[arg-type]


def matcher_for(company: str, domain: str = "") -> EmployerExclusionMatcher:
    return EmployerExclusionMatcher(
        [
            ExclusionIdentity(
                "fixture",
                frozenset({fingerprint("company", company)}),
                frozenset({fingerprint("domain", domain)}) if domain else frozenset(),
            )
        ]
    )


class PolicyTests(unittest.TestCase):
    def test_tracked_private_policy_has_three_confidential_identities(self) -> None:
        data = json.loads(
            Path("job_search/policy/employer_exclusions.json").read_text(encoding="utf-8")
        )
        self.assertEqual(3, len(data["identities"]))
        self.assertNotIn("company", " ".join(item["id"] for item in data["identities"]))

    def test_current_employer_direct_role_is_hard_blocked(self) -> None:
        matcher = matcher_for("Confidential Current Employer", "current.example")
        result = evaluate_eligibility(
            job(company="Confidential Current Employer", company_domain="current.example"), matcher
        )
        self.assertEqual(Verdict.SKIP, result.verdict)
        self.assertEqual(("CURRENT_EMPLOYER_EXCLUDED",), result.reason_codes)

    def test_recruiter_role_for_current_employer_is_hard_blocked(self) -> None:
        matcher = matcher_for("Confidential Current Employer")
        result = evaluate_eligibility(
            job(company="International Recruiter", destination_company="Confidential Current Employer"),
            matcher,
        )
        self.assertEqual(("CURRENT_EMPLOYER_EXCLUDED",), result.reason_codes)

    def test_us_company_hiring_remote_ph_is_eligible(self) -> None:
        result = evaluate_eligibility(job(location="Remote Philippines"), matcher_for("Excluded Fixture"))
        self.assertTrue(result.can_score)

    def test_uk_company_with_ph_office_is_eligible(self) -> None:
        result = evaluate_eligibility(
            job(location="Manila office", company_origin_evidence="Headquartered in London"),
            matcher_for("Excluded Fixture"),
        )
        self.assertTrue(result.can_score)

    def test_australian_company_using_ph_eor_is_eligible(self) -> None:
        result = evaluate_eligibility(
            job(remote_policy="Philippine EOR; employer headquartered in Australia"),
            matcher_for("Excluded Fixture"),
        )
        self.assertTrue(result.can_score)

    def test_philippine_headquartered_company_is_skipped(self) -> None:
        result = evaluate_eligibility(
            job(company_origin=CompanyOrigin.PHILIPPINES), matcher_for("Excluded Fixture")
        )
        self.assertEqual(Verdict.SKIP, result.verdict)
        self.assertEqual(("PH_LOCAL_COMPANY",), result.reason_codes)

    def test_ambiguous_origin_is_review(self) -> None:
        result = evaluate_eligibility(
            job(company_origin=CompanyOrigin.AMBIGUOUS), matcher_for("Excluded Fixture")
        )
        self.assertEqual(Verdict.REVIEW, result.verdict)
        self.assertEqual(("COMPANY_ORIGIN_UNVERIFIED",), result.reason_codes)

    def test_hard_blocker_overrides_perfect_rubric(self) -> None:
        eligibility = evaluate_eligibility(
            job(company_origin=CompanyOrigin.PHILIPPINES), matcher_for("Excluded Fixture")
        )
        assessment = build_assessment(
            job_id="job_1",
            eligibility=eligibility,
            rubric=FitRubric(25, 15, 20, 10, 10, 10, 10),
            eligibility_confidence=100,
            application_readiness=100,
            readiness_reason_codes=[],
            real_problem="Perfect technical match",
            strongest_matches=["Everything"],
            relevant_projects=["All"],
            relevant_technologies=["All"],
            legitimate_gaps=[],
            dealbreakers=[],
            narrative="Senior software",
            cv_emphasis="Everything",
            application_angle="Apply",
            interview_risks=[],
        )
        self.assertEqual(Verdict.SKIP, assessment.verdict)
        self.assertIsNone(assessment.fit_score)

    def test_pure_devops_role_cannot_become_strong_from_technical_overlap(self) -> None:
        rubric = FitRubric(
            actual_responsibilities=22,
            architecture_match=14,
            career_direction_fit=6,
            technical_stack=9,
            ai_product_platform_relevance=4,
            seniority_scope=9,
            remote_compatibility=9,
        )
        assessment = build_assessment(
            job_id="job_devops",
            eligibility=EligibilityResult(can_score=True),
            rubric=rubric,
            eligibility_confidence=90,
            application_readiness=55,
            readiness_reason_codes=["MATERIAL_REQUIREMENT_GAP"],
            real_problem="Operate conventional cloud infrastructure.",
            strongest_matches=["AWS", "Terraform", "observability"],
            relevant_projects=["Experience Digital"],
            relevant_technologies=["AWS", "Terraform"],
            legitimate_gaps=["Deep production Kubernetes operations"],
            dealbreakers=[],
            narrative="Platform engineering",
            cv_emphasis="Infrastructure history",
            application_angle="Review only",
            interview_risks=[],
        )
        self.assertEqual(90, assessment.technical_fit_score)
        self.assertEqual(30, assessment.career_direction_fit_score)
        self.assertEqual(66, assessment.fit_score)
        self.assertEqual(Verdict.REVIEW, assessment.verdict)

    def test_eligibility_uncertainty_prevents_near_perfect_score(self) -> None:
        self.assertEqual(80, uncertainty_adjusted_score(100, 80))
        self.assertEqual(88, uncertainty_adjusted_score(96, 92))

    def test_material_unknowns_cap_optimistic_confidence_and_readiness(self) -> None:
        reasons = ["TIMEZONE_REQUIREMENT_UNRESOLVED", "MATERIAL_REQUIREMENT_GAP"]
        self.assertEqual(92, calibrate_eligibility_confidence(100, reasons))
        self.assertEqual(55, calibrate_application_readiness(100, reasons))

    def test_unknown_compensation_alone_does_not_reduce_signals(self) -> None:
        reasons = ["COMPENSATION_EXPECTATION_UNRESOLVED"]
        self.assertEqual(100, calibrate_eligibility_confidence(100, reasons))
        self.assertEqual(100, calibrate_application_readiness(100, reasons))

    def test_verdict_boundaries(self) -> None:
        cases = {
            100: Verdict.STRONG_APPLY,
            85: Verdict.STRONG_APPLY,
            84: Verdict.APPLY,
            75: Verdict.APPLY,
            74: Verdict.REVIEW,
            65: Verdict.REVIEW,
            64: Verdict.SKIP,
            0: Verdict.SKIP,
        }
        for score, expected in cases.items():
            with self.subTest(score=score):
                self.assertEqual(expected, verdict_from_score(score))


if __name__ == "__main__":
    unittest.main()
