from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

from job_search.answers import AnswerStatus, resolve_question, resolve_questions
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

    def test_explicit_no_recurring_weekend_requirement_is_not_a_false_positive(self) -> None:
        result = evaluate_eligibility(
            job(
                work_schedule="No recurring weekend requirement disclosed",
                recurring_weekend_work=False,
            ),
            EmployerExclusionMatcher([]),
        )
        self.assertTrue(result.can_score)

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
    def test_canonical_philippine_residence_shape_is_persisted(self) -> None:
        facts = json.loads(
            Path("job_search/policy/candidate_facts.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {
                "country": "Philippines",
                "city": "Dumaguete City",
                "region": "Negros Oriental",
                "state_or_region": "Negros Oriental",
            },
            facts["residence"],
        )

    def test_philippine_citizenship_and_work_authorization_are_exact(self) -> None:
        citizenship = resolve_question(
            "filipino_citizen", "Are you a Filipino citizen?"
        )
        country = resolve_question(
            "citizenship_country", "What is your country of citizenship?"
        )
        nationality = resolve_question("nationality", "What is your nationality?")
        authorization = resolve_question(
            "ph_work_authorization",
            "Are you legally authorized to work in the Philippines?",
        )
        teamified = resolve_question(
            "based_and_can_legally_work_in_philippines",
            "Are you based and can legally work in The Philippines?",
        )
        sponsorship = resolve_question(
            "ph_sponsorship", "Will you require sponsorship to work in the Philippines?"
        )

        self.assertEqual("Yes", citizenship.answer)
        self.assertEqual("Philippines", country.answer)
        self.assertEqual("Philippines", nationality.answer)
        self.assertEqual("Yes", authorization.answer)
        self.assertEqual("Yes", teamified.answer)
        self.assertEqual("No", sponsorship.answer)
        self.assertTrue(
            all(
                result.status == AnswerStatus.EXACT
                for result in (
                    citizenship,
                    country,
                    nationality,
                    authorization,
                    teamified,
                    sponsorship,
                )
            )
        )

    def test_philippines_job_work_visa_question_uses_job_context(self) -> None:
        result = resolve_question(
            "work_visa",
            "Do you need a work visa?",
            job=job(location="Philippines", remote_policy="Remote in the Philippines"),
        )
        self.assertEqual("No", result.answer)
        self.assertEqual(AnswerStatus.EXACT, result.status)

    def test_united_states_work_authorization_is_not_generalized_from_ph_status(self) -> None:
        boolean = resolve_question(
            "us_work_authorization",
            "Are you legally authorized to work in the United States?",
        )
        status = resolve_question(
            "us_work_authorization_status", "US work authorization status"
        )
        canada = resolve_question(
            "canada_work_authorization",
            "Are you legally authorized to work in Canada?",
        )

        self.assertEqual("No", boolean.answer)
        self.assertEqual("Not Applicable / located outside the US", status.answer)
        self.assertEqual(AnswerStatus.EXACT, boolean.status)
        self.assertEqual(AnswerStatus.MATERIAL_UNKNOWN, canada.status)

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

    def test_upcoming_commitments_are_canonically_resolved(self) -> None:
        boolean = resolve_question(
            "upcoming_commitments",
            "Do you have any upcoming commitments over the next three months?",
        )
        free_text = resolve_question(
            "upcoming_commitments",
            "Do you have any upcoming commitments over the next three months that could affect your work schedule or availability?",
            field_type="textbox",
        )
        fully_available = resolve_question(
            "schedule_availability",
            "Are you fully available for the required schedule?",
        )
        self.assertEqual("No", boolean.answer)
        self.assertEqual(
            "No, I don't have any upcoming commitments that would affect my work schedule or availability.",
            free_text.answer,
        )
        self.assertEqual("Yes", fully_available.answer)
        self.assertEqual(AnswerStatus.EXACT, boolean.status)

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
        self.assertIn("2+ years of practical AI-product", free_text.answer or "")
        self.assertEqual(AnswerStatus.STRONGEST_SUPPORTED_ANSWER, free_text.status)

    def test_cms_capability_is_strong_without_vendor_overclaim(self) -> None:
        general = resolve_question("cms", "Do you have CMS experience?")
        custom = resolve_question(
            "custom_cms", "Describe your custom content management experience"
        )
        wordpress = resolve_question(
            "wordpress", "Do you have professional WordPress experience?"
        )
        shopify = resolve_question(
            "shopify", "Do you have professional Shopify experience?"
        )
        headless = resolve_question(
            "headless_cms", "Do you have headless CMS architecture experience?"
        )
        aem = resolve_question(
            "aem", "Do you have deep hands-on Adobe AEM experience?"
        )
        contentful = resolve_question(
            "contentful", "Do you have Contentful experience?"
        )
        self.assertEqual("Yes", general.answer)
        self.assertEqual(AnswerStatus.DIRECT_DEEP, general.status)
        self.assertEqual(AnswerStatus.DIRECT_DEEP, custom.status)
        self.assertEqual("Yes", wordpress.answer)
        self.assertEqual(AnswerStatus.DIRECT_WORKING, wordpress.status)
        self.assertEqual("Yes", shopify.answer)
        self.assertEqual(AnswerStatus.DIRECT_WORKING, shopify.status)
        self.assertEqual("Yes", headless.answer)
        self.assertEqual(AnswerStatus.TRANSFERABLE_STRONG, headless.status)
        self.assertEqual("No", aem.answer)
        self.assertEqual(AnswerStatus.EXACT, aem.status)
        self.assertIsNone(contentful.answer)
        self.assertEqual(AnswerStatus.MATERIAL_UNKNOWN, contentful.status)

    def test_enterprise_cms_uses_strongest_supported_framing(self) -> None:
        result = resolve_question(
            "enterprise_cms",
            "How would you describe your hands-on experience with enterprise content management systems?",
        )
        self.assertEqual(AnswerStatus.STRONGEST_SUPPORTED_ANSWER, result.status)
        self.assertIn("Substantial hands-on CMS engineering", result.answer or "")
        self.assertNotIn("eager to learn", (result.answer or "").casefold())

    def test_documented_senior_capabilities_resolve_strongly(self) -> None:
        api = resolve_question(
            "api_design", "Do you have substantial API design experience?"
        )
        architecture = resolve_question(
            "system_architecture", "Describe your system architecture experience"
        )
        self.assertEqual("Yes", api.answer)
        self.assertEqual(AnswerStatus.STRONGEST_SUPPORTED_ANSWER, api.status)
        self.assertIn("Substantial hands-on system", architecture.answer or "")

    def test_known_weak_cms_answer_is_strengthened_before_review(self) -> None:
        resolved, unresolved, metadata, _ = resolve_questions(
            {"cms": "Describe your CMS experience"},
            {
                "cms": "I have limited or no direct CMS experience, but I am eager to learn and grow in this area."
            },
        )
        self.assertIn("substantial hands-on CMS engineering", resolved["cms"])
        self.assertEqual([], unresolved)
        self.assertEqual(
            "STRONGEST_SUPPORTED_ANSWER", metadata["cms"]["status"]
        )
        self.assertEqual(
            "PASS", metadata["cms"]["senior_positioning_review"]["status"]
        )

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

    def test_canonical_us_legal_authorization_is_exact_no(self) -> None:
        result = resolve_question(
            "work_authorization", "Are you authorized to work in the United States?"
        )
        self.assertEqual("No", result.answer)
        self.assertEqual(AnswerStatus.EXACT, result.status)

    def test_current_and_previous_salary_use_distinct_canonical_facts(self) -> None:
        current = resolve_question("current_salary", "What is your current salary?")
        numeric_current = resolve_question(
            "current_salary", "What is your current salary?", field_type="number"
        )
        private_fixture = {"previous_salary": {"monthly_php": 123456}}
        with patch(
            "job_search.answers.load_private_candidate_facts",
            return_value=private_fixture,
        ):
            previous = resolve_question(
                "previous_salary", "What was your most recent monthly salary?"
            )
            numeric_previous = resolve_question(
                "previous_salary",
                "What was your most recent monthly salary?",
                field_type="number",
            )
        self.assertEqual("Not currently applicable / not currently employed", current.answer)
        self.assertEqual("0", numeric_current.answer)
        self.assertEqual("PHP 123,456/month", previous.answer)
        self.assertEqual("123456", numeric_previous.answer)
        self.assertTrue(
            all(
                result.status == AnswerStatus.EXACT
                for result in (current, numeric_current, previous, numeric_previous)
            )
        )

    def test_answer_bank_is_loaded_before_generated_fallbacks(self) -> None:
        result = resolve_question(
            "background_check", "Are you willing to undergo a background check?"
        )
        self.assertEqual("Yes", result.answer)
        self.assertEqual(AnswerStatus.EXACT, result.status)
        self.assertIn("application_answer_bank.background_check", result.supporting_evidence[0])

    def test_employment_engagement_and_external_commitments_are_canonical(self) -> None:
        questions = (
            ("currently_employed", "Are you currently employed?", "No"),
            ("seeking", "Are you actively seeking full-time employment?", "Yes"),
            ("full_time", "Are you available to work full time?", "Yes"),
            ("hours", "Can you commit 40 hours per week?", "Yes"),
            (
                "outside_work",
                "Do you have outside projects that would interfere with your responsibilities?",
                "No",
            ),
            (
                "exclusivity",
                "Can you comply with an exclusivity requirement?",
                "Yes",
            ),
            (
                "side_business",
                "Would you cease a side business if exclusivity is required?",
                "Yes",
            ),
        )
        for key, question, answer in questions:
            with self.subTest(key=key):
                result = resolve_question(key, question)
                self.assertEqual(answer, result.answer)
                self.assertEqual(AnswerStatus.EXACT, result.status)

    def test_schedule_and_remote_setup_use_verified_thresholds(self) -> None:
        self.assertEqual(
            "Yes",
            resolve_question("schedule", "Can you work Monday-Friday AEST?").answer,
        )
        self.assertEqual(
            "Yes",
            resolve_question(
                "on_call", "Can you provide occasional emergency weekend on-call support?"
            ).answer,
        )
        self.assertEqual(
            "Yes - secondary internet provider and mobile data",
            resolve_question("backup_internet", "Do you have backup internet?").answer,
        )
        exact_speed = resolve_question(
            "internet_speed", "Do you have at least 25 Mbps backup internet?"
        )
        reported_speed = resolve_question(
            "internet_speed", "What is your backup internet speed?"
        )
        eight_hour_power = resolve_question(
            "power_runtime", "Can your backup power support at least 8 hours?"
        )
        exact_runtime = resolve_question(
            "power_runtime",
            "How many hours of backup power runtime do you have?",
            field_type="number",
        )
        self.assertEqual("Yes", exact_speed.answer)
        self.assertEqual("100 Mbps", reported_speed.answer)
        self.assertEqual("Yes", eight_hour_power.answer)
        self.assertEqual("8", exact_runtime.answer)
        self.assertEqual(AnswerStatus.EXACT, exact_speed.status)
        self.assertEqual(AnswerStatus.EXACT, exact_runtime.status)

        above_verified = resolve_question(
            "internet_speed", "Do you have at least 150 Mbps backup internet?"
        )
        self.assertEqual(AnswerStatus.MATERIAL_UNKNOWN, above_verified.status)
        recurring_weekend = resolve_question(
            "weekend_schedule", "Can you work a recurring weekend schedule?"
        )
        self.assertEqual("No", recurring_weekend.answer)
        self.assertEqual(AnswerStatus.EXACT, recurring_weekend.status)

    def test_private_legal_identity_resolves_without_public_literal(self) -> None:
        private_fixture = {
            "legal_identity": {
                "full_legal_name": "Private Legal Fixture",
                "mailing_address": {"formatted": "Private Address Fixture"},
            }
        }
        with patch(
            "job_search.answers.load_private_candidate_facts",
            return_value=private_fixture,
        ):
            legal_name = resolve_question(
                "legal_name", "Please provide your full legal birth name."
            )
            address = resolve_question(
                "mailing_address", "Please provide your full mailing address."
            )
        self.assertEqual(private_fixture["legal_identity"]["full_legal_name"], legal_name.answer)
        self.assertEqual(
            private_fixture["legal_identity"]["mailing_address"]["formatted"],
            address.answer,
        )
        self.assertEqual(AnswerStatus.EXACT, legal_name.status)
        self.assertEqual(AnswerStatus.EXACT, address.status)

    def test_professional_name_remains_public_safe(self) -> None:
        result = resolve_question("full_name", "What is your full name?")
        self.assertEqual("Jariel Balberona", result.answer)
        self.assertEqual(AnswerStatus.EXACT, result.status)

    def test_llm_mobility_travel_and_passport_answers_are_canonical(self) -> None:
        questions = (
            (
                "llm_providers",
                "Which LLM providers have you used professionally?",
                "OpenAI, Anthropic Claude, and Google Gemini",
            ),
            ("relocation", "Are you willing to relocate?", "Yes"),
            ("travel", "Are you willing to travel internationally for business?", "Yes"),
            ("passport", "Do you have a valid passport?", "Yes"),
        )
        for key, question, expected in questions:
            with self.subTest(key=key):
                result = resolve_question(key, question)
                self.assertEqual(expected, result.answer)
                self.assertEqual(AnswerStatus.EXACT, result.status)

    def test_senior_working_style_and_collaboration_are_not_undersold(self) -> None:
        questions = (
            ("independent", "Can you work independently with ambiguous requirements?"),
            ("mentoring", "Have you mentored engineers?"),
            ("architecture", "Have you owned architecture decisions?"),
            ("reviews", "Do you review pull requests and give engineering feedback?"),
            ("distributed", "Have you worked with global remote teams?"),
            ("stakeholders", "Do you communicate directly with business stakeholders?"),
            ("startup", "Are you comfortable in a fast-moving environment with changing requirements?"),
        )
        for key, question in questions:
            with self.subTest(key=key):
                result = resolve_question(key, question)
                self.assertEqual("Yes", result.answer)
                self.assertEqual(AnswerStatus.STRONGEST_SUPPORTED_ANSWER, result.status)

    def test_screening_terms_assessments_equipment_and_consent_are_canonical(self) -> None:
        questions = (
            ("reference_check", "Are you willing to undergo a reference check?", "Yes"),
            ("nda", "Will you sign an NDA or confidentiality agreement?", "Yes"),
            ("noncompete", "Can you accept a reasonable non-compete?", "Yes"),
            ("nonsolicit", "Can you accept a reasonable non-solicitation clause?", "Yes"),
            ("exclusive", "Can you accept reasonable exclusivity?", "Yes"),
            ("conflict", "Will you comply with a conflict of interest policy?", "Yes"),
            ("live_coding", "Are you willing to complete a live coding interview?", "Yes"),
            ("assessment", "Are you willing to complete a technical assessment?", "Yes"),
            ("system_design", "Are you willing to complete a system design interview?", "Yes"),
            ("own_device", "Can you use your own device?", "Yes"),
            ("suitable_equipment", "Do you already have suitable equipment?", "Yes"),
            ("employer_device", "Do you require an employer-provided computer?", "No"),
            ("provided_device", "Are you willing to use employer-provided equipment?", "Yes"),
            ("dedicated_workspace", "Do you have a dedicated workspace?", "Yes"),
            ("quiet_workspace", "Do you have a quiet workspace?", "Yes"),
            ("talent_pool", "Do you consent to retention in our talent pool?", "Yes"),
        )
        for key, question, expected in questions:
            with self.subTest(key=key):
                result = resolve_question(key, question)
                self.assertEqual(expected, result.answer)
                self.assertEqual(AnswerStatus.EXACT, result.status)

    def test_communication_screening_and_free_text_templates_are_reusable(self) -> None:
        self.assertEqual(
            "9",
            resolve_question("english", "Rate your English proficiency 1-10").answer,
        )
        self.assertEqual(
            "Yes, upon request",
            resolve_question("references", "Are professional references available?").answer,
        )
        self.assertEqual(
            "Yes",
            resolve_question(
                "marketing", "Do you consent to marketing communications?"
            ).answer,
        )
        why_hire = resolve_question("why_hire", "Why should we hire you?")
        self.assertIn("10+ years", why_hire.answer or "")
        self.assertEqual(AnswerStatus.STRONGEST_SUPPORTED_ANSWER, why_hire.status)

    def test_updated_react_and_typescript_years_are_exact(self) -> None:
        react = resolve_question("react_years", "How many years of React experience?")
        typescript = resolve_question(
            "typescript_years", "How many years of TypeScript experience?"
        )
        self.assertEqual("10", react.answer)
        self.assertEqual("8", typescript.answer)
        self.assertEqual(AnswerStatus.EXACT, react.status)
        self.assertEqual(AnswerStatus.EXACT, typescript.status)

    def test_remote_ph_sponsorship_is_best_supported_when_job_is_verified(self) -> None:
        result = resolve_question(
            "visa_sponsorship",
            "Will you now or in the future require visa sponsorship?",
            job=job(location="Remote worldwide", remote_from_ph=True),
        )
        self.assertEqual("No", result.answer)
        self.assertEqual(AnswerStatus.BEST_SUPPORTED_ANSWER, result.status)

    def test_conservative_estimate_does_not_reduce_readiness(self) -> None:
        self.assertEqual(100, calibrate_application_readiness(100, ["CONSERVATIVE_ESTIMATE"]))
        self.assertEqual(
            100, calibrate_application_readiness(100, ["TIMEZONE_REQUIREMENT_UNRESOLVED"])
        )
        self.assertEqual(80, calibrate_application_readiness(100, ["MATERIAL_UNKNOWN"]))
        self.assertEqual(84, calibrate_application_readiness(100, ["REQUIRED_VIDEO_INTRO"]))

    def test_self_ratings_are_strong_and_evidence_based(self) -> None:
        core = resolve_question("typescript_rating", "Rate your TypeScript proficiency from 1-10")
        secondary = resolve_question("python_rating", "Select your Python skill level")
        self.assertEqual("8", core.answer)
        self.assertEqual("Intermediate", secondary.answer)
        self.assertEqual(AnswerStatus.STRONGEST_SUPPORTED_ANSWER, core.status)
        self.assertEqual(AnswerStatus.CONSERVATIVE_ESTIMATE, secondary.status)


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
