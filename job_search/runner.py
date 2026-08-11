from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

from .application import prepare_application_packet
from .campaign import classify_freshness
from .ledger import DEFAULT_DB, Ledger
from .models import ApplicationStatus, CompanyOrigin, FitRubric, Job, RunMode, Verdict, utc_now
from .normalization import application_id, canonicalize_url
from .policy import EmployerExclusionMatcher, evaluate_eligibility
from .scoring import build_assessment, reconcile_assessment_with_answers


DEFAULT_STATE = Path(".job-search")


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    return [str(item) for item in value]


def _job_from_dict(item: dict[str, Any], source: str) -> Job:
    known = {
        "source",
        "role",
        "company",
        "description",
        "original_url",
        "company_origin",
        "location",
        "source_posting_id",
        "actual_employer",
        "destination_company",
        "company_domain",
        "destination_domain",
        "company_origin_evidence",
        "remote_policy",
        "remote_from_ph",
        "employment_type",
        "compensation",
        "work_schedule",
        "recurring_weekend_work",
        "advertised_compensation_currency",
        "advertised_compensation_min",
        "advertised_compensation_max",
        "advertised_compensation_basis",
        "advertised_compensation_monthly_php_min",
        "advertised_compensation_monthly_php_max",
        "advertised_compensation_exchange_rate_to_php",
        "advertised_compensation_conversion_date",
        "strategically_exceptional",
        "active",
        "posted_at",
        "discovered_at",
        "posting_age_days",
        "freshness_bucket",
        "engineering_domain_eligible",
    }
    raw = {key: value for key, value in item.items() if key not in known}
    posting_age_days, freshness_bucket = classify_freshness(
        item.get("posted_at"), item.get("discovered_at", utc_now())
    )
    return Job(
        source=source,
        role=item["role"],
        company=item["company"],
        description=item["description"],
        original_url=item["original_url"],
        company_origin=CompanyOrigin(item["company_origin"]),
        location=item.get("location", ""),
        source_posting_id=item.get("source_posting_id"),
        actual_employer=item.get("actual_employer"),
        destination_company=item.get("destination_company"),
        company_domain=item.get("company_domain"),
        destination_domain=item.get("destination_domain"),
        company_origin_evidence=item.get("company_origin_evidence", ""),
        remote_policy=item.get("remote_policy", ""),
        remote_from_ph=item.get("remote_from_ph"),
        employment_type=item.get("employment_type", ""),
        compensation=item.get("compensation", ""),
        work_schedule=item.get("work_schedule", ""),
        recurring_weekend_work=item.get("recurring_weekend_work"),
        advertised_compensation_currency=item.get("advertised_compensation_currency"),
        advertised_compensation_min=item.get("advertised_compensation_min"),
        advertised_compensation_max=item.get("advertised_compensation_max"),
        advertised_compensation_basis=item.get("advertised_compensation_basis"),
        advertised_compensation_monthly_php_min=item.get(
            "advertised_compensation_monthly_php_min"
        ),
        advertised_compensation_monthly_php_max=item.get(
            "advertised_compensation_monthly_php_max"
        ),
        advertised_compensation_exchange_rate_to_php=item.get(
            "advertised_compensation_exchange_rate_to_php"
        ),
        advertised_compensation_conversion_date=item.get(
            "advertised_compensation_conversion_date"
        ),
        strategically_exceptional=bool(item.get("strategically_exceptional", False)),
        active=bool(item.get("active", True)),
        posted_at=item.get("posted_at"),
        discovered_at=item.get("discovered_at", utc_now()),
        posting_age_days=item.get("posting_age_days", posting_age_days),
        freshness_bucket=item.get("freshness_bucket", freshness_bucket.value),
        engineering_domain_eligible=item.get("engineering_domain_eligible"),
        raw=raw,
    )


def _artifact_slug(company: str, role: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", f"{company}-{role}".casefold()).strip("-")[:100]


def run_dry_run(
    input_path: Path,
    *,
    db_path: Path = DEFAULT_DB,
    state_dir: Path = DEFAULT_STATE,
) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    source = payload["source"]
    mode = RunMode(payload.get("mode", "DRY_RUN"))
    if mode != RunMode.DRY_RUN:
        raise ValueError("calibration import must run in DRY_RUN")

    run_id = payload.get("run_id") or f"run_{uuid.uuid4().hex[:16]}"
    run_dir = state_dir / "runs" / run_id
    artifact_dir = state_dir / "artifacts" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    artifact_dir.mkdir(parents=True, exist_ok=False)
    matcher = EmployerExclusionMatcher.load()
    counts = {
        "discovered_count": len(payload["jobs"]),
        "normalized_count": 0,
        "duplicate_count": 0,
        "reassessed_count": 0,
        "skipped_count": 0,
        "review_count": 0,
        "apply_count": 0,
        "strong_apply_count": 0,
        "prepared_count": 0,
        "submitted_count": 0,
        "eligible_count": 0,
        "assessed_count": 0,
        "held_count": 0,
        "verified_submitted_count": 0,
    }
    errors: list[str] = []
    ranked: list[dict[str, Any]] = []
    prepared: list[dict[str, Any]] = []

    with Ledger(db_path) as ledger:
        ledger.initialize()
        ledger.start_run(run_id, source, mode, payload.get("started_at"))
        for position, item in enumerate(payload["jobs"], start=1):
            try:
                job = _job_from_dict(item, source)
                eligibility = evaluate_eligibility(job, matcher)
                job_id, duplicate = ledger.upsert_job(
                    job,
                    eligibility_verdict=eligibility.verdict.value if eligibility.verdict else None,
                    reason_codes=eligibility.reason_codes,
                )
                counts["normalized_count"] += 1
                if duplicate:
                    counts["duplicate_count"] += 1
                    if not payload.get("reassess_existing", False):
                        continue
                    counts["reassessed_count"] += 1

                if eligibility.can_score:
                    counts["eligible_count"] += 1

                rubric_data = item.get("rubric")
                rubric = FitRubric(**rubric_data) if rubric_data and eligibility.can_score else None
                analysis = item.get("analysis", {})
                assessment = build_assessment(
                    job_id=job_id,
                    eligibility=eligibility,
                    rubric=rubric,
                    eligibility_confidence=int(analysis.get("eligibility_confidence", 100)),
                    application_readiness=int(analysis.get("application_readiness", 100)),
                    readiness_reason_codes=_list(analysis.get("readiness_reason_codes")),
                    real_problem=analysis.get("real_problem", ""),
                    strongest_matches=_list(analysis.get("strongest_matches")),
                    relevant_projects=_list(analysis.get("relevant_projects")),
                    relevant_technologies=_list(analysis.get("relevant_technologies")),
                    legitimate_gaps=_list(analysis.get("legitimate_gaps")),
                    dealbreakers=_list(analysis.get("dealbreakers")),
                    narrative=analysis.get("narrative", ""),
                    cv_emphasis=analysis.get("cv_emphasis", ""),
                    application_angle=analysis.get("application_angle", ""),
                    interview_risks=_list(analysis.get("interview_risks")),
                )
                counts["assessed_count"] += 1
                packet_input = item.get("application_packet")
                if packet_input and assessment.verdict != Verdict.SKIP:
                    packet = prepare_application_packet(
                        job,
                        assessment,
                        letter=packet_input.get("letter"),
                        screening_questions=packet_input.get("screening_questions", {}),
                        canonical_answers=packet_input.get("canonical_answers", {}),
                        screening_questions_verified=bool(
                            packet_input.get("screening_questions_verified", False)
                        ),
                        screening_questions_source=packet_input.get(
                            "screening_questions_source", ""
                        ),
                        matcher=matcher,
                    )
                    reconcile_assessment_with_answers(
                        assessment,
                        packet,
                        proposed_eligibility_confidence=int(
                            analysis.get("eligibility_confidence", 100)
                        ),
                        proposed_application_readiness=int(
                            analysis.get("application_readiness", 100)
                        ),
                    )
                    ledger.save_draft(packet)
                    ledger.upsert_application(
                        packet,
                        ApplicationStatus.PREPARED,
                        application_method=packet_input.get("application_method", "Indeed"),
                    )
                    artifact_path = artifact_dir / f"{_artifact_slug(job.employer, job.role)}.json"
                    artifact_path.write_text(
                        json.dumps(packet.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
                    )
                    counts["prepared_count"] += 1
                    prepared.append({"job_id": job_id, "artifact": str(artifact_path)})

                ledger.save_assessment(assessment)

                count_key = {
                    Verdict.SKIP: "skipped_count",
                    Verdict.REVIEW: "review_count",
                    Verdict.APPLY: "apply_count",
                    Verdict.STRONG_APPLY: "strong_apply_count",
                }[assessment.verdict]
                counts[count_key] += 1
                result = {
                    "rank": position,
                    "job_id": job_id,
                    "company": job.employer,
                    "role": job.role,
                    "url": canonicalize_url(job.original_url),
                    "fit_score": assessment.fit_score,
                    "base_fit_score": assessment.base_fit_score,
                    "technical_fit_score": assessment.technical_fit_score,
                    "career_direction_fit_score": assessment.career_direction_fit_score,
                    "eligibility_confidence": assessment.eligibility_confidence,
                    "application_readiness": assessment.application_readiness,
                    "verdict": assessment.verdict.value,
                    "reason_codes": assessment.reason_codes,
                    "readiness_reason_codes": assessment.readiness_reason_codes,
                    "why_it_fits": assessment.real_problem,
                    "main_gap": assessment.legitimate_gaps[0] if assessment.legitimate_gaps else "",
                    "application_angle": assessment.application_angle,
                }
                ranked.append(result)

            except Exception as exc:  # Keep one bad listing from destroying calibration evidence.
                errors.append(f"job {position}: {type(exc).__name__}: {exc}")

        ranked.sort(key=lambda item: item["fit_score"] if item["fit_score"] is not None else -1, reverse=True)
        for index, item in enumerate(ranked, start=1):
            item["rank"] = index
        summary = {
            "run_id": run_id,
            "source": source,
            "mode": mode.value,
            "counts": counts,
            "ranked_jobs": ranked,
            "prepared_applications": prepared,
            "errors": errors,
            "external_writes": list(payload.get("external_writes", [])),
            "real_applications_submitted": 0,
        }
        ledger.finish_run(run_id, counts, errors, summary["external_writes"])

    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    return summary
