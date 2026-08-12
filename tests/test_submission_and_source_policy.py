from __future__ import annotations

import unittest

from job_search.models import Assessment, RunMode, Verdict
from job_search.campaign import (
    CampaignPolicy,
    CampaignStopReason,
    FreshnessBucket,
    classify_freshness,
    evaluate_campaign_progress,
)
from job_search.source_registry import (
    get_source_policy,
    get_submission_authorization,
    load_source_registry,
)
from job_search.submission import (
    ApplicantAutomationPolicy,
    SourcePolicy,
    SubmissionAuthorization,
    SubmissionBlocked,
    SubmissionController,
    SubmissionEvidence,
    evaluate_live_autonomy,
)


GLOBAL_AUTHORIZATION = SubmissionAuthorization(
    user_authorized_globally=True,
    individual_application_approval_required=False,
)


def assessment(verdict: Verdict, readiness: int) -> Assessment:
    return Assessment(
        job_id="job_1",
        fit_score=88,
        base_fit_score=96,
        technical_fit_score=95,
        career_direction_fit_score=100,
        eligibility_confidence=92,
        application_readiness=readiness,
        verdict=verdict,
        reason_codes=[],
        readiness_reason_codes=[],
        real_problem="Build a production AI product.",
        strongest_matches=["Agentic systems"],
        relevant_projects=["Ordr.now"],
        relevant_technologies=["TypeScript"],
        legitimate_gaps=[],
        dealbreakers=[],
        narrative="AI-native / agentic engineering",
        cv_emphasis="Product delivery",
        application_angle="Lead with governed agent execution.",
        interview_risks=[],
    )


class SubmissionTests(unittest.TestCase):
    def test_registry_enables_only_verified_workable_autonomy(self) -> None:
        registry = load_source_registry()
        self.assertFalse(registry["autonomy_calibration_stage"])
        self.assertEqual("AUTONOMOUS_CAMPAIGN", registry["default_run_mode"])
        self.assertEqual(85, registry["strong_apply_readiness_threshold"])
        self.assertEqual(92, registry["apply_readiness_threshold"])
        self.assertEqual(GLOBAL_AUTHORIZATION, get_submission_authorization())
        indeed = registry["sources"]["indeed_ph"]
        self.assertFalse(indeed["live_submit"])
        self.assertEqual("RESTRICTED", indeed["applicant_automation_policy"])
        self.assertEqual(RunMode.DISCOVERY_ONLY, get_source_policy("indeed_ph").execution_mode)
        self.assertFalse(registry["sources"]["greenhouse"]["live_submit"])
        self.assertEqual(
            "UNCLEAR", registry["sources"]["greenhouse"]["applicant_automation_policy"]
        )
        self.assertFalse(registry["sources"]["ashby"]["live_submit"])
        self.assertEqual("2026-08-12", registry["sources"]["ashby"]["policy_verified_at"])
        self.assertFalse(registry["sources"]["lever"]["live_submit"])
        self.assertEqual("2026-08-12", registry["sources"]["lever"]["policy_verified_at"])
        self.assertFalse(registry["sources"]["teamtailor"]["live_submit"])
        self.assertEqual(
            RunMode.DISCOVERY_ONLY,
            get_source_policy("teamtailor").execution_mode,
        )
        self.assertFalse(registry["sources"]["breezy"]["live_submit"])
        self.assertTrue(registry["sources"]["workable"]["live_submit"])
        self.assertEqual("PERMITTED", registry["sources"]["workable"]["applicant_automation_policy"])
        self.assertEqual(RunMode.AUTONOMOUS, get_source_policy("workable").execution_mode)

    def test_dry_run_never_executes_submission_handler(self) -> None:
        called = 0

        def handler() -> SubmissionEvidence:
            nonlocal called
            called += 1
            return SubmissionEvidence(True, "confirmation-page")

        controller = SubmissionController()
        with self.assertRaises(SubmissionBlocked):
            controller.submit(
                run_mode=RunMode.DRY_RUN,
                source_policy=SourcePolicy(
                    RunMode.AUTONOMOUS,
                    True,
                    "2026-08-11",
                    ApplicantAutomationPolicy.PERMITTED,
                ),
                unresolved_questions=[],
                handler=handler,
                submission_authorization=GLOBAL_AUTHORIZATION,
            )
        self.assertEqual(0, called)

    def test_unverified_source_blocks_non_dry_submission(self) -> None:
        controller = SubmissionController()
        with self.assertRaises(SubmissionBlocked):
            controller.submit(
                run_mode=RunMode.ASSISTED,
                source_policy=SourcePolicy(
                    RunMode.ASSISTED,
                    False,
                    None,
                    ApplicantAutomationPolicy.PERMITTED,
                ),
                unresolved_questions=[],
                handler=lambda: SubmissionEvidence(True, "confirmation-page"),
                submission_authorization=GLOBAL_AUTHORIZATION,
            )

    def test_strong_apply_can_be_autonomous_after_calibration(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.STRONG_APPLY, 90),
            source_policy=SourcePolicy(
                RunMode.AUTONOMOUS,
                True,
                "2026-08-11",
                ApplicantAutomationPolicy.PERMITTED,
            ),
            unresolved_questions=[],
            calibration_stage=False,
            submission_authorization=GLOBAL_AUTHORIZATION,
        )
        self.assertTrue(decision.permitted)
        self.assertFalse(decision.requires_review)

    def test_apply_requires_higher_readiness_for_autonomy(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.APPLY, 91),
            source_policy=SourcePolicy(
                RunMode.AUTONOMOUS,
                True,
                "2026-08-11",
                ApplicantAutomationPolicy.PERMITTED,
            ),
            unresolved_questions=[],
            calibration_stage=False,
            submission_authorization=GLOBAL_AUTHORIZATION,
        )
        self.assertFalse(decision.permitted)
        self.assertIn("READINESS_BELOW_AUTONOMY_THRESHOLD", decision.reason_codes)

    def test_review_requires_jariel_review(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.REVIEW, 100),
            source_policy=SourcePolicy(
                RunMode.AUTONOMOUS,
                True,
                "2026-08-11",
                ApplicantAutomationPolicy.PERMITTED,
            ),
            unresolved_questions=[],
            calibration_stage=False,
            submission_authorization=GLOBAL_AUTHORIZATION,
        )
        self.assertFalse(decision.permitted)
        self.assertTrue(decision.requires_review)
        self.assertIn("VERDICT_REQUIRES_REVIEW", decision.reason_codes)

    def test_skip_is_never_autonomous(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.SKIP, 100),
            source_policy=SourcePolicy(
                RunMode.AUTONOMOUS,
                True,
                "2026-08-11",
                ApplicantAutomationPolicy.PERMITTED,
            ),
            unresolved_questions=[],
            calibration_stage=False,
            submission_authorization=GLOBAL_AUTHORIZATION,
        )
        self.assertFalse(decision.permitted)
        self.assertFalse(decision.requires_review)
        self.assertIn("VERDICT_SKIP", decision.reason_codes)

    def test_global_authorization_removes_calibration_approval_but_not_unresolved_questions(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.STRONG_APPLY, 100),
            source_policy=SourcePolicy(
                RunMode.AUTONOMOUS,
                True,
                "2026-08-11",
                ApplicantAutomationPolicy.PERMITTED,
            ),
            unresolved_questions=["Required salary answer"],
            calibration_stage=True,
            submission_authorization=GLOBAL_AUTHORIZATION,
        )
        self.assertFalse(decision.permitted)
        self.assertNotIn("CALIBRATION_REVIEW_REQUIRED", decision.reason_codes)
        self.assertNotIn("INDIVIDUAL_APPLICATION_APPROVAL_REQUIRED", decision.reason_codes)
        self.assertIn("UNRESOLVED_CONSEQUENTIAL_FACT", decision.reason_codes)

    def test_missing_global_authorization_blocks_autonomy(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.STRONG_APPLY, 100),
            source_policy=SourcePolicy(
                RunMode.AUTONOMOUS,
                True,
                "2026-08-12",
                ApplicantAutomationPolicy.PERMITTED,
            ),
            unresolved_questions=[],
            calibration_stage=False,
        )
        self.assertFalse(decision.permitted)
        self.assertIn("GLOBAL_USER_AUTHORIZATION_MISSING", decision.reason_codes)

    def test_restricted_and_unclear_platform_policies_are_distinct(self) -> None:
        for policy_status, reason in (
            (ApplicantAutomationPolicy.RESTRICTED, "SOURCE_RESTRICTED"),
            (ApplicantAutomationPolicy.UNCLEAR, "POLICY_UNCLEAR"),
        ):
            with self.subTest(policy_status=policy_status):
                decision = evaluate_live_autonomy(
                    assessment=assessment(Verdict.STRONG_APPLY, 100),
                    source_policy=SourcePolicy(
                        RunMode.AUTONOMOUS,
                        True,
                        "2026-08-12",
                        policy_status,
                    ),
                    unresolved_questions=[],
                    calibration_stage=False,
                    submission_authorization=GLOBAL_AUTHORIZATION,
                )
                self.assertFalse(decision.permitted)
                self.assertIn(reason, decision.reason_codes)

    def test_autonomous_controller_enforces_current_assessment(self) -> None:
        controller = SubmissionController()
        result = controller.submit(
            run_mode=RunMode.AUTONOMOUS,
            source_policy=SourcePolicy(
                RunMode.AUTONOMOUS,
                True,
                "2026-08-11",
                ApplicantAutomationPolicy.PERMITTED,
            ),
            unresolved_questions=[],
            assessment=assessment(Verdict.STRONG_APPLY, 90),
            calibration_stage=False,
            submission_authorization=GLOBAL_AUTHORIZATION,
            handler=lambda: SubmissionEvidence(True, "confirmation-page"),
        )
        self.assertTrue(result.verified)

    def test_campaign_controller_enforces_verified_submission_cap(self) -> None:
        controller = SubmissionController()
        with self.assertRaisesRegex(SubmissionBlocked, "campaign maximum"):
            controller.submit(
                run_mode=RunMode.AUTONOMOUS_CAMPAIGN,
                source_policy=SourcePolicy(
                    RunMode.AUTONOMOUS,
                    True,
                    "2026-08-12",
                    ApplicantAutomationPolicy.PERMITTED,
                ),
                unresolved_questions=[],
                assessment=assessment(Verdict.STRONG_APPLY, 95),
                calibration_stage=False,
                submission_authorization=GLOBAL_AUTHORIZATION,
                campaign_verified_submissions=13,
                handler=lambda: SubmissionEvidence(True, "confirmation-page"),
            )

    def test_campaign_freshness_and_stop_conditions(self) -> None:
        self.assertEqual(
            (3, FreshnessBucket.P0_FRESH),
            classify_freshness("2026-08-09", "2026-08-12"),
        )
        self.assertEqual(
            (10, FreshnessBucket.P1_RECENT),
            classify_freshness("2026-08-02", "2026-08-12"),
        )
        self.assertEqual(
            CampaignStopReason.QUALITY_LIMITED_INVENTORY_EXHAUSTED,
            evaluate_campaign_progress(
                verified_submitted=5,
                quality_inventory_exhausted=True,
            ).stop_reason,
        )
        self.assertEqual(
            CampaignStopReason.MAXIMUM_VERIFIED_SUBMISSIONS,
            evaluate_campaign_progress(
                verified_submitted=CampaignPolicy().maximum_new_submissions,
                quality_inventory_exhausted=False,
            ).stop_reason,
        )


if __name__ == "__main__":
    unittest.main()
