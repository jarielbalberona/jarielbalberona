from __future__ import annotations

import unittest
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from job_search.answers import AnswerStatus, resolve_question
from job_search.candidate import accepts_engagement_type
from job_search.compensation import (
    build_compensation_decision,
    evaluate_compensation,
    evaluate_compensation_range,
    load_compensation_policy,
    select_expected_monthly_php,
    select_expected_range_monthly_php,
)
from job_search.media import MediaRequirement, resolve_candidate_media
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
    def test_canonical_candidate_photo_is_reused_for_required_upload(self) -> None:
        result = resolve_question(
            "candidate_photo",
            "Photo",
            field_type="required_photo",
        )
        self.assertEqual(".job-search/assets/candidate-photo.jpeg", result.answer)
        self.assertEqual(AnswerStatus.EXACT, result.status)
        self.assertFalse(result.blocks_readiness)

    def test_required_introduction_video_holds_without_changing_fit(self) -> None:
        media = resolve_candidate_media(
            "introduction_video", MediaRequirement.REQUIRED
        )
        result = resolve_question(
            "english_introduction_video",
            "Please record a short video to introduce yourself in English",
            field_type="required_introduction_video",
        )
        self.assertEqual("HOLD", media.action)
        self.assertEqual("REQUIRED_VIDEO_INTRO", media.reason_code)
        self.assertIsNone(result.answer)
        self.assertEqual(AnswerStatus.REQUIRED_VIDEO_INTRO, result.status)
        self.assertTrue(result.blocks_readiness)

    def test_optional_photo_requires_application_specific_approval(self) -> None:
        omitted = resolve_candidate_media("photo", MediaRequirement.OPTIONAL)
        approved = resolve_candidate_media(
            "photo",
            MediaRequirement.OPTIONAL,
            optional_use_approved=True,
        )
        self.assertEqual("NONE", omitted.action)
        self.assertEqual("ATTACH", approved.action)

    def test_notice_and_rendering_period_use_canonical_zero_availability(self) -> None:
        notice = resolve_question("notice_period", "What is your notice period?")
        rendering_days = resolve_question(
            "rendering_period_days", "How many days is your rendering period?"
        )
        self.assertEqual("None", notice.answer)
        self.assertEqual("0", rendering_days.answer)
        self.assertEqual(AnswerStatus.EXACT, notice.status)
        self.assertEqual(AnswerStatus.EXACT, rendering_days.status)

    def test_immediate_start_answers_are_canonical(self) -> None:
        start = resolve_question("start_availability", "When can you start?")
        immediate = resolve_question(
            "available_immediately", "Are you available to start immediately?"
        )
        self.assertEqual("Immediately", start.answer)
        self.assertEqual("Yes", immediate.answer)

    def test_required_start_date_uses_application_day(self) -> None:
        result = resolve_question(
            "earliest_start",
            "Earliest available start date?",
            field_type="date",
        )
        expected = datetime.now(ZoneInfo("Asia/Manila")).date().isoformat()
        self.assertEqual(expected, result.answer)
        self.assertEqual(AnswerStatus.EXACT, result.status)

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

    def test_ambiguous_combined_stack_uses_dominant_stack_evidence(self) -> None:
        result = resolve_question(
            "years_stack",
            "How many years is your experience with Next.js, TS, Python (FastAPI), PostgreSQL?",
        )
        self.assertEqual("5", result.answer)
        self.assertEqual(AnswerStatus.BEST_SUPPORTED_ANSWER, result.status)
        self.assertEqual(0.9, result.confidence)
        self.assertIn("Python/FastAPI is secondary", result.interpretation)
        self.assertEqual(5, len(result.supporting_evidence))

    def test_explicit_all_technologies_uses_weakest_depth_semantics(self) -> None:
        result = resolve_question(
            "years_all_stack",
            "How many years have you used ALL of the following technologies professionally: Next.js, TypeScript, Python, FastAPI, and PostgreSQL?",
        )
        self.assertEqual("1", result.answer)
        self.assertEqual(AnswerStatus.CONSERVATIVE_ESTIMATE, result.status)
        self.assertIn("weakest-depth semantics", result.interpretation)

    def test_never_used_technology_cannot_hide_in_combined_stack(self) -> None:
        result = resolve_question(
            "years_stack_with_kotlin",
            "How many years of experience do you have with TypeScript, PostgreSQL, Python, and Kotlin?",
        )
        self.assertIsNone(result.answer)
        self.assertEqual(AnswerStatus.MATERIAL_UNKNOWN, result.status)
        self.assertIn("cannot be hidden", result.interpretation)

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
        self.assertEqual(84, calibrate_application_readiness(100, ["REQUIRED_VIDEO_INTRO"]))

    def test_self_ratings_are_conservative_and_evidence_based(self) -> None:
        core = resolve_question("typescript_rating", "Rate your TypeScript proficiency from 1-10")
        secondary = resolve_question("python_rating", "Select your Python skill level")
        self.assertEqual("8", core.answer)
        self.assertEqual("Intermediate", secondary.answer)
        self.assertEqual(AnswerStatus.CONSERVATIVE_ESTIMATE, core.status)


class CompensationTests(unittest.TestCase):
    def test_hard_and_preferred_minimums_remain_unchanged(self) -> None:
        policy = load_compensation_policy()
        self.assertEqual(160000, policy["employee"]["hard_minimum_monthly_php"])
        self.assertEqual(180000, policy["employee"]["preferred_minimum_monthly_php"])
        self.assertEqual(220000, policy["employee"]["default_strong_senior_monthly_php"])
        self.assertEqual(240000, policy["employee"]["default_ai_native_senior_monthly_php"])
        self.assertIsNone(policy["employee"]["upper_rejection_ceiling_monthly_php"])
        self.assertEqual(200000, policy["contractor"]["hard_minimum_monthly_php"])
        self.assertEqual(220000, policy["contractor"]["preferred_minimum_monthly_php"])
        self.assertEqual(240000, policy["contractor"]["default_strong_senior_monthly_php"])
        self.assertEqual(250000, policy["contractor"]["default_ai_native_senior_monthly_php"])
        self.assertIsNone(policy["contractor"]["upper_rejection_ceiling_monthly_php"])

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

    def test_conversion_friendly_default_anchors(self) -> None:
        self.assertEqual(
            220000,
            select_expected_monthly_php("Full-time employee"),
        )
        self.assertEqual(
            240000,
            select_expected_monthly_php(
                "Full-time employee", strong_ai_alignment=True
            ),
        )
        self.assertEqual(
            240000,
            select_expected_monthly_php("Full-time independent contractor"),
        )
        self.assertEqual(
            250000,
            select_expected_monthly_php(
                "Full-time independent contractor",
                strong_ai_alignment=True,
                philippines_targeted_international=True,
            ),
        )
        self.assertEqual(
            (250000, 250000),
            select_expected_range_monthly_php(
                "Full-time independent contractor", strong_ai_alignment=True
            ),
        )

    def test_staff_ai_without_budget_evidence_does_not_jump_to_300k(self) -> None:
        selected = select_expected_monthly_php(
            "Full-time independent contractor",
            strong_ai_alignment=True,
            staff_scope=True,
        )
        self.assertEqual(275000, selected)
        self.assertLessEqual(selected, 275000)
        self.assertEqual(
            (250000, 275000),
            select_expected_range_monthly_php(
                "Full-time independent contractor",
                strong_ai_alignment=True,
                staff_scope=True,
            ),
        )

    def test_direct_international_staff_rate_can_use_300k(self) -> None:
        self.assertEqual(
            300000,
            select_expected_monthly_php(
                "Full-time independent contractor",
                strong_ai_alignment=True,
                staff_scope=True,
                direct_international_rate=True,
            ),
        )
        self.assertEqual(
            (275000, 300000),
            select_expected_range_monthly_php(
                "Full-time independent contractor",
                strong_ai_alignment=True,
                staff_scope=True,
                direct_international_rate=True,
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

    def test_employer_range_supporting_300k_can_select_300k(self) -> None:
        decision = build_compensation_decision(
            "Full-time independent contractor",
            strong_ai_alignment=True,
            advertised_currency="PHP",
            advertised_min=250000,
            advertised_max=350000,
            advertised_basis="gross_monthly",
        )
        self.assertEqual(300000, decision.submitted_amount)
        self.assertTrue(decision.high_budget_evidence)

    def test_omniflow_override_is_250k_best_supported_answer(self) -> None:
        omniflow = job(
            role="AI Software Engineer (Remote)",
            company="Global Finance Teams",
            destination_company="Omniflow",
            location="Remote in National Capital Region",
            remote_policy="Remote from the Philippines; Monday-Friday PST or EST",
            employment_type="Full-time independent contractor",
        )
        assessment = SimpleNamespace(
            career_direction_fit_score=100,
            narrative="AI-native / agentic engineering",
        )
        result = resolve_question(
            "expected_monthly_service_pay",
            "How much is your expected monthly service pay?",
            job=omniflow,
            assessment=assessment,  # type: ignore[arg-type]
        )
        self.assertEqual("250000", result.answer)
        self.assertEqual(AnswerStatus.BEST_SUPPORTED_ANSWER, result.status)
        decision = result.internal["compensation_decision"]
        self.assertEqual(250000, decision["php_reference_monthly"])
        self.assertEqual("omniflow", decision["policy_override"])
        self.assertTrue(decision["philippines_targeted_international"])

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
