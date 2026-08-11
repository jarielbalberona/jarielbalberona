from __future__ import annotations

import json
import unittest
from pathlib import Path

from job_search.models import CompanyOrigin, FitRubric, Job, Verdict
from job_search.normalization import fingerprint
from job_search.policy import EmployerExclusionMatcher, ExclusionIdentity, evaluate_eligibility
from job_search.scoring import build_assessment, verdict_from_score


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
            rubric=FitRubric(30, 20, 15, 15, 10, 10),
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
