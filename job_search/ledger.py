from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from .models import ApplicationPacket, ApplicationStatus, Assessment, Job, RunMode, utc_now
from .normalization import application_id, canonicalize_url, content_fingerprint, description_hash


DEFAULT_DB = Path(".job-search/job-search.sqlite")
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


class Ledger:
    def __init__(self, path: Path = DEFAULT_DB):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "Ledger":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def initialize(self) -> None:
        migration = MIGRATIONS_DIR / "001_initial.sql"
        self.connection.executescript(migration.read_text(encoding="utf-8"))
        self.connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            ("001_initial", utc_now()),
        )
        self.connection.commit()

    def start_run(self, run_id: str, source: str, mode: RunMode, started_at: str | None = None) -> None:
        self.connection.execute(
            "INSERT INTO runs(run_id, started_at, source, mode) VALUES (?, ?, ?, ?)",
            (run_id, started_at or utc_now(), source, mode.value),
        )
        self.connection.commit()

    def finish_run(self, run_id: str, counts: Mapping[str, int], errors: list[str], external_writes: list[str]) -> None:
        columns = (
            "discovered_count",
            "normalized_count",
            "duplicate_count",
            "skipped_count",
            "review_count",
            "apply_count",
            "strong_apply_count",
            "prepared_count",
            "submitted_count",
        )
        assignments = ", ".join(f"{name} = ?" for name in columns)
        values = [int(counts.get(name, 0)) for name in columns]
        self.connection.execute(
            f"UPDATE runs SET finished_at = ?, {assignments}, errors_json = ?, external_writes_json = ? WHERE run_id = ?",
            (utc_now(), *values, json.dumps(errors), json.dumps(external_writes), run_id),
        )
        self.connection.commit()

    def _find_existing_job(self, job: Job) -> sqlite3.Row | None:
        canonical_url = canonicalize_url(job.original_url)
        fingerprint = content_fingerprint(job)
        if job.source_posting_id:
            found = self.connection.execute(
                "SELECT * FROM jobs WHERE source = ? AND source_posting_id = ?",
                (job.source, job.source_posting_id),
            ).fetchone()
            if found:
                return found
        return self.connection.execute(
            "SELECT * FROM jobs WHERE canonical_url = ? OR content_fingerprint = ? LIMIT 1",
            (canonical_url, fingerprint),
        ).fetchone()

    def upsert_job(
        self,
        job: Job,
        *,
        eligibility_verdict: str | None = None,
        reason_codes: list[str] | tuple[str, ...] = (),
    ) -> tuple[str, bool]:
        existing = self._find_existing_job(job)
        now = utc_now()
        if existing:
            job_id = str(existing["job_id"])
            self.connection.execute(
                "INSERT OR IGNORE INTO job_sources(source, source_posting_id, job_id, url, observed_at) VALUES (?, ?, ?, ?, ?)",
                (job.source, job.source_posting_id or "", job_id, job.original_url, now),
            )
            self.connection.execute("UPDATE jobs SET updated_at = ? WHERE job_id = ?", (now, job_id))
            self.connection.commit()
            return job_id, True

        job_id = application_id(job)
        values = (
            job_id,
            job.source,
            job.source_posting_id,
            job.original_url,
            canonicalize_url(job.original_url),
            job.company,
            job.actual_employer,
            job.destination_company,
            job.company_domain,
            job.destination_domain,
            job.company_origin.value,
            job.company_origin_evidence,
            job.role,
            job.location,
            job.remote_policy,
            None if job.remote_from_ph is None else int(job.remote_from_ph),
            job.employment_type,
            job.compensation,
            job.description,
            description_hash(job.description),
            content_fingerprint(job),
            int(job.active),
            job.posted_at,
            job.discovered_at,
            eligibility_verdict,
            json.dumps(list(reason_codes)),
            json.dumps(job.raw, sort_keys=True),
            now,
            now,
        )
        self.connection.execute(
            """
            INSERT INTO jobs(
              job_id, source, source_posting_id, original_url, canonical_url,
              company, actual_employer, destination_company, company_domain, destination_domain,
              company_origin, company_origin_evidence, role, location, remote_policy, remote_from_ph,
              employment_type, compensation, description, description_hash, content_fingerprint,
              active, posted_at, discovered_at, eligibility_verdict, reason_codes_json, raw_json,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        self.connection.execute(
            "INSERT OR IGNORE INTO job_sources(source, source_posting_id, job_id, url, observed_at) VALUES (?, ?, ?, ?, ?)",
            (job.source, job.source_posting_id or "", job_id, job.original_url, now),
        )
        self.connection.commit()
        return job_id, False

    def save_assessment(self, assessment: Assessment) -> str:
        seed = f"{assessment.job_id}|{assessment.created_at}|{assessment.verdict.value}"
        assessment_id = "assessment_" + hashlib.blake2b(seed.encode(), digest_size=10).hexdigest()
        self.connection.execute(
            """
            INSERT INTO assessments(
              assessment_id, job_id, fit_score, verdict, reason_codes_json,
              rubric_json, assessment_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assessment_id,
                assessment.job_id,
                assessment.fit_score,
                assessment.verdict.value,
                json.dumps(assessment.reason_codes),
                json.dumps(assessment.rubric.to_dict()) if assessment.rubric else None,
                json.dumps(assessment.to_dict(), sort_keys=True),
                assessment.created_at,
            ),
        )
        self.connection.commit()
        return assessment_id

    def save_draft(self, packet: ApplicationPacket) -> str:
        version = int(
            self.connection.execute(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM application_drafts WHERE job_id = ?",
                (packet.job_id,),
            ).fetchone()[0]
        )
        draft_id = f"draft_{packet.job_id}_{version}"
        self.connection.execute(
            """
            INSERT INTO application_drafts(draft_id, job_id, version, narrative, letter, packet_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                draft_id,
                packet.job_id,
                version,
                packet.narrative,
                packet.letter,
                json.dumps(packet.to_dict(), sort_keys=True),
                packet.prepared_at,
            ),
        )
        self.connection.commit()
        return draft_id

    def upsert_application(
        self,
        packet: ApplicationPacket,
        status: ApplicationStatus,
        *,
        application_method: str = "",
    ) -> None:
        now = utc_now()
        self.connection.execute(
            """
            INSERT INTO applications(
              application_id, job_id, status, application_method, cv_version,
              date_discovered, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(application_id) DO UPDATE SET
              application_method = excluded.application_method,
              cv_version = excluded.cv_version,
              updated_at = excluded.updated_at
            """,
            (
                packet.application_id,
                packet.job_id,
                status.value,
                application_method,
                packet.cv_version,
                packet.prepared_at[:10],
                now,
                now,
            ),
        )
        self.connection.commit()

    def record_email_event(
        self,
        *,
        message_id: str,
        application_id_value: str | None,
        response_type: str,
        confidence: float,
        ambiguous: bool,
        candidate_ids: list[str],
        received_at: str,
        metadata: Mapping[str, Any],
    ) -> bool:
        cursor = self.connection.execute(
            """
            INSERT OR IGNORE INTO email_events(
              message_id, application_id, response_type, confidence, ambiguous,
              candidate_application_ids_json, received_at, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                application_id_value,
                response_type,
                confidence,
                int(ambiguous),
                json.dumps(candidate_ids),
                received_at,
                json.dumps(dict(metadata), sort_keys=True),
                utc_now(),
            ),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def table_count(self, table: str) -> int:
        if table not in {
            "runs",
            "jobs",
            "job_sources",
            "assessments",
            "application_drafts",
            "applications",
            "application_events",
            "email_events",
        }:
            raise ValueError("unsupported table")
        return int(self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        return dict(row) if row else None
