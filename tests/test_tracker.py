from __future__ import annotations

import unittest
from datetime import date

from job_search.tracker import (
    HEADERS,
    REVIEW_QUEUE_HEADERS,
    close_review_queue_record,
    format_compensation_for_tracker,
    is_review_queue_due,
    map_record_to_row,
    map_review_queue_record_to_row,
    plan_review_queue_upsert,
    plan_sheet_upsert,
    should_sync_review_queue,
)


def record(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "application_id": "app_123",
        "date_discovered": "2026-08-11",
        "date_applied": "",
        "company": "International Product Company",
        "role": "Senior Software Engineer",
        "source": "Indeed PH",
        "job_url": "https://example.com/job?tracking=1",
        "canonical_job_url": "https://example.com/job",
        "location": "Remote Philippines",
        "remote_policy": "Remote from PH",
        "employment_type": "Full-time",
        "compensation": "",
        "fit_score": 88,
        "verdict": "STRONG APPLY",
        "application_status": "PREPARED",
        "application_method": "Indeed",
        "cv_version": "portfolio/public/jariel-balberona-cv.pdf",
        "application_letter": "Short letter",
        "key_matches": ["TypeScript", "PostgreSQL"],
        "gaps": ["Python is secondary"],
        "recruiter_contact": "",
        "last_response_at": "",
        "response_type": "",
        "next_action": "Review packet",
        "follow_up_date": "",
        "notes": "",
    }
    value.update(overrides)
    return value


def queue_record(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "queue_id": "queue_123",
        "date_discovered": "2026-08-12",
        "last_reviewed": "2026-08-12",
        "company": "International Product Company",
        "role": "Senior Software Engineer",
        "source": "Managed web search",
        "ats": "Workable",
        "job_url": "https://jobs.example.com/view/123?utm_source=search",
        "posted_date": "2026-08-10",
        "job_age": 2,
        "fit_score": 91,
        "verdict": "STRONG APPLY",
        "readiness": 72,
        "queue_status": "HOLD",
        "hold_review_reason": "Required introduction video",
        "next_action": "Record candidate-authored video",
        "compensation": "Advertised: undisclosed | Policy reference: PHP 250,000 monthly",
        "key_matches": ["TypeScript", "Product ownership"],
        "material_gaps": ["Required video"],
        "prepared_screening_answers": {"work_authorization": "Yes"},
        "cover_letter": "A role-specific three-paragraph letter.",
        "cv_version": "portfolio/public/jariel-balberona-cv.pdf",
        "media_requirement": "Video REQUIRED; Photo OPTIONAL",
        "source_ats_policy": "Workable autonomous submission permitted after live verification",
        "re_review_after": "2026-08-14",
        "notes": "Worth preserving.",
    }
    value.update(overrides)
    return value


class TrackerTests(unittest.TestCase):
    def test_review_queue_mapping_is_exactly_a_to_z(self) -> None:
        row = map_review_queue_record_to_row(queue_record())
        self.assertEqual(26, len(REVIEW_QUEUE_HEADERS))
        self.assertEqual(26, len(row))
        self.assertEqual("queue_123", row[0])
        self.assertEqual(91, row[10])
        self.assertEqual("HOLD", row[13])
        self.assertEqual('{"work_authorization": "Yes"}', row[19])

    def test_held_review_queue_sync_is_idempotent(self) -> None:
        existing = [
            map_review_queue_record_to_row(
                queue_record(queue_status="MANUAL_APPLY", notes="Manual review note")
            )
        ]
        plan = plan_review_queue_upsert(
            existing,
            queue_record(queue_status="HOLD", notes="Local note"),
        )
        self.assertEqual("update", plan.action)
        self.assertEqual(2, plan.row_number)
        self.assertEqual("queue_id", plan.matched_by)
        self.assertEqual("MANUAL_APPLY", plan.values[13])
        self.assertEqual("Manual review note", plan.values[25])

    def test_review_queue_matches_canonicalized_job_url(self) -> None:
        existing = [
            map_review_queue_record_to_row(
                queue_record(queue_id="legacy", job_url="https://jobs.example.com/view/123")
            )
        ]
        plan = plan_review_queue_upsert(existing, queue_record(queue_id="new"))
        self.assertEqual("update", plan.action)
        self.assertEqual("job_url", plan.matched_by)

    def test_applied_transition_closes_queue_without_duplicate_application(self) -> None:
        closed = close_review_queue_record(queue_record(), applied_at="2026-08-12")
        existing = [map_review_queue_record_to_row(queue_record())]
        queue_plan = plan_review_queue_upsert(
            existing, closed, preserve_manual=False, force_lifecycle=True
        )
        application_plan = plan_sheet_upsert(
            [map_record_to_row(record(application_status="PREPARED"))],
            record(application_status="APPLIED"),
            preserve_manual=False,
        )
        self.assertEqual("update", queue_plan.action)
        self.assertEqual("CLOSED", queue_plan.values[13])
        self.assertEqual("update", application_plan.action)
        self.assertEqual("APPLIED", application_plan.values[14])

    def test_hard_skip_never_enters_review_queue(self) -> None:
        skipped = queue_record(verdict="SKIP", queue_status="HOLD")
        self.assertFalse(should_sync_review_queue(skipped))
        with self.assertRaises(ValueError):
            plan_review_queue_upsert([], skipped)

    def test_worthwhile_active_queue_record_requires_prepared_cover_letter(self) -> None:
        with self.assertRaisesRegex(ValueError, "prepared cover letter"):
            plan_review_queue_upsert([], queue_record(cover_letter=""))

    def test_new_review_queue_taxonomy_is_accepted_and_legacy_values_are_rejected(self) -> None:
        for queue_status in (
            "MANUAL_APPLY",
            "READY_TO_RETRY",
            "PREPARED",
            "HOLD",
            "VIDEO_REQUIRED",
            "SOURCE_RESTRICTED",
            "FORM_INACCESSIBLE",
            "CLOSED",
        ):
            with self.subTest(queue_status=queue_status):
                self.assertTrue(
                    should_sync_review_queue(
                        queue_record(queue_status=queue_status)
                    )
                )
        for queue_status in ("HELD", "REVIEW", "READY TO APPLY"):
            with self.subTest(queue_status=queue_status):
                self.assertFalse(
                    should_sync_review_queue(
                        queue_record(queue_status=queue_status)
                    )
                )

    def test_due_re_review_excludes_closed_rows(self) -> None:
        self.assertTrue(
            is_review_queue_due(queue_record(re_review_after="2026-08-12"), as_of=date(2026, 8, 12))
        )
        self.assertFalse(
            is_review_queue_due(
                queue_record(queue_status="CLOSED", re_review_after="2026-08-12"),
                as_of=date(2026, 8, 12),
            )
        )

    def test_mapping_is_exactly_a_to_z(self) -> None:
        row = map_record_to_row(record())
        self.assertEqual(26, len(HEADERS))
        self.assertEqual(26, len(row))
        self.assertEqual("app_123", row[0])
        self.assertEqual(88, row[12])
        self.assertEqual("PREPARED", row[14])

    def test_repeated_sync_updates_same_application(self) -> None:
        existing = [map_record_to_row(record(application_status="SHORTLISTED", notes="Manual note"))]
        plan = plan_sheet_upsert(existing, record(application_status="PREPARED", notes="Local note"))
        self.assertEqual("update", plan.action)
        self.assertEqual(2, plan.row_number)
        self.assertEqual("application_id", plan.matched_by)
        self.assertEqual("SHORTLISTED", plan.values[14])
        self.assertEqual("Manual note", plan.values[25])

    def test_new_application_appends(self) -> None:
        plan = plan_sheet_upsert([], record())
        self.assertEqual("append", plan.action)
        self.assertIsNone(plan.row_number)

    def test_compensation_summary_preserves_advertised_and_expected_values(self) -> None:
        summary = format_compensation_for_tracker(
            "Undisclosed",
            {
                "submitted_currency": "PHP",
                "submitted_amount": 275000,
                "requested_basis": "gross_monthly",
            },
        )
        self.assertEqual(
            "Advertised: Undisclosed | Expected/submitted: PHP 275,000 gross monthly",
            summary,
        )


if __name__ == "__main__":
    unittest.main()
