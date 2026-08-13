from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from job_search.ledger import Ledger
from job_search.lifecycle import SubmissionEvidence, canonical_event_type
from job_search.media import MediaRequirement
from job_search.models import ApplicationPacket, ApplicationStatus, CompanyOrigin, Job, RunMode
from job_search.monitoring import build_read_only_gmail_plan
from job_search.normalization import normalize_source_key
from job_search.preflight import evaluate_application_preflight
from job_search.source_registry import plan_diverse_discovery_rotation, resolve_source_id
from job_search.time_utils import manila_display, normalize_utc_timestamp
from job_search.tracker import plan_sheet_upsert


def packet_for(job_id: str) -> ApplicationPacket:
    return ApplicationPacket(
        application_id=job_id,
        job_id=job_id,
        company="International Product Co",
        role="Senior Product Engineer",
        narrative="Production product engineering",
        selected_evidence=["Ordr.now"],
        letter="A supported role-specific letter.",
        screening_plan={},
        unresolved_questions=[],
        gaps=[],
        reasons=[],
    )


class ControlPlaneHardeningTests(unittest.TestCase):
    def test_applied_requires_verified_evidence_and_closes_queue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with Ledger(Path(directory) / "ledger.sqlite") as ledger:
                ledger.initialize()
                job = Job(
                    source="Workable",
                    role="Senior Product Engineer",
                    company="International Product Co",
                    description="Own a TypeScript product platform.",
                    original_url="https://example.com/jobs/1",
                    company_origin=CompanyOrigin.INTERNATIONAL,
                )
                job_id, _ = ledger.upsert_job(job)
                packet = packet_for(job_id)
                ledger.upsert_application(packet, ApplicationStatus.PREPARED)
                with self.assertRaisesRegex(ValueError, "verified submission evidence"):
                    ledger.upsert_application(packet, ApplicationStatus.APPLIED)
                ledger.upsert_application(
                    packet,
                    ApplicationStatus.APPLIED,
                    submission_evidence=SubmissionEvidence(
                        "ATS_SUCCESS_STATE", "Employer received application", "confirmation-1",
                        "2026-08-14T00:00:00+08:00",
                    ),
                )
                application = ledger.connection.execute(
                    "SELECT * FROM applications WHERE application_id = ?", (job_id,)
                ).fetchone()
                self.assertEqual("APPLIED", application["status"])
                self.assertEqual("2026-08-13T16:00:00+00:00", application["date_applied"])
                self.assertEqual("workable", ledger.connection.execute("SELECT source FROM jobs").fetchone()[0])

    def test_legacy_event_aliases_are_canonical(self) -> None:
        self.assertEqual("SUBMIT_CLICKED", canonical_event_type("SUBMITTED").value)
        self.assertEqual("SUBMISSION_VERIFIED", canonical_event_type("VERIFIED_SUBMITTED").value)
        self.assertEqual("ACKNOWLEDGEMENT", canonical_event_type("ACKNOWLEDGEMENT_RECEIVED").value)

    def test_run_counts_are_derived_and_manual_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with Ledger(Path(directory) / "ledger.sqlite") as ledger:
                ledger.initialize()
                ledger.start_run("run_1", "workable", RunMode.DRY_RUN)
                ledger.record_run_outcome("run_1", "job_1", "DISCOVERED")
                with self.assertRaisesRegex(ValueError, "disagree"):
                    ledger.finish_run("run_1", {"discovered_count": 2})
                counts = ledger.finish_run("run_1")
                self.assertEqual(1, counts["discovered_count"])

    def test_active_queue_gets_review_and_expiry_dates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with Ledger(Path(directory) / "ledger.sqlite") as ledger:
                ledger.initialize()
                job = Job(
                    source="greenhouse",
                    role="Senior Engineer",
                    company="Acme",
                    description="Build products.",
                    original_url="https://example.com/jobs/2",
                    company_origin=CompanyOrigin.INTERNATIONAL,
                )
                job_id, _ = ledger.upsert_job(job)
                ledger.upsert_review_queue(
                    {
                        "queue_id": job_id, "job_id": job_id, "company": "Acme",
                        "role": "Senior Engineer", "job_url": job.original_url,
                        "queue_status": "HUMAN_SUBMIT_READY", "verdict": "STRONG APPLY",
                        "cover_letter": "Specific letter.", "next_action": "Click Submit after review.",
                    }
                )
                row = ledger.list_review_queue()[0]
                self.assertTrue(row["re_review_after"])
                self.assertTrue(row["expires_at"])

    def test_tracker_rejects_pre_submission_projection(self) -> None:
        with self.assertRaisesRegex(ValueError, "post-submission"):
            plan_sheet_upsert([], {"application_id": "a", "application_status": "PREPARED"})

    def test_media_and_human_verification_are_preflighted(self) -> None:
        result = evaluate_application_preflight(
            [{"label": "Record a video introduction", "required": True}],
            video_requirement=MediaRequirement.UNKNOWN_NOT_INSPECTED,
        )
        self.assertFalse(result.can_prepare)
        self.assertEqual("VIDEO_REQUIRED", result.queue_status)
        captcha = evaluate_application_preflight([{"label": "Human verification", "required": True}])
        self.assertIn("HUMAN_VERIFICATION_REQUIRED", captcha.blockers)

    def test_source_resolution_and_diversity_are_separate_from_fit(self) -> None:
        self.assertEqual("indeed_ph", normalize_source_key("Indeed-PH"))
        self.assertEqual("workable", resolve_source_id("Workable"))
        rotation = plan_diverse_discovery_rotation({"workable": 99})
        self.assertNotEqual("workable", rotation[0]["id"])

    def test_response_monitor_is_strictly_read_only(self) -> None:
        plan = build_read_only_gmail_plan(
            [{"application_id": "a1", "status": "APPLIED", "company": "Acme", "role": "Senior Engineer"}]
        )
        self.assertTrue(plan["read_only"])
        self.assertIn("SEND", plan["forbidden_actions"])
        self.assertEqual(1, len(plan["queries"]))

    def test_timestamps_are_utc_authoritative_with_manila_display(self) -> None:
        self.assertEqual("2026-08-13T16:00:00+00:00", normalize_utc_timestamp("2026-08-14T00:00:00+08:00"))
        self.assertTrue(manila_display("2026-08-13T16:00:00Z").startswith("2026-08-14T00:00:00"))

    def test_private_ledger_hardening_normalizes_timezone_qualified_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with Ledger(Path(directory) / "ledger.sqlite") as ledger:
                ledger.initialize()
                ledger.start_run("run_time", "Workable", RunMode.DRY_RUN)
                ledger.connection.execute(
                    "UPDATE runs SET started_at = ? WHERE run_id = ?",
                    ("2026-08-14T00:00:00+08:00", "run_time"),
                )
                ledger.connection.commit()
                result = ledger.harden_existing_data()
                self.assertEqual(1, result["timestamps"])
                self.assertEqual(
                    "2026-08-13T16:00:00+00:00",
                    ledger.get_run("run_time")["started_at"],
                )


if __name__ == "__main__":
    unittest.main()
