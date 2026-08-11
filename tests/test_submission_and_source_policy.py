from __future__ import annotations

import unittest

from job_search.models import RunMode
from job_search.source_registry import get_source_policy, load_source_registry
from job_search.submission import (
    SourcePolicy,
    SubmissionBlocked,
    SubmissionController,
    SubmissionEvidence,
)


class SubmissionTests(unittest.TestCase):
    def test_indeed_registry_is_dry_run_and_not_live_submit(self) -> None:
        registry = load_source_registry()
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


if __name__ == "__main__":
    unittest.main()
