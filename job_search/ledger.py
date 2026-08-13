from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from .campaign import CampaignPolicy, classify_freshness
from .lifecycle import (
    ApplicationEventType,
    SubmissionEvidence,
    assert_transition,
    canonical_event_type,
    require_applied_evidence,
)
from .models import ApplicationPacket, ApplicationStatus, Assessment, Job, RunMode, utc_now
from .normalization import (
    application_id,
    canonical_job_url,
    canonicalize_url,
    content_fingerprint,
    description_hash,
    normalize_source_key,
)
from .queue import queue_dates
from .time_utils import canonical_timestamp, normalize_utc_timestamp
from .tracker import should_sync_review_queue


MEDIA_REQUIREMENT_VALUES = frozenset(
    {"REQUIRED", "OPTIONAL", "NOT_REQUIRED", "UNKNOWN_NOT_INSPECTED", "INACCESSIBLE"}
)


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
        initial = MIGRATIONS_DIR / "001_initial.sql"
        self.connection.executescript(initial.read_text(encoding="utf-8"))
        self.connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            ("001_initial", utc_now()),
        )
        applied = {
            str(row[0])
            for row in self.connection.execute("SELECT version FROM schema_migrations").fetchall()
        }
        for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = migration.stem
            if version in applied or version == "001_initial":
                continue
            self.connection.executescript(migration.read_text(encoding="utf-8"))
            self.connection.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                (version, utc_now()),
            )
        self.connection.commit()

    def start_run(
        self,
        run_id: str,
        source: str,
        mode: RunMode,
        started_at: str | None = None,
        campaign_policy: CampaignPolicy | None = None,
    ) -> None:
        if mode == RunMode.AUTONOMOUS_CAMPAIGN and campaign_policy is None:
            campaign_policy = CampaignPolicy()
        self.connection.execute(
            """
            INSERT INTO runs(
              run_id, started_at, source, mode,
              campaign_minimum_desired, campaign_normal_target, campaign_maximum
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                canonical_timestamp(started_at) or utc_now(),
                normalize_source_key(source),
                mode.value,
                campaign_policy.minimum_desired_new_submissions if campaign_policy else None,
                campaign_policy.normal_target_new_submissions if campaign_policy else None,
                campaign_policy.maximum_new_submissions if campaign_policy else None,
            ),
        )
        self.connection.commit()

    def record_run_outcome(
        self,
        run_id: str,
        job_id: str,
        outcome: str,
        payload: Mapping[str, Any] | None = None,
        occurrence_key: str = "",
    ) -> None:
        self.connection.execute(
            """
            INSERT OR IGNORE INTO run_outcomes(run_id, job_id, outcome, occurrence_key, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (run_id, job_id, outcome.strip().upper(), occurrence_key, json.dumps(dict(payload or {}), sort_keys=True), utc_now()),
        )
        self.connection.commit()

    def derive_run_counts(self, run_id: str) -> dict[str, int]:
        mapping = {
            "DISCOVERED": "discovered_count", "NORMALIZED": "normalized_count",
            "DUPLICATE": "duplicate_count", "SKIPPED": "skipped_count",
            "REVIEW": "review_count", "APPLY": "apply_count",
            "STRONG_APPLY": "strong_apply_count", "PREPARED": "prepared_count",
            "SUBMITTED": "submitted_count", "ELIGIBLE": "eligible_count",
            "ASSESSED": "assessed_count", "HELD": "held_count",
            "VERIFIED_SUBMITTED": "verified_submitted_count",
            "AUTO_SUBMITTED": "auto_submitted_count",
            "AUTO_VERIFIED_SUBMITTED": "auto_verified_submitted_count",
            "HUMAN_SUBMIT_READY": "human_submit_ready_count",
            "READY_FOR_BROWSER_PREP": "ready_for_browser_prep_count",
            "HUMAN_CLICKED": "human_clicked_count",
            "HUMAN_VERIFIED_SUBMITTED": "human_verified_submitted_count",
            "SUBMISSION_UNVERIFIED": "submission_unverified_count",
            "VIDEO_REQUIRED": "video_required_count",
        }
        result = {column: 0 for column in mapping.values()}
        for row in self.connection.execute(
            "SELECT outcome, COUNT(*) AS total FROM run_outcomes WHERE run_id = ? GROUP BY outcome",
            (run_id,),
        ):
            column = mapping.get(str(row["outcome"]))
            if column:
                result[column] = int(row["total"])
        return result

    def finish_run(
        self,
        run_id: str,
        counts: Mapping[str, int] | None = None,
        errors: list[str] | None = None,
        external_writes: list[str] | None = None,
    ) -> dict[str, int]:
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
            "eligible_count",
            "assessed_count",
            "held_count",
            "verified_submitted_count",
            "auto_submitted_count",
            "auto_verified_submitted_count",
            "human_submit_ready_count",
            "ready_for_browser_prep_count",
            "human_clicked_count",
            "human_verified_submitted_count",
            "submission_unverified_count",
            "video_required_count",
        )
        assignments = ", ".join(f"{name} = ?" for name in columns)
        derived = self.derive_run_counts(run_id)
        has_outcomes = self.connection.execute(
            "SELECT EXISTS(SELECT 1 FROM run_outcomes WHERE run_id = ?)", (run_id,)
        ).fetchone()[0]
        authoritative = derived if has_outcomes else {name: int((counts or {}).get(name, 0)) for name in columns}
        if has_outcomes and counts:
            mismatches = {
                name: (int(counts.get(name, 0)), derived[name])
                for name in columns
                if int(counts.get(name, 0)) != derived[name]
            }
            if mismatches:
                raise ValueError(f"caller-supplied run counts disagree with ledger outcomes: {mismatches}")
        values = [authoritative[name] for name in columns]
        self.connection.execute(
            f"UPDATE runs SET finished_at = ?, {assignments}, errors_json = ?, external_writes_json = ? WHERE run_id = ?",
            (utc_now(), *values, json.dumps(errors or []), json.dumps(external_writes or []), run_id),
        )
        self.connection.commit()
        return authoritative

    def _find_existing_job(self, job: Job) -> sqlite3.Row | None:
        canonical_url = canonical_job_url(job)
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
        job.source = normalize_source_key(job.source)
        canonical_url = canonical_job_url(job)
        if job.posting_age_days is None or job.freshness_bucket is None:
            age, bucket = classify_freshness(job.posted_at, job.discovered_at)
            job.posting_age_days = age
            job.freshness_bucket = bucket.value
        existing = self._find_existing_job(job)
        now = utc_now()
        if existing:
            job_id = str(existing["job_id"])
            self.connection.execute(
                "INSERT OR IGNORE INTO job_sources(source, source_posting_id, job_id, url, observed_at) VALUES (?, ?, ?, ?, ?)",
                (job.source, job.source_posting_id or "", job_id, job.original_url, now),
            )
            if str(existing["source"]) == job.source:
                self.connection.execute(
                    """
                    UPDATE jobs SET
                      original_url = ?, canonical_url = ?, company = ?, actual_employer = ?,
                      destination_company = ?, company_domain = ?, destination_domain = ?,
                      company_origin = ?, company_origin_evidence = ?, role = ?, location = ?,
                      remote_policy = ?, remote_from_ph = ?, employment_type = ?, compensation = ?,
                      work_schedule = ?, recurring_weekend_work = ?,
                      advertised_compensation_currency = ?, advertised_compensation_min = ?,
                      advertised_compensation_max = ?, advertised_compensation_basis = ?,
                      advertised_compensation_monthly_php_min = ?,
                      advertised_compensation_monthly_php_max = ?,
                      advertised_compensation_exchange_rate_to_php = ?,
                      advertised_compensation_conversion_date = ?, strategically_exceptional = ?,
                      description = ?, description_hash = ?, content_fingerprint = ?, active = ?,
                      posted_at = ?, posting_age_days = ?, freshness_bucket = ?,
                      eligibility_verdict = ?, reason_codes_json = ?, raw_json = ?,
                      updated_at = ?
                    WHERE job_id = ?
                    """,
                    (
                        job.original_url,
                        canonical_url,
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
                        job.work_schedule,
                        None
                        if job.recurring_weekend_work is None
                        else int(job.recurring_weekend_work),
                        job.advertised_compensation_currency,
                        job.advertised_compensation_min,
                        job.advertised_compensation_max,
                        job.advertised_compensation_basis,
                        job.advertised_compensation_monthly_php_min,
                        job.advertised_compensation_monthly_php_max,
                        job.advertised_compensation_exchange_rate_to_php,
                        job.advertised_compensation_conversion_date,
                        int(job.strategically_exceptional),
                        job.description,
                        description_hash(job.description),
                        content_fingerprint(job),
                        int(job.active),
                        canonical_timestamp(job.posted_at),
                        job.posting_age_days,
                        job.freshness_bucket,
                        eligibility_verdict,
                        json.dumps(list(reason_codes)),
                        json.dumps(job.raw, sort_keys=True),
                        now,
                        job_id,
                    ),
                )
            else:
                if job.destination_ats_url:
                    self.connection.execute(
                        "UPDATE jobs SET canonical_url = ?, updated_at = ? WHERE job_id = ?",
                        (canonical_url, now, job_id),
                    )
                else:
                    self.connection.execute(
                        "UPDATE jobs SET updated_at = ? WHERE job_id = ?",
                        (now, job_id),
                    )
            self.connection.commit()
            return job_id, True

        job_id = application_id(job)
        values = (
            job_id,
            job.source,
            job.source_posting_id,
            job.original_url,
            canonical_url,
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
            job.work_schedule,
            None if job.recurring_weekend_work is None else int(job.recurring_weekend_work),
            job.advertised_compensation_currency,
            job.advertised_compensation_min,
            job.advertised_compensation_max,
            job.advertised_compensation_basis,
            job.advertised_compensation_monthly_php_min,
            job.advertised_compensation_monthly_php_max,
            job.advertised_compensation_exchange_rate_to_php,
            job.advertised_compensation_conversion_date,
            int(job.strategically_exceptional),
            job.description,
            description_hash(job.description),
            content_fingerprint(job),
            int(job.active),
            canonical_timestamp(job.posted_at),
            canonical_timestamp(job.discovered_at),
            job.posting_age_days,
            job.freshness_bucket,
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
              employment_type, compensation, work_schedule, recurring_weekend_work,
              advertised_compensation_currency, advertised_compensation_min,
              advertised_compensation_max, advertised_compensation_basis,
              advertised_compensation_monthly_php_min,
              advertised_compensation_monthly_php_max,
              advertised_compensation_exchange_rate_to_php,
              advertised_compensation_conversion_date, strategically_exceptional,
              description, description_hash, content_fingerprint,
              active, posted_at, discovered_at, posting_age_days, freshness_bucket,
              eligibility_verdict, reason_codes_json, raw_json,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                canonical_timestamp(assessment.created_at),
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
                canonical_timestamp(packet.prepared_at),
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
        submission_evidence: SubmissionEvidence | Mapping[str, Any] | None = None,
    ) -> None:
        current_row = self.connection.execute(
            "SELECT status FROM applications WHERE application_id = ?", (packet.application_id,)
        ).fetchone()
        current = ApplicationStatus(current_row["status"]) if current_row else None
        assert_transition(current, status)
        evidence = require_applied_evidence(status, submission_evidence)
        now = utc_now()
        self.connection.execute(
            """
            INSERT INTO applications(
              application_id, job_id, status, application_method, cv_version,
              date_discovered, date_applied, submission_evidence_json,
              answer_metadata_json, compensation_decision_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(application_id) DO UPDATE SET
              status = excluded.status,
              application_method = excluded.application_method,
              cv_version = excluded.cv_version,
              date_applied = COALESCE(applications.date_applied, excluded.date_applied),
              submission_evidence_json = COALESCE(excluded.submission_evidence_json, applications.submission_evidence_json),
              answer_metadata_json = excluded.answer_metadata_json,
              compensation_decision_json = excluded.compensation_decision_json,
              updated_at = excluded.updated_at
            """,
            (
                packet.application_id,
                packet.job_id,
                status.value,
                application_method,
                packet.cv_version,
                packet.prepared_at[:10],
                (str(evidence.get("occurred_at", now)) if evidence else None),
                json.dumps(evidence, sort_keys=True) if evidence else None,
                json.dumps(packet.answer_metadata, sort_keys=True),
                json.dumps(packet.compensation_decision, sort_keys=True)
                if packet.compensation_decision
                else None,
                now,
                now,
            ),
        )
        if status == ApplicationStatus.APPLIED:
            self.connection.execute(
                """
                UPDATE review_queue SET
                  application_id = ?, queue_status = 'CLOSED',
                  hold_review_reason = 'Resolved by verified application submission.',
                  next_action = 'Monitor application lifecycle in Applications.',
                  re_review_after = NULL, updated_at = ?
                WHERE job_id = ?
                """,
                (packet.application_id, now, packet.job_id),
            )
            self.record_application_event(
                application_id_value=packet.application_id,
                event_type=ApplicationEventType.SUBMISSION_VERIFIED,
                external_key=str(evidence["external_key"]),
                payload=evidence,
                created_at=str(evidence.get("occurred_at", now)),
                commit=False,
            )
        self.connection.commit()

    def record_application_event(
        self,
        *,
        application_id_value: str,
        event_type: str | ApplicationEventType,
        external_key: str,
        payload: Mapping[str, Any] | None = None,
        created_at: str | None = None,
        commit: bool = True,
    ) -> bool:
        event_type = canonical_event_type(event_type).value
        seed = f"{application_id_value}|{event_type}|{external_key}"
        event_id = "event_" + hashlib.blake2b(seed.encode(), digest_size=10).hexdigest()
        cursor = self.connection.execute(
            """
            INSERT OR IGNORE INTO application_events(
              event_id, application_id, event_type, external_key, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                application_id_value,
                event_type,
                external_key,
                json.dumps(dict(payload or {}), sort_keys=True),
                canonical_timestamp(created_at) or utc_now(),
            ),
        )
        if commit:
            self.connection.commit()
        return cursor.rowcount == 1

    def upsert_review_queue(self, record: Mapping[str, Any]) -> None:
        if not should_sync_review_queue(record):
            raise ValueError("SKIP and non-queue lifecycle records must not enter Review Queue")
        required = (
            "queue_id",
            "job_id",
            "company",
            "role",
            "job_url",
            "queue_status",
        )
        missing = [key for key in required if not str(record.get(key, "")).strip()]
        if missing:
            raise ValueError(f"missing review queue fields: {', '.join(missing)}")
        if (
            str(record["queue_status"]).strip().upper() != "CLOSED"
            and not str(record.get("cover_letter", "")).strip()
        ):
            raise ValueError("worthwhile active Review Queue records require a prepared cover letter")
        now = utc_now()
        queue_status = str(record["queue_status"]).strip().upper()
        default_review, default_expiry = queue_dates(queue_status)
        re_review_after = record.get("re_review_after") or default_review
        expires_at = record.get("expires_at") or default_expiry
        if queue_status != "CLOSED" and not str(record.get("next_action", "")).strip():
            raise ValueError("active Review Queue records require a concrete next action")
        self.connection.execute(
            """
            INSERT INTO review_queue(
              queue_id, job_id, application_id, source_posting_id, description_hash,
              date_discovered, last_reviewed, company, role, source, ats, job_url,
              posted_date, job_age, fit_score, verdict, readiness, queue_status,
              hold_review_reason, next_action, compensation, key_matches,
              material_gaps, prepared_screening_answers, cover_letter, cv_version,
              media_requirement, source_ats_policy, re_review_after, expires_at,
              last_verified_at, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(queue_id) DO UPDATE SET
              job_id = excluded.job_id,
              application_id = COALESCE(excluded.application_id, review_queue.application_id),
              source_posting_id = excluded.source_posting_id,
              description_hash = excluded.description_hash,
              date_discovered = excluded.date_discovered,
              last_reviewed = excluded.last_reviewed,
              company = excluded.company,
              role = excluded.role,
              source = excluded.source,
              ats = excluded.ats,
              job_url = excluded.job_url,
              posted_date = excluded.posted_date,
              job_age = excluded.job_age,
              fit_score = excluded.fit_score,
              verdict = excluded.verdict,
              readiness = excluded.readiness,
              queue_status = excluded.queue_status,
              hold_review_reason = excluded.hold_review_reason,
              next_action = excluded.next_action,
              compensation = excluded.compensation,
              key_matches = excluded.key_matches,
              material_gaps = excluded.material_gaps,
              prepared_screening_answers = excluded.prepared_screening_answers,
              cover_letter = excluded.cover_letter,
              cv_version = excluded.cv_version,
              media_requirement = excluded.media_requirement,
              source_ats_policy = excluded.source_ats_policy,
              re_review_after = excluded.re_review_after,
              expires_at = excluded.expires_at,
              last_verified_at = excluded.last_verified_at,
              notes = excluded.notes,
              updated_at = excluded.updated_at
            """,
            (
                record["queue_id"],
                record["job_id"],
                record.get("application_id"),
                record.get("source_posting_id", ""),
                record.get("description_hash", ""),
                record.get("date_discovered", ""),
                record.get("last_reviewed", ""),
                record["company"],
                record["role"],
                record.get("source", ""),
                record.get("ats", ""),
                canonicalize_url(str(record["job_url"])),
                record.get("posted_date"),
                record.get("job_age"),
                record.get("fit_score"),
                record.get("verdict", ""),
                record.get("readiness"),
                record["queue_status"],
                record.get("hold_review_reason", ""),
                record.get("next_action", ""),
                record.get("compensation", ""),
                json.dumps(record.get("key_matches", [])),
                json.dumps(record.get("material_gaps", [])),
                json.dumps(record.get("prepared_screening_answers", {}), sort_keys=True),
                record.get("cover_letter", ""),
                record.get("cv_version", ""),
                record.get("media_requirement", ""),
                record.get("source_ats_policy", ""),
                re_review_after,
                expires_at,
                record.get("last_verified_at") or record.get("last_reviewed") or now,
                record.get("notes", ""),
                now,
                now,
            ),
        )
        self.connection.commit()

    def list_review_queue(
        self,
        *,
        include_closed: bool = True,
        due_on_or_before: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        if not include_closed:
            clauses.append("queue_status != 'CLOSED'")
        if due_on_or_before:
            clauses.append("re_review_after IS NOT NULL AND date(re_review_after) <= date(?)")
            values.append(due_on_or_before[:10])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.connection.execute(
            f"SELECT * FROM review_queue {where} ORDER BY COALESCE(re_review_after, '9999-12-31'), fit_score DESC, queue_id",
            values,
        ).fetchall()
        return [dict(row) for row in rows]

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
                canonical_timestamp(received_at),
                json.dumps(dict(metadata), sort_keys=True),
                utc_now(),
            ),
        )
        self.connection.commit()
        return cursor.rowcount == 1

    def upsert_application_media_requirement(
        self,
        *,
        job_id: str,
        video_requirement: str,
        photo_requirement: str,
        application_url: str = "",
        ats: str = "",
        video_prompt: str = "",
        video_duration: str = "",
        video_method: str = "",
        evidence: Mapping[str, Any] | None = None,
        inspected_at: str | None = None,
    ) -> None:
        if video_requirement not in MEDIA_REQUIREMENT_VALUES:
            raise ValueError("unsupported video requirement classification")
        if photo_requirement not in MEDIA_REQUIREMENT_VALUES:
            raise ValueError("unsupported photo requirement classification")
        now = utc_now()
        self.connection.execute(
            """
            INSERT INTO application_media_requirements(
              job_id, application_url, ats, video_requirement, photo_requirement,
              video_prompt, video_duration, video_method, evidence_json, inspected_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
              application_url = excluded.application_url,
              ats = excluded.ats,
              video_requirement = excluded.video_requirement,
              photo_requirement = excluded.photo_requirement,
              video_prompt = excluded.video_prompt,
              video_duration = excluded.video_duration,
              video_method = excluded.video_method,
              evidence_json = excluded.evidence_json,
              inspected_at = excluded.inspected_at,
              updated_at = excluded.updated_at
            """,
            (
                job_id,
                application_url,
                ats,
                video_requirement,
                photo_requirement,
                video_prompt,
                video_duration,
                video_method,
                json.dumps(dict(evidence or {}), sort_keys=True),
                canonical_timestamp(inspected_at),
                now,
            ),
        )
        self.connection.commit()

    def list_application_media_requirements(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT m.*, j.company, j.role, j.source, a.status AS application_status
            FROM application_media_requirements m
            JOIN jobs j ON j.job_id = m.job_id
            LEFT JOIN applications a ON a.job_id = m.job_id
            ORDER BY j.created_at, j.job_id
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def harden_existing_data(self) -> dict[str, int]:
        """Normalize legacy vocabulary and backfill queue control dates safely."""
        result = {"sources": 0, "events": 0, "queue_dates": 0, "timestamps": 0}
        for row in self.connection.execute("SELECT rowid, source FROM job_sources").fetchall():
            canonical = normalize_source_key(str(row["source"]))
            if canonical == row["source"]:
                continue
            original = self.connection.execute(
                "SELECT * FROM job_sources WHERE rowid = ?", (row["rowid"],)
            ).fetchone()
            self.connection.execute(
                "INSERT OR IGNORE INTO job_sources(source, source_posting_id, job_id, url, observed_at) VALUES (?, ?, ?, ?, ?)",
                (canonical, original["source_posting_id"], original["job_id"], original["url"], original["observed_at"]),
            )
            self.connection.execute("DELETE FROM job_sources WHERE rowid = ?", (row["rowid"],))
            result["sources"] += 1
        for row in self.connection.execute("SELECT job_id, source, source_posting_id FROM jobs").fetchall():
            canonical = normalize_source_key(str(row["source"]))
            if canonical == row["source"]:
                continue
            collision = self.connection.execute(
                "SELECT 1 FROM jobs WHERE source = ? AND source_posting_id = ? AND job_id != ?",
                (canonical, row["source_posting_id"], row["job_id"]),
            ).fetchone()
            if not collision:
                self.connection.execute("UPDATE jobs SET source = ? WHERE job_id = ?", (canonical, row["job_id"]))
                result["sources"] += 1

        for row in self.connection.execute("SELECT * FROM application_events").fetchall():
            canonical = canonical_event_type(str(row["event_type"])).value
            if canonical == row["event_type"]:
                continue
            self.record_application_event(
                application_id_value=str(row["application_id"]),
                event_type=canonical,
                external_key=str(row["external_key"] or ""),
                payload=json.loads(str(row["payload_json"] or "{}")),
                created_at=str(row["created_at"]),
                commit=False,
            )
            self.connection.execute("DELETE FROM application_events WHERE event_id = ?", (row["event_id"],))
            result["events"] += 1

        for row in self.connection.execute(
            "SELECT queue_id, queue_status, re_review_after, expires_at FROM review_queue WHERE queue_status != 'CLOSED'"
        ).fetchall():
            review, expiry = queue_dates(str(row["queue_status"]))
            if row["re_review_after"] and row["expires_at"]:
                continue
            self.connection.execute(
                "UPDATE review_queue SET re_review_after = COALESCE(re_review_after, ?), expires_at = COALESCE(expires_at, ?), updated_at = ? WHERE queue_id = ?",
                (review, expiry, utc_now(), row["queue_id"]),
            )
            result["queue_dates"] += 1

        timestamp_columns = {
            "runs": ("started_at", "finished_at"),
            "jobs": ("posted_at", "discovered_at", "created_at", "updated_at"),
            "assessments": ("created_at",),
            "application_drafts": ("created_at",),
            "applications": ("date_applied", "last_response_at", "created_at", "updated_at"),
            "application_events": ("created_at",),
            "email_events": ("received_at", "created_at"),
            "application_media_requirements": ("inspected_at", "updated_at"),
            "review_queue": ("last_verified_at", "created_at", "updated_at"),
        }
        for table, columns in timestamp_columns.items():
            primary_key = {
                "runs": "run_id", "jobs": "job_id", "assessments": "assessment_id",
                "application_drafts": "draft_id", "applications": "application_id",
                "application_events": "event_id", "email_events": "message_id",
                "application_media_requirements": "job_id", "review_queue": "queue_id",
            }[table]
            selection = ", ".join((primary_key, *columns))
            for row in self.connection.execute(f"SELECT {selection} FROM {table}").fetchall():
                updates: dict[str, str] = {}
                for column in columns:
                    raw = str(row[column] or "").strip()
                    if "T" not in raw or not raw:
                        continue
                    try:
                        canonical = normalize_utc_timestamp(raw)
                    except ValueError:
                        continue
                    if canonical != raw:
                        updates[column] = canonical
                if updates:
                    assignments = ", ".join(f"{column} = ?" for column in updates)
                    self.connection.execute(
                        f"UPDATE {table} SET {assignments} WHERE {primary_key} = ?",
                        (*updates.values(), row[primary_key]),
                    )
                    result["timestamps"] += len(updates)
        self.connection.commit()
        return result

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
            "application_media_requirements",
            "review_queue",
            "run_outcomes",
        }:
            raise ValueError("unsupported table")
        return int(self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        return dict(row) if row else None
