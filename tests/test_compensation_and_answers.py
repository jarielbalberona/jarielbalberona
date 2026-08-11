from __future__ import annotations

import unittest

from job_search.answers import AnswerStatus, resolve_question
from job_search.candidate import accepts_engagement_type
from job_search.compensation import (
    build_compensation_decision,
    evaluate_compensation,
    evaluate_compensation_range,
    select_expected_monthly_php,
    select_expected_range_monthly_php,
)
from job_search.models import CompanyOrigin, Job, Verdict
from job_search.policy import EmployerExclusionMatcher, evaluate_eligibility
from job_search.scoring import calibrate_application_readiness


def job(**overrides: object) -> Job:
    values: dict[str, object] = {
        "source": "fixture",
        "role": "Senior Software Engineer",
        "company": "International Product Company",
        "description": "Own a production product platform.",
        "original_url": "https://jobs.example.com/1",
        "company_origin": CompanyOrigin.INTERNATIONAL,
        "remote_from_ph": True,
        "engineering_domain_eligible": True,
        "employment_type": "Full-time employee",
    }
    values.update(overrides)
    return Job(**values)  # type: ignore[arg-type]


class CandidateAvailabilityTests(unittest.TestCase):
    def test_full_time_engagement_types_are_accepted(self) -> None:
        for employment_type in (
            "Full-time employee",
            "Full-time contractor",
            "Full-time independent contractor",
            "Full-time freelance B2B",
            "Full-time consultant",
            "Full-time employer of record",
        ):
            with self.subTest(employment_type=employment_type):
                self.assertTrue(accepts_engagement_type(employment_type))
                eligibility = evaluate_eligibility(
                    job(employment_type=employment_type), EmployerExclusionMatcher([])
                )
                self.assertTrue(eligibility.can_score)

    def test_part_time_is_not_the_primary_engagement(self) -> None:
        self.assertFalse(accepts_engagement_type("Part-time contractor", full_time=False))
        self.assertFalse(accepts_engagement_type("Part-time contractor"))

    def test_weekday_international_schedules_are_eligible(self) -> None:
        for schedule in ("Monday-Friday PST", "Monday-Friday EST", "Monday-Friday UK hours"):
            with self.subTest(schedule=schedule):
                result = evaluate_eligibility(
                    job(work_schedule=schedule, recurring_weekend_work=False),
                    EmployerExclusionMatcher([]),
                )
                self.assertTrue(result.can_score)

    def test_tuesday_to_saturday_is_skipped(self) -> None:
        result = evaluate_eligibility(
            job(work_schedule="Required Tuesday-Saturday"), EmployerExclusionMatcher([])
        )
        self.assertEqual(Verdict.SKIP, result.verdict)
        self.assertEqual(("REQUIRED_WEEKEND_WORK",), result.reason_codes)

    def test_required_recurring_saturday_is_skipped(self) -> None:
        result = evaluate_eligibility(
            job(work_schedule="Regular Saturday shift", recurring_weekend_work=True),
            EmployerExclusionMatcher([]),
        )
        self.assertEqual(("REQUIRED_WEEKEND_WORK",), result.reason_codes)

    def test_unclear_on_call_weekend_language_requires_review(self) -> None:
        result = evaluate_eligibility(
            job(work_schedule="Occasional weekend on-call incidents"),
            EmployerExclusionMatcher([]),
        )
        self.assertEqual(Verdict.REVIEW, result.verdict)
        self.assertEqual(("WEEKEND_WORK_UNVERIFIED",), result.reason_codes)

    def test_foreign_advertised_range_requires_current_php_normalization(self) -> None:
        unresolved = evaluate_eligibility(
            job(
                advertised_compensation_currency="USD",
                advertised_compensation_min=4000,
                advertised_compensation_max=5000,
                advertised_compensation_basis="gross_monthly",
            ),
            EmployerExclusionMatcher([]),
        )
        normalized = evaluate_eligibility(
            job(
                advertised_compensation_currency="USD",
                advertised_compensation_min=4000,
                advertised_compensation_max=5000,
                advertised_compensation_basis="gross_monthly",
                advertised_compensation_monthly_php_min=230000,
                advertised_compensation_monthly_php_max=285000,
                advertised_compensation_exchange_rate_to_php=57.0,
                advertised_compensation_conversion_date="2026-08-11",
            ),
            EmployerExclusionMatcher([]),
        )
        self.assertEqual(("COMPENSATION_CONVERSION_REQUIRED",), unresolved.reason_codes)
        self.assertTrue(normalized.can_score)


class AnswerPolicyTests(unittest.TestCase):
    def test_location_uses_exact_canonical_city_region_and_country(self) -> None:
        result = resolve_question(
            "location_city",
            "Location (City, State/Region, Country)",
        )
        self.assertEqual("Dumaguete City, Negros Oriental, Philippines", result.answer)
        self.assertEqual(AnswerStatus.EXACT, result.status)
        self.assertFalse(result.blocks_readiness)

    def test_generic_ai_numeric_and_free_text_answers(self) -> None:
        numeric = resolve_question("years_ai", "How many years of AI experience do you have?")
        free_text = resolve_question("ai_summary", "Describe your AI experience")
        self.assertEqual("2", numeric.answer)
        self.assertEqual(AnswerStatus.EXACT, numeric.status)
        self.assertEqual("2+ years", free_text.answer)

    def test_narrow_pytorch_question_does_not_reuse_ai_tenure(self) -> None:
        result = resolve_question("years_pytorch", "How many years of PyTorch experience?")
        self.assertIsNone(result.answer)
        self.assertEqual(AnswerStatus.MATERIAL_UNKNOWN, result.status)

    def test_python_and_fastapi_use_conservative_one_year(self) -> None:
        for key, question in (
            ("years_python", "How many years of Python experience?"),
            ("years_fastapi", "How many years of FastAPI experience?"),
        ):
            with self.subTest(key=key):
                result = resolve_question(key, question)
                self.assertEqual("1", result.answer)
                self.assertEqual(AnswerStatus.CONSERVATIVE_ESTIMATE, result.status)

    def test_generic_software_engineering_years_use_canonical_floor(self) -> None:
        result = resolve_question(
            "years_swe", "How many years of professional software engineering experience?"
        )
        self.assertEqual("10", result.answer)

    def test_secondary_framework_estimate_is_resolved(self) -> None:
        result = resolve_question("years_vite", "How many years of Vite experience?")
        self.assertEqual("1", result.answer)
        self.assertEqual(AnswerStatus.CONSERVATIVE_ESTIMATE, result.status)
        self.assertFalse(result.blocks_readiness)

    def test_never_used_technology_is_not_fabricated(self) -> None:
        result = resolve_question("years_kotlin", "How many years of Kotlin experience?")
        self.assertIsNone(result.answer)
        self.assertTrue(result.blocks_readiness)

    def test_ambiguous_combined_stack_uses_supported_interpretation(self) -> None:
        result = resolve_question(
            "years_stack",
            "How many years is your experience with Next.js, TS, Python (FastAPI), PostgreSQL?",
        )
        self.assertEqual("4", result.answer)
        self.assertEqual(AnswerStatus.CONSERVATIVE_ESTIMATE, result.status)
        self.assertIn("not represented as equal", result.interpretation)

    def test_legal_authorization_unknown_is_material(self) -> None:
        result = resolve_question(
            "work_authorization", "Are you authorized to work in the United States?"
        )
        self.assertEqual(AnswerStatus.MATERIAL_UNKNOWN, result.status)

    def test_current_salary_is_unknown_unless_non_disclosure_exists(self) -> None:
        unknown = resolve_question("current_salary", "What is your current salary?")
        non_disclosure = resolve_question(
            "current_salary", "Current salary (you may select Prefer not to disclose)"
        )
        self.assertIsNone(unknown.answer)
        self.assertEqual(AnswerStatus.MATERIAL_UNKNOWN, unknown.status)
        self.assertEqual("Prefer not to disclose", non_disclosure.answer)

    def test_conservative_estimate_does_not_reduce_readiness(self) -> None:
        self.assertEqual(100, calibrate_application_readiness(100, ["CONSERVATIVE_ESTIMATE"]))
        self.assertEqual(
            100, calibrate_application_readiness(100, ["TIMEZONE_REQUIREMENT_UNRESOLVED"])
        )
        self.assertEqual(80, calibrate_application_readiness(100, ["MATERIAL_UNKNOWN"]))

    def test_self_ratings_are_conservative_and_evidence_based(self) -> None:
        core = resolve_question("typescript_rating", "Rate your TypeScript proficiency from 1-10")
        secondary = resolve_question("python_rating", "Select your Python skill level")
        self.assertEqual("8", core.answer)
        self.assertEqual("Intermediate", secondary.answer)
        self.assertEqual(AnswerStatus.CONSERVATIVE_ESTIMATE, core.status)


class CompensationTests(unittest.TestCase):
    def test_employee_compensation_boundaries(self) -> None:
        self.assertEqual(
            Verdict.SKIP, evaluate_compensation(150000, "Full-time employee").verdict
        )
        self.assertEqual(
            Verdict.REVIEW, evaluate_compensation(170000, "Full-time employee").verdict
        )
        self.assertEqual(
            "COMPENSATION_TARGET_MATCH",
            evaluate_compensation(220000, "Full-time employee").reason_code,
        )

    def test_contractor_compensation_boundaries(self) -> None:
        self.assertEqual(
            Verdict.SKIP, evaluate_compensation(180000, "Independent contractor").verdict
        )
        self.assertEqual(
            Verdict.REVIEW, evaluate_compensation(210000, "Independent contractor").verdict
        )
        self.assertEqual(
            "COMPENSATION_TARGET_MATCH",
            evaluate_compensation(250000, "Independent contractor").reason_code,
        )

    def test_high_alignment_ai_contractor_selects_275k(self) -> None:
        selected = select_expected_monthly_php(
            "Full-time independent contractor", strong_ai_alignment=True
        )
        self.assertEqual(275000, selected)
        self.assertEqual(
            (250000, 300000),
            select_expected_range_monthly_php(
                "Full-time independent contractor", strong_ai_alignment=True
            ),
        )

    def test_undisclosed_and_above_target_are_not_blocked(self) -> None:
        undisclosed = evaluate_compensation(None, "Full-time employee")
        above_target = evaluate_compensation(350000, "Full-time employee")
        self.assertIsNone(undisclosed.verdict)
        self.assertEqual("COMPENSATION_UNDISCLOSED", undisclosed.reason_code)
        self.assertIsNone(above_target.verdict)
        self.assertEqual("COMPENSATION_TARGET_MATCH", above_target.reason_code)

    def test_partially_overlapping_range_requires_review(self) -> None:
        result = evaluate_compensation_range(140000, 200000, "Full-time employee")
        self.assertEqual(Verdict.REVIEW, result.verdict)

    def test_foreign_conversion_requires_rate_and_date(self) -> None:
        with self.assertRaises(ValueError):
            build_compensation_decision(
                "Full-time employee", requested_currency="USD"
            )
        decision = build_compensation_decision(
            "Full-time employee",
            requested_currency="USD",
            exchange_rate_from_php=0.017,
            conversion_date="2026-08-11",
        )
        self.assertEqual("2026-08-11", decision.conversion_date)
        self.assertEqual(220000, decision.php_reference_monthly)

    def test_advertised_range_biases_answer_without_anchoring_at_minimum(self) -> None:
        decision = build_compensation_decision(
            "Full-time employee",
            strong_ai_alignment=True,
            advertised_currency="PHP",
            advertised_min=180000,
            advertised_max=250000,
            advertised_basis="gross_monthly",
        )
        self.assertEqual(240000, decision.submitted_amount)
        self.assertEqual(180000, decision.advertised_min)

    def test_advertised_maximum_below_floor_cannot_be_agreed_autonomously(self) -> None:
        with self.assertRaises(ValueError):
            build_compensation_decision(
                "Full-time independent contractor",
                advertised_currency="PHP",
                advertised_min=150000,
                advertised_max=180000,
                advertised_basis="gross_monthly",
            )


if __name__ == "__main__":
    unittest.main()
