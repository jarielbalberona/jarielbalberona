from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
import re
from typing import Any, Mapping, Sequence

from .normalization import canonicalize_url


HEADERS = (
    "Application ID",
    "Date Discovered",
    "Date Applied",
    "Company",
    "Role",
    "Source",
    "Job URL",
    "Canonical Job URL",
    "Location",
    "Remote Policy",
    "Employment Type",
    "Salary / Compensation",
    "Fit Score",
    "Verdict",
    "Application Status",
    "Application Method",
    "CV Version",
    "Application Letter",
    "Key Matches",
    "Gaps",
    "Recruiter / Contact",
    "Last Response At",
    "Response Type",
    "Next Action",
    "Follow-up Date",
    "Notes",
)

FIELD_MAP = {
    "Application ID": "application_id",
    "Date Discovered": "date_discovered",
    "Date Applied": "date_applied",
    "Company": "company",
    "Role": "role",
    "Source": "source",
    "Job URL": "job_url",
    "Canonical Job URL": "canonical_job_url",
    "Location": "location",
    "Remote Policy": "remote_policy",
    "Employment Type": "employment_type",
    "Salary / Compensation": "compensation",
    "Fit Score": "fit_score",
    "Verdict": "verdict",
    "Application Status": "application_status",
    "Application Method": "application_method",
    "CV Version": "cv_version",
    "Application Letter": "application_letter",
    "Key Matches": "key_matches",
    "Gaps": "gaps",
    "Recruiter / Contact": "recruiter_contact",
    "Last Response At": "last_response_at",
    "Response Type": "response_type",
    "Next Action": "next_action",
    "Follow-up Date": "follow_up_date",
    "Notes": "notes",
}

MANUAL_PRESERVE_FIELDS = frozenset(
    {"Application Status", "Next Action", "Follow-up Date", "Notes"}
)

REVIEW_QUEUE_HEADERS = (
    "Queue ID",
    "Date Discovered",
    "Last Reviewed",
    "Company",
    "Role",
    "Source",
    "ATS",
    "Job URL",
    "Posted Date",
    "Job Age",
    "Fit Score",
    "Verdict",
    "Readiness",
    "Queue Status",
    "Hold / Review Reason",
    "Next Action",
    "Compensation",
    "Key Matches",
    "Material Gaps",
    "Prepared Screening Answers",
    "Cover Letter",
    "CV Version",
    "Media Requirement",
    "Source / ATS Policy",
    "Re-review After",
    "Notes",
)

REVIEW_QUEUE_FIELD_MAP = {
    "Queue ID": "queue_id",
    "Date Discovered": "date_discovered",
    "Last Reviewed": "last_reviewed",
    "Company": "company",
    "Role": "role",
    "Source": "source",
    "ATS": "ats",
    "Job URL": "job_url",
    "Posted Date": "posted_date",
    "Job Age": "job_age",
    "Fit Score": "fit_score",
    "Verdict": "verdict",
    "Readiness": "readiness",
    "Queue Status": "queue_status",
    "Hold / Review Reason": "hold_review_reason",
    "Next Action": "next_action",
    "Compensation": "compensation",
    "Key Matches": "key_matches",
    "Material Gaps": "material_gaps",
    "Prepared Screening Answers": "prepared_screening_answers",
    "Cover Letter": "cover_letter",
    "CV Version": "cv_version",
    "Media Requirement": "media_requirement",
    "Source / ATS Policy": "source_ats_policy",
    "Re-review After": "re_review_after",
    "Notes": "notes",
}

REVIEW_QUEUE_STATUSES = (
    "PREPARED",
    "HELD",
    "REVIEW",
    "READY TO APPLY",
    "CLOSED",
)

REVIEW_QUEUE_MANUAL_PRESERVE_FIELDS = frozenset(
    {"Queue Status", "Next Action", "Re-review After", "Notes"}
)


def _display(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return "; ".join(str(item) for item in value)
    if isinstance(value, Mapping):
        return json.dumps(dict(value), ensure_ascii=False, sort_keys=True)
    return value


def format_compensation_for_tracker(
    advertised: str,
    compensation_decision: Mapping[str, Any] | None,
) -> str:
    parts = [f"Advertised: {advertised.strip() or 'undisclosed'}"]
    if compensation_decision:
        currency = str(compensation_decision.get("submitted_currency", "")).strip()
        amount = compensation_decision.get("submitted_amount")
        minimum = compensation_decision.get("submitted_min")
        maximum = compensation_decision.get("submitted_max")
        basis = str(compensation_decision.get("requested_basis", "")).replace("_", " ")
        if currency and isinstance(amount, (int, float)):
            parts.append(f"Expected/submitted: {currency} {amount:,.0f} {basis}".strip())
        elif currency and isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)):
            parts.append(
                f"Expected/submitted: {currency} {minimum:,.0f}-{maximum:,.0f} {basis}".strip()
            )
    return " | ".join(parts)


def map_record_to_row(record: Mapping[str, Any]) -> list[Any]:
    return [_display(record.get(FIELD_MAP[header], "")) for header in HEADERS]


def row_to_record(row: Sequence[Any]) -> dict[str, Any]:
    values = list(row) + [""] * (len(HEADERS) - len(row))
    return {FIELD_MAP[header]: values[index] for index, header in enumerate(HEADERS)}


def map_review_queue_record_to_row(record: Mapping[str, Any]) -> list[Any]:
    return [_display(record.get(REVIEW_QUEUE_FIELD_MAP[header], "")) for header in REVIEW_QUEUE_HEADERS]


def review_queue_row_to_record(row: Sequence[Any]) -> dict[str, Any]:
    values = list(row) + [""] * (len(REVIEW_QUEUE_HEADERS) - len(row))
    return {
        REVIEW_QUEUE_FIELD_MAP[header]: values[index]
        for index, header in enumerate(REVIEW_QUEUE_HEADERS)
    }


@dataclass(frozen=True, slots=True)
class SheetUpsertPlan:
    action: str
    row_number: int | None
    values: tuple[Any, ...]
    matched_by: str | None


def _normalized_company_role(company: Any, role: Any) -> str:
    value = f"{company} {role}".casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def should_sync_review_queue(record: Mapping[str, Any]) -> bool:
    verdict = str(record.get("verdict", "")).strip().upper()
    queue_status = str(record.get("queue_status", "")).strip().upper()
    if verdict == "SKIP":
        return False
    return queue_status in REVIEW_QUEUE_STATUSES


def is_review_queue_due(record: Mapping[str, Any], *, as_of: date) -> bool:
    if str(record.get("queue_status", "")).strip().upper() == "CLOSED":
        return False
    raw = str(record.get("re_review_after", "")).strip()
    if not raw:
        return False
    return date.fromisoformat(raw[:10]) <= as_of


def close_review_queue_record(
    record: Mapping[str, Any],
    *,
    applied_at: str,
) -> dict[str, Any]:
    closed = dict(record)
    previous_notes = str(closed.get("notes", "")).strip()
    transition_note = f"Applied and moved to Applications on {applied_at}."
    closed.update(
        {
            "queue_status": "CLOSED",
            "hold_review_reason": "Resolved by verified application submission.",
            "next_action": "Monitor application lifecycle in Applications.",
            "re_review_after": "",
            "notes": f"{previous_notes} {transition_note}".strip(),
        }
    )
    return closed


def plan_review_queue_upsert(
    existing_rows: Sequence[Sequence[Any]],
    record: Mapping[str, Any],
    *,
    preserve_manual: bool = True,
    force_lifecycle: bool = False,
) -> SheetUpsertPlan:
    if not should_sync_review_queue(record):
        raise ValueError("SKIP and non-queue lifecycle records must not enter Review Queue")
    if (
        str(record.get("queue_status", "")).strip().upper() != "CLOSED"
        and not str(record.get("cover_letter", "")).strip()
    ):
        raise ValueError("worthwhile active Review Queue records require a prepared cover letter")

    target_id = str(record.get("queue_id", "")).strip()
    target_url = canonicalize_url(str(record.get("job_url", "")).strip())
    target_company_role = _normalized_company_role(
        record.get("company", ""), record.get("role", "")
    )
    match_index: int | None = None
    matched_by: str | None = None

    for index, row in enumerate(existing_rows, start=2):
        existing = review_queue_row_to_record(row)
        if target_id and str(existing["queue_id"]).strip() == target_id:
            match_index, matched_by = index, "queue_id"
            break
        existing_url = canonicalize_url(str(existing["job_url"]).strip())
        if target_url and existing_url == target_url:
            match_index, matched_by = index, "job_url"
            break
        if target_company_role and _normalized_company_role(
            existing["company"], existing["role"]
        ) == target_company_role:
            match_index, matched_by = index, "company_role"
            break

    mapped = map_review_queue_record_to_row(record)
    if match_index is None:
        return SheetUpsertPlan("append", None, tuple(mapped), None)

    existing_row = list(existing_rows[match_index - 2]) + [""] * len(REVIEW_QUEUE_HEADERS)
    if preserve_manual and not force_lifecycle:
        for header in REVIEW_QUEUE_MANUAL_PRESERVE_FIELDS:
            column = REVIEW_QUEUE_HEADERS.index(header)
            if existing_row[column] not in (None, ""):
                mapped[column] = existing_row[column]
    return SheetUpsertPlan("update", match_index, tuple(mapped), matched_by)


def plan_sheet_upsert(
    existing_rows: Sequence[Sequence[Any]],
    record: Mapping[str, Any],
    *,
    preserve_manual: bool = True,
) -> SheetUpsertPlan:
    target_id = str(record.get("application_id", ""))
    target_url = str(record.get("canonical_job_url", ""))
    match_index: int | None = None
    matched_by: str | None = None

    for index, row in enumerate(existing_rows, start=2):
        existing = row_to_record(row)
        if target_id and str(existing["application_id"]) == target_id:
            match_index, matched_by = index, "application_id"
            break
        if target_url and str(existing["canonical_job_url"]) == target_url:
            match_index, matched_by = index, "canonical_job_url"
            break

    mapped = map_record_to_row(record)
    if match_index is None:
        return SheetUpsertPlan("append", None, tuple(mapped), None)

    existing_row = list(existing_rows[match_index - 2]) + [""] * len(HEADERS)
    if preserve_manual:
        for header in MANUAL_PRESERVE_FIELDS:
            column = HEADERS.index(header)
            if existing_row[column] not in (None, ""):
                mapped[column] = existing_row[column]
    return SheetUpsertPlan("update", match_index, tuple(mapped), matched_by)
