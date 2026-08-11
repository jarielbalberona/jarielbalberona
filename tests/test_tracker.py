from __future__ import annotations

import unittest

from job_search.tracker import HEADERS, map_record_to_row, plan_sheet_upsert


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


class TrackerTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
