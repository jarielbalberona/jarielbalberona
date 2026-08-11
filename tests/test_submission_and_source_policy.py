from __future__ import annotations

import unittest

from job_search.models import Assessment, RunMode, Verdict
from job_search.source_registry import get_source_policy, load_source_registry
from job_search.submission import (
    SourcePolicy,
    SubmissionBlocked,
    SubmissionController,
    SubmissionEvidence,
    evaluate_live_autonomy,
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
    def test_indeed_registry_is_dry_run_and_not_live_submit(self) -> None:
        registry = load_source_registry()
        self.assertTrue(registry["autonomy_calibration_stage"])
        self.assertEqual(85, registry["strong_apply_readiness_threshold"])
        self.assertEqual(92, registry["apply_readiness_threshold"])
        indeed = registry["sources"]["indeed_ph"]
        self.assertTrue(indeed["dry_run"])
        self.assertFalse(indeed["live_submit"])
        self.assertEqual(RunMode.ASSISTED, get_source_policy("indeed_ph").execution_mode)

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
                source_policy=SourcePolicy(RunMode.AUTONOMOUS, True, "2026-08-11"),
                unresolved_questions=[],
                handler=handler,
            )
        self.assertEqual(0, called)

    def test_unverified_source_blocks_non_dry_submission(self) -> None:
        controller = SubmissionController()
        with self.assertRaises(SubmissionBlocked):
            controller.submit(
                run_mode=RunMode.ASSISTED,
                source_policy=SourcePolicy(RunMode.ASSISTED, False, None),
                unresolved_questions=[],
                handler=lambda: SubmissionEvidence(True, "confirmation-page"),
            )

    def test_strong_apply_can_be_autonomous_after_calibration(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.STRONG_APPLY, 90),
            source_policy=SourcePolicy(RunMode.AUTONOMOUS, True, "2026-08-11"),
            unresolved_questions=[],
            calibration_stage=False,
        )
        self.assertTrue(decision.permitted)
        self.assertFalse(decision.requires_review)

    def test_apply_requires_higher_readiness_for_autonomy(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.APPLY, 91),
            source_policy=SourcePolicy(RunMode.AUTONOMOUS, True, "2026-08-11"),
            unresolved_questions=[],
            calibration_stage=False,
        )
        self.assertFalse(decision.permitted)
        self.assertIn("READINESS_BELOW_AUTONOMY_THRESHOLD", decision.reason_codes)

    def test_review_requires_jariel_review(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.REVIEW, 100),
            source_policy=SourcePolicy(RunMode.AUTONOMOUS, True, "2026-08-11"),
            unresolved_questions=[],
            calibration_stage=False,
        )
        self.assertFalse(decision.permitted)
        self.assertTrue(decision.requires_review)
        self.assertIn("VERDICT_REQUIRES_REVIEW", decision.reason_codes)

    def test_skip_is_never_autonomous(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.SKIP, 100),
            source_policy=SourcePolicy(RunMode.AUTONOMOUS, True, "2026-08-11"),
            unresolved_questions=[],
            calibration_stage=False,
        )
        self.assertFalse(decision.permitted)
        self.assertFalse(decision.requires_review)
        self.assertIn("VERDICT_SKIP", decision.reason_codes)

    def test_calibration_and_unresolved_questions_block_autonomy(self) -> None:
        decision = evaluate_live_autonomy(
            assessment=assessment(Verdict.STRONG_APPLY, 100),
            source_policy=SourcePolicy(RunMode.AUTONOMOUS, True, "2026-08-11"),
            unresolved_questions=["Required salary answer"],
            calibration_stage=True,
        )
        self.assertFalse(decision.permitted)
        self.assertIn("CALIBRATION_REVIEW_REQUIRED", decision.reason_codes)
        self.assertIn("UNRESOLVED_CONSEQUENTIAL_FACT", decision.reason_codes)

    def test_autonomous_controller_enforces_current_assessment(self) -> None:
        controller = SubmissionController()
        result = controller.submit(
            run_mode=RunMode.AUTONOMOUS,
            source_policy=SourcePolicy(RunMode.AUTONOMOUS, True, "2026-08-11"),
            unresolved_questions=[],
            assessment=assessment(Verdict.STRONG_APPLY, 90),
            calibration_stage=False,
            handler=lambda: SubmissionEvidence(True, "confirmation-page"),
        )
        self.assertTrue(result.verified)


if __name__ == "__main__":
    unittest.main()
