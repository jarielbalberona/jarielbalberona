from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from job_search.ledger import Ledger
from job_search.models import ApplicationPacket, ApplicationStatus, CompanyOrigin, Job
from job_search.normalization import canonicalize_url


def fixture_job(source: str, url: str, source_id: str) -> Job:
    return Job(
        source=source,
        source_posting_id=source_id,
        role="Senior Product Engineer",
        company="International Systems Inc",
        description="Own the same production platform across TypeScript, Node.js, React and PostgreSQL.",
        original_url=url,
        company_origin=CompanyOrigin.INTERNATIONAL,
        remote_from_ph=True,
        engineering_domain_eligible=True,
    )


class DeduplicationTests(unittest.TestCase):
    def test_review_queue_persists_once_and_applied_transition_closes_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "ledger.sqlite"
            with Ledger(db) as ledger:
                ledger.initialize()
                stored_job = fixture_job(
                    "workable", "https://jobs.example.com/review", "review"
                )
                job_id, _ = ledger.upsert_job(stored_job)
                queue = {
                    "queue_id": job_id,
                    "job_id": job_id,
                    "company": stored_job.company,
                    "role": stored_job.role,
                    "source": stored_job.source,
                    "ats": "Workable",
                    "job_url": stored_job.original_url,
                    "fit_score": 91,
                    "verdict": "STRONG APPLY",
                    "readiness": 70,
                    "queue_status": "HOLD",
                    "hold_review_reason": "Consequential answer pending",
                    "cover_letter": "A role-specific letter.",
                    "re_review_after": "2026-08-12",
                }
                ledger.upsert_review_queue(queue)
                ledger.upsert_review_queue({**queue, "readiness": 75})
                self.assertEqual(1, ledger.table_count("review_queue"))
                self.assertEqual(
                    75, ledger.list_review_queue(due_on_or_before="2026-08-12")[0]["readiness"]
                )

                packet = ApplicationPacket(
                    application_id=job_id,
                    job_id=job_id,
                    company=stored_job.company,
                    role=stored_job.role,
                    narrative="Senior product engineering",
                    selected_evidence=["Ordr.now"],
                    letter="A role-specific letter.",
                    screening_plan={},
                    unresolved_questions=[],
                    gaps=[],
                    reasons=[],
                )
                ledger.upsert_application(packet, ApplicationStatus.APPLIED)
                row = ledger.list_review_queue()[0]
                self.assertEqual("CLOSED", row["queue_status"])
                self.assertEqual(0, len(ledger.list_review_queue(include_closed=False)))

    def test_tracking_parameters_are_removed_but_job_identity_is_preserved(self) -> None:
        result = canonicalize_url(
            "https://ph.indeed.com/viewjob?jk=abc123&utm_source=email&from=serp"
        )
        self.assertEqual("https://ph.indeed.com/viewjob?jk=abc123", result)

    def test_same_underlying_job_from_two_sources_is_one_job(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "ledger.sqlite"
            with Ledger(db) as ledger:
                ledger.initialize()
                first_id, first_duplicate = ledger.upsert_job(
                    fixture_job("indeed_ph", "https://ph.indeed.com/viewjob?jk=abc", "abc")
                )
                second_id, second_duplicate = ledger.upsert_job(
                    fixture_job("linkedin", "https://linkedin.com/jobs/view/999", "999")
                )
                self.assertFalse(first_duplicate)
                self.assertTrue(second_duplicate)
                self.assertEqual(first_id, second_id)
                self.assertEqual(1, ledger.table_count("jobs"))
                self.assertEqual(2, ledger.table_count("job_sources"))

    def test_compensation_answer_metadata_and_schedule_are_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "ledger.sqlite"
            with Ledger(db) as ledger:
                ledger.initialize()
                stored_job = fixture_job(
                    "indeed_ph", "https://ph.indeed.com/viewjob?jk=comp", "comp"
                )
                stored_job.employment_type = "Full-time independent contractor"
                stored_job.compensation = "Undisclosed"
                stored_job.work_schedule = "Monday-Friday PST"
                stored_job.recurring_weekend_work = False
                job_id, _ = ledger.upsert_job(stored_job)
                packet = ApplicationPacket(
                    application_id=job_id,
                    job_id=job_id,
                    company=stored_job.company,
                    role=stored_job.role,
                    narrative="AI-native / agentic engineering",
                    selected_evidence=["Ordr.now"],
                    letter="A truthful letter.",
                    screening_plan={"expected_pay": "275000"},
                    unresolved_questions=[],
                    gaps=[],
                    reasons=[],
                    answer_metadata={
                        "expected_pay": {"status": "BEST_SUPPORTED_ANSWER"}
                    },
                    compensation_decision={
                        "submitted_currency": "PHP",
                        "submitted_amount": 275000,
                        "requested_basis": "gross_monthly",
                    },
                )
                ledger.upsert_application(packet, ApplicationStatus.PREPARED)

                job_row = ledger.connection.execute(
                    "SELECT work_schedule, recurring_weekend_work, compensation FROM jobs WHERE job_id = ?",
                    (job_id,),
                ).fetchone()
                application_row = ledger.connection.execute(
                    "SELECT answer_metadata_json, compensation_decision_json FROM applications WHERE application_id = ?",
                    (job_id,),
                ).fetchone()
                self.assertEqual("Monday-Friday PST", job_row["work_schedule"])
                self.assertEqual(0, job_row["recurring_weekend_work"])
                self.assertEqual("Undisclosed", job_row["compensation"])
                self.assertIn("BEST_SUPPORTED_ANSWER", application_row["answer_metadata_json"])
                self.assertIn("275000", application_row["compensation_decision_json"])

                ledger.upsert_application(packet, ApplicationStatus.HELD)
                updated_status = ledger.connection.execute(
                    "SELECT status FROM applications WHERE application_id = ?",
                    (job_id,),
                ).fetchone()["status"]
                self.assertEqual(ApplicationStatus.HELD.value, updated_status)

    def test_media_requirement_audit_is_persisted_and_queryable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "ledger.sqlite"
            with Ledger(db) as ledger:
                ledger.initialize()
                stored_job = fixture_job(
                    "direct", "https://jobs.example.com/media", "media"
                )
                job_id, _ = ledger.upsert_job(stored_job)
                ledger.upsert_application_media_requirement(
                    job_id=job_id,
                    application_url="https://jobs.example.com/media/apply",
                    ats="Fixture ATS",
                    video_requirement="REQUIRED",
                    photo_requirement="OPTIONAL",
                    video_prompt="Introduce yourself.",
                    video_method="upload_or_record",
                    evidence={"form_inspected": True},
                    inspected_at="2026-08-12T00:00:00+08:00",
                )

                self.assertEqual(1, ledger.table_count("application_media_requirements"))
                row = ledger.list_application_media_requirements()[0]
                self.assertEqual("REQUIRED", row["video_requirement"])
                self.assertEqual("OPTIONAL", row["photo_requirement"])
                self.assertEqual("Fixture ATS", row["ats"])
                self.assertIn("form_inspected", row["evidence_json"])


if __name__ == "__main__":
    unittest.main()
